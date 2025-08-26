import aiohttp
import asyncio
from fastapi import HTTPException
import requests
import qrcode
import io
import base64
import time
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from typing import Dict, Optional, List
from decimal import Decimal
import sqlalchemy as sa
from solders.pubkey import Pubkey
from celery import Celery
from celery.schedules import crontab
import uuid
from src.schema import CampaignCreate, CampaignResponse, ErrorResponse, CampaignData
from src.config import solana_client, get_db_session_sync, config, async_session
from src.models import Transaction, Campaign
from src.logger import setup_logger

logger = setup_logger("service", "service.log")

# Create a Celery app instance with the name "solana_monitor"
celery_app = Celery('solana_monitor')

# Load all configuration from src/celery_config.py
celery_app.config_from_object('src.celery_config')

# --------------------------
# Celery Beat (scheduler) configuration
# --------------------------
# Defines periodic tasks that run automatically
celery_app.conf.beat_schedule = {
    # Task 1: Update Solana price every 60 seconds
    'update-sol-price': {
        'task': 'src.services.update_sol_price',  # Task function
        'schedule': 60.0,                         # Run every 1 minute
    },
    # Task 2: Check monitored wallets every 15 seconds
    'check-all-monitored-wallets': {
        'task': 'src.services.check_all_monitored_wallets',
        'schedule': 15.0,                         # Run every 15 seconds
    },
}

# Ensure all scheduling uses UTC
celery_app.conf.timezone = 'UTC'



class CampaignService():
    def __init__(self, db:AsyncSession):
        self.db = db
    
    
    async def check_if_campaign_exist(self, campaign_id):
        campaign = await self.db.execute(
            sa.select(Campaign).where(
                sa.and_(
                campaign_id == Campaign.campaign_id,
                Campaign.status == 'active'
                )
            )
        )
        return campaign.scalar_one_or_none()
    
    async def create(self, campaign_data: CampaignCreate):
        try:
            # Generate campaign ID
            campaign_id = f"cmp_{uuid.uuid4().hex[:8]}"
            
            # Generate escrow wallet (in production, use a secure key generation method)
            wallet_address = Pubkey.from_string(config.WALLET)  # Mock escrow
            
            # Fetch token metadata (now async)
            token_metadata = await TokenService.fetch_token_metadata(campaign_data.contract_address)
            if not token_metadata:
                raise HTTPException(status_code=400, detail="Unable to fetch token metadata")
            
            campaign_exist = await self.check_if_campaign_exist(campaign_id=campaign_id)
            if campaign_exist:
                raise HTTPException(status_code=400, detail=f"token {campaign_exist.name} already exists and is active")
            # Create campaign
            campaign = Campaign(
                campaign_id=campaign_id,
                name=token_metadata['name'],
                symbol=token_metadata['symbol'],
                contract_address=campaign_data.contract_address,
                image_url=token_metadata['image_url'],
                wallet_address=str(wallet_address),
                goal_amount=Decimal(str(campaign_data.goal_amount)),
                campaign_type = campaign_data.campaign_type,
                expires_at=datetime.fromisoformat(campaign_data.expires_at.replace('Z', '+00:00')), 
                social_twitter=token_metadata["twitter_url"],
                social_website=token_metadata["website_url"],
                description=campaign_data.description,
                liquidity=str(token_metadata.get('liquidity', 0)),
                market_cap=str(token_metadata.get('market_cap', 0)),
                price_usd=str(token_metadata.get('price_usd', 0)),
                volume_24h=str(token_metadata.get('volume_24h', 0))
            )
            
            self.db.add(campaign)
            await self.db.commit()
            await self.db.refresh(campaign)
            
            # Start monitoring this wallet (now async)
            await start_monitoring_campaign(campaign_id, str(wallet_address))
            
            return CampaignResponse(
                success=True,
                campaign_id=campaign_id,
                escrow_address=str(wallet_address)
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    

    async def get_campaign_details(self, contract_address):
        """Get campaign details by contract address"""
        try:
            # Use async query
            stmt = sa.select(Campaign).where(
                Campaign.contract_address == contract_address,
                Campaign.is_active == True
            )
            result = await self.db.execute(stmt)
            campaign = result.scalar_one_or_none()
            
            if not campaign:
                raise HTTPException(status_code=404, detail="Campaign not found")
            
            # Calculate current balance from transactions (async)
            tx_stmt = sa.select(Transaction).where(Transaction.campaign_id == campaign.campaign_id)
            tx_result = await self.db.execute(tx_stmt)
            transactions = tx_result.scalars().all()
            
            current_balance_sol = sum(float(tx.amount) for tx in transactions)
            current_sol_price = await SolanaMonitor.get_current_sol_price()
            current_balance_usd = current_balance_sol * current_sol_price
            
            contributor_count = len(set(tx.from_wallet for tx in transactions))
            
            campaign_data = {
                "id": campaign.id,
                "name": campaign.name,
                "symbol": campaign.symbol,
                "contract_address": campaign.contract_address,
                "image_url": campaign.image_url,
                "wallet_address": campaign.wallet_address,
                "goal_amount": float(campaign.goal_amount),
                "status": campaign.status,
                "created_at": campaign.created_at.replace(tzinfo=timezone.utc),
                "expires_at": campaign.expires_at.replace(tzinfo=timezone.utc),
                "campaign_type": campaign.campaign_type,
                "social_twitter": campaign.social_twitter,
                "social_website": campaign.social_website,
                "description": campaign.description,
                "current_balance": current_balance_usd,
                "contributor_count": contributor_count,
                "token_launchpad": campaign.token_launchpad,
                "token_source": campaign.token_source,
                "liquidity": campaign.liquidity or "0",
                "market_cap": campaign.market_cap or "0",
                "price_usd": campaign.price_usd or "0",
                "volume_24h": campaign.volume_24h or "0"
            }
            
            return CampaignResponse(
                success=True,
                campaign = campaign_data
            )
            # return {"success": True, "campaign": campaign_data}
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"error: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    
    
class TokenService:
    @staticmethod
    async def get_sol_price() -> float:
        """Get SOL price from CoinGecko (asynchronous)"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return float(data["solana"]["usd"])
        except Exception as e:
            logger.error(f"Error getting SOL price from CoinGecko: {e}")
            return 180.0  # Fallback price
    
    @staticmethod
    async def fetch_token_metadata(contract_address: str) -> Dict:
        """Fetch token metadata from DexScreener API (asynchronous)"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://api.dexscreener.com/latest/dex/tokens/{contract_address}",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    if data.get('pairs') and len(data['pairs']) > 0:
                        pair = data['pairs'][0]
                        info = pair.get('info', {})
                        websites = info.get('websites', [])
                        socials = info.get('socials', [])

                        # Extract socials safely
                        twitter_url = next((s['url'] for s in socials if s.get('type') == 'twitter'), None)
                        telegram_url = next((s['url'] for s in socials if s.get('type') == 'telegram'), None)
                        website_url = websites[0]['url'] if websites else None
                        image_url = info.get('imageUrl')

                        return {
                            "contract_address": contract_address,
                            "name": pair['baseToken'].get('name'),
                            "symbol": pair['baseToken'].get('symbol'),
                            "decimals": 9,
                            "price_usd": float(pair.get('priceUsd', 0)),
                            "liquidity": pair.get('liquidity', {}).get('usd', 0),
                            "volume_24h": pair.get('volume', {}).get('h24', 0),
                            "market_cap": pair.get('marketCap', 0),
                            "image_url": image_url,
                            "website_url": website_url,
                            "twitter_url": twitter_url,
                            "telegram_url": telegram_url,
                            "last_updated": datetime.now(timezone.utc).isoformat()
                        }
                        
                    logger.warning(f"DexScreener did not return pairs for {contract_address}. Falling back to Solana RPC.")
                    return await TokenService._fetch_from_solana(contract_address)
                    
        except Exception as e:
            logger.error(f"Error fetching token metadata for {contract_address} from DexScreener: {e}")
            return await TokenService._fetch_from_solana(contract_address)
    
    @staticmethod
    async def _fetch_from_solana(contract_address: str) -> Dict:
        """Fallback method to fetch basic token info from Solana (asynchronous)"""
        try:
            pubkey = Pubkey.from_string(contract_address)
            # Run the blocking Solana client call in a thread pool
            account_info = await asyncio.get_event_loop().run_in_executor(
                None, solana_client.get_account_info, pubkey
            )
            
            if account_info.value:
                logger.info(f"Fetched basic token metadata for {contract_address} from Solana RPC.")
                return {
                    "contract_address": contract_address,
                    "name": f"Token {contract_address[:6]}...",
                    "symbol": "TKN",
                    "decimals": 9,
                    "price_usd": 0,
                    "liquidity": "0",
                    "volume_24h": "0",
                    "market_cap": "0",
                    "image_url": f"https://dd.dexscreener.com/ds-data/tokens/solana/{contract_address}.png",
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }
            else:
                logger.warning(f"No account info found for {contract_address} on Solana RPC.")
        except Exception as e:
            logger.error(f"Error fetching token metadata for {contract_address} from Solana RPC: {e}")
        
        return None

class QRCodeService:
    @staticmethod
    async def generate_qr_code(wallet_address: str, amount: float = None) -> str:
        """Generate QR code for Solana Pay (asynchronous)"""
        def _generate_qr():
            # Solana Pay URI format
            if amount:
                uri = f"solana:{wallet_address}?amount={amount}"
            else:
                uri = f"solana:{wallet_address}"
            
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(uri)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_base64}", uri
        
        # Run QR code generation in thread pool to avoid blocking
        return await asyncio.get_event_loop().run_in_executor(None, _generate_qr)

class SolanaMonitor:
    def __init__(self):
        self.sol_price = 180.0
    """Simple monitoring class that manages active campaigns"""
    
    @staticmethod
    async def get_active_campaigns() -> List[Dict]:
            """Get all active campaigns that need wallet monitoring (asynchronous)"""
            try:
                async with async_session() as db:  # async session
                    print(f"DB URL: {db.bind.url}")
                    
                    stmt = sa.select(Campaign).where(
                        Campaign.status == 'active',
                        Campaign.wallet_address.isnot(None)
                    )
                    
                    result = await db.execute(stmt)
                    campaigns = result.scalars().all()
                    
                    print(f"DEBUG campaigns count: {len(campaigns)}")
                    for c in campaigns:
                        print(f"DEBUG -> id={c.id}, campaign_id={c.campaign_id}, "
                            f"status={c.status}, wallet={c.wallet_address}")
                    
                    return [
                        {
                            'campaign_id': c.campaign_id,  # use campaign_id string
                            'wallet_address': c.wallet_address,
                            'description': c.description,
                        }
                        for c in campaigns
                    ]
            except Exception as e:
                logger.error(f"Error getting active campaigns: {e}")
                return []
      
    @staticmethod
    async def get_current_sol_price() -> float:
        """Get current SOL price from database or default (asynchronous)"""
        try:
            # You might store this in a settings table or cache
            # For now, we'll use a simple approach
            price = await TokenService.get_sol_price()
            return price
        except Exception as e:
            logger.error(f"Error getting current SOL price: {e}")
            return 180.0
    
    async def set_current_sol_price(self, price: float):
        """Cache current SOL price (asynchronous)"""
        self.sol_price = price

# =============================================================================
# CELERY TASKS
# =============================================================================


"""sumary_line

By binding, you gain access to task metadata & utilities via self, for example:

self.request → info about current execution (id, retries, args, kwargs, etc).

self.retry() → lets you retry the task on error.

self.name → task name.

Example from your code:
"""

@celery_app.task(bind=True, max_retries=3)
def update_sol_price(self):
    """Celery task to update SOL price
    Task: Fetch the latest Solana (SOL) price and update the DB.
    Runs every 60s (scheduled by Celery Beat).
    Retries on failure with exponential backoff.
    """
    async def _update_price():
        try:
            new_price = await TokenService.get_sol_price()
            old_price = await SolanaMonitor.get_current_sol_price()
            
            if abs(new_price - old_price) > 0.01:  # Only log significant changes
                logger.info(f"Updated SOL price: ${old_price:.2f} → ${new_price:.2f}")
            
            monitor = SolanaMonitor()
            await monitor.set_current_sol_price(new_price)
            return {"success": True, "price": new_price}
            
        except Exception as e:
            logger.error(f"Error updating SOL price: {e}")
            # Retry with exponential backoff
            raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
    
    # Run the async function
    return asyncio.run(_update_price())


@celery_app.task(bind=True, max_retries=3)
def check_all_monitored_wallets(self):
    """Celery task to check all monitored wallets"""
    async def _check_wallets():
        try:
            active_campaigns =  await SolanaMonitor.get_active_campaigns()
            
            if not active_campaigns:
                logger.debug("No active campaigns to monitor")
                return {"success": True, "campaigns_checked": 0}
            
            results = []
            for campaign in active_campaigns:
                try:
                    # Schedule individual wallet check task
                    result = check_wallet_transactions.delay(
                        campaign['wallet_address'], 
                        campaign['campaign_id']
                    )
                    results.append({
                        'campaign_id': campaign['campaign_id'], 
                        'task_id': result.id
                    })
                except Exception as e:
                    logger.error(f"Error scheduling wallet check for campaign {campaign['campaign_id']}: {e}")
            
            logger.debug(f"Scheduled wallet checks for {len(results)} campaigns")
            return {"success": True, "campaigns_checked": len(results), "tasks": results}
            
        except Exception as e:
            logger.error(f"Error in check_all_monitored_wallets: {e}")
            raise self.retry(exc=e, countdown=30 * (2 ** self.request.retries))
    
    # Run the async function
    return asyncio.run(_check_wallets())

@celery_app.task(bind=True, max_retries=3)
def check_wallet_transactions(self, wallet_address: str, campaign_id: str):
    """Celery task to check transactions for a specific wallet"""
    async def _check_transactions():
        try:
            logger.debug(f"Checking wallet {wallet_address} for campaign {campaign_id}")
            
            pubkey = Pubkey.from_string(wallet_address)
            # Run blocking Solana client calls in thread pool
            signatures = await asyncio.get_event_loop().run_in_executor(
                None, solana_client.get_signatures_for_address, pubkey, 5
            )
            
            if not signatures.value:
                return {"success": True, "new_transactions": 0}
            
            async def _db_operations():
                async with async_session() as db:
                    new_transactions = []
                    
                    try:
                        for sig_info in signatures.value:
                            sig_str = str(sig_info.signature)
                            
                            # Check if we already processed this transaction
                            stmt = sa.select(Transaction).where(Transaction.signature == sig_str)
                            existing = await db.execute(stmt).scalar_one_or_none()
                            
                            if existing:
                                logger.debug(f"Transaction {sig_str} already processed.")
                                continue
                            
                            # Get transaction details
                            tx_detail = solana_client.get_transaction(
                                sig_info.signature,
                                encoding="jsonParsed",
                                max_supported_transaction_version=0
                            )
                            
                            if tx_detail.value and tx_detail.value.transaction:
                                transaction_data = tx_detail.value.transaction
                                
                                if transaction_data.meta and not transaction_data.meta.err:
                                    tx_info = parse_transaction(transaction_data, wallet_address)
                                    if tx_info:
                                        # Get SOL price synchronously in thread
                                        try:
                                            response = requests.get(
                                                "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd",
                                                timeout=10
                                            )
                                            response.raise_for_status()
                                            data = response.json()
                                            sol_price = float(data["solana"]["usd"])
                                        except:
                                            sol_price = 180.0
                                        
                                        transaction = Transaction(
                                            campaign_id=campaign_id,
                                            signature=sig_str,
                                            amount=Decimal(str(tx_info['amount'])),
                                            from_wallet=tx_info['from'],
                                            to_wallet=wallet_address,
                                            timestamp=sig_info.block_time or int(time.time()),
                                            amount_usd=Decimal(str(tx_info['amount'] * sol_price))
                                        )
                                        
                                        await db.add(transaction)
                                        await db.commit()
                                        
                                        new_transactions.append({
                                            'signature': sig_str,
                                            'amount': tx_info['amount'],
                                            'from': tx_info['from'],
                                            'amount_usd': float(tx_info['amount'] * sol_price)
                                        })
                                        
                                        logger.info(f"Saved new transaction: {tx_info['amount']} SOL from {tx_info['from']} for campaign {campaign_id}")
                        
                        return {
                            "success": True, 
                            "new_transactions": len(new_transactions),
                            "transactions": new_transactions
                        }
                        
                    except Exception as e:
                        logger.error(f"an error occured: {e}")
                    # finally:
                    #     db.close()
                
            # Run database operations in thread pool
            return asyncio.run(_db_operations())
            # return await asyncio.get_event_loop().run_in_executor(None, _db_operations)
                
        except Exception as e:
            logger.error(f"Error checking wallet {wallet_address}: {e}")
            # Retry with exponential backoff, but don't retry forever
            if self.request.retries < 2:
                raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
            return {"success": False, "error": str(e)}
    
    # Run the async function
    return asyncio.run(_check_transactions())
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # try:
    #     return loop.run_until_complete(_check_transactions())
    # finally:
    #     loop.close()

def parse_transaction(tx_detail, wallet_address: str) -> Optional[Dict]:
    """Parse transaction to extract SOL transfers"""
    try:
        pre_balances = tx_detail.meta.pre_balances
        post_balances = tx_detail.meta.post_balances
        account_keys = tx_detail.transaction.message.account_keys
        
        for i, (pre, post) in enumerate(zip(pre_balances, post_balances)):
            if str(account_keys[i]) == wallet_address and post > pre:
                amount_lamports = post - pre
                amount_sol = amount_lamports / 1e9
                
                # Find sender (simplified)
                sender = "Unknown"
                for j, (pre_j, post_j) in enumerate(zip(pre_balances, post_balances)):
                    if j != i and post_j < pre_j and abs((pre_j - post_j) - amount_lamports) < 5000:
                        sender = str(account_keys[j])
                        break
                
                logger.debug(f"Parsed transaction for {wallet_address}: {amount_sol} SOL from {sender}")
                return {
                    'amount': amount_sol,
                    'from': sender
                }
        
    except Exception as e:
        logger.error(f"Error parsing transaction: {e}")
    
    return None

# =============================================================================
# CONVENIENCE FUNCTIONS FOR YOUR MAIN APP
# =============================================================================

async def start_monitoring_campaign(campaign_id: str, wallet_address: str):
    """Start monitoring a campaign (called when campaign becomes active) - async"""
    logger.info(f"Started monitoring campaign {campaign_id} with wallet {wallet_address}")
    # The Celery beat scheduler will automatically pick up active campaigns
    # No need to manually start/stop tasks
    
async def stop_monitoring_campaign(campaign_id: str):
    """Stop monitoring a campaign (called when campaign ends) - async"""
    logger.info(f"Stopped monitoring campaign {campaign_id}")
    # Update campaign status in database, Celery beat will stop checking it automatically

async def get_monitoring_status() -> Dict:
    """Get current monitoring status - async"""
    logger.info("get_active_campaigns() called")
    active_campaigns =  await SolanaMonitor.get_active_campaigns()
    current_price = await SolanaMonitor.get_current_sol_price()
    
    return {
        "active_campaigns": len(active_campaigns),
        "campaigns": active_campaigns,
        "current_sol_price": current_price,
        "monitoring_active": True
    }
    
    



"""

Big Picture: How Celery Works in Your Project

Celery App → The orchestrator (like a manager).

Broker (Redis) → The “middleman” (queue) where tasks are placed.

Workers → Background processes that pick tasks from Redis and run them.

Beat → The scheduler (like cron) that kicks off tasks periodically.

In your case:

Celery Beat triggers update_sol_price every 60s and check_all_monitored_wallets every 15s.

Workers pick those tasks from the queue and run them.

check_all_monitored_wallets doesn’t do heavy work itself — it creates more tasks (check_wallet_transactions) for each wallet.

This scales well because many wallets can be checked in parallel by multiple workers.

So think of it like:

Beat = “reminder system”

Worker = “background assistants”

Redis = “task board” where tasks are posted

Your tasks = “things assistants must do (e.g., update price, check wallets, fetch txns)”

Detailed Task Flow
1. update_sol_price

Runs every 60 seconds (Celery Beat).

Fetches latest SOL price (TokenService.get_sol_price()).

Compares it with last known price (SolanaMonitor.get_current_sol_price()).

If change > $0.01 → logs update.

Stores the new price in DB (via monitor.set_current_sol_price).

Retries if it fails (with exponential backoff: 1 min → 2 min → 4 min).

👉 Purpose: Keeps your system’s idea of SOL price fresh, so all transactions can be valued in USD.

2. check_all_monitored_wallets

Runs every 15 seconds (Celery Beat).

Fetches all active campaigns from DB (SolanaMonitor.get_active_campaigns()).

For each campaign:

It does NOT check transactions itself.

Instead, it schedules a new task check_wallet_transactions.delay(wallet, campaign_id).

Returns a report: how many campaigns got scheduled.

👉 Purpose: Acts like a dispatcher: finds wallets to check, and offloads actual work to sub-tasks.
👉 Scaling benefit: If you have 1,000 wallets, you don’t block one worker — instead, you schedule 1,000 smaller tasks that multiple workers can chew through at the same time.

3. check_wallet_transactions

Runs for a single wallet.

Steps:

Fetch recent transaction signatures for that wallet from Solana (solana_client.get_signatures_for_address).

For each signature:

Check if already in DB. If yes → skip.

If new → fetch full transaction (solana_client.get_transaction).

Parse it (parse_transaction) to extract transfer amount + sender.

Fetch SOL price (via CoinGecko API).

Save transaction details into DB (Transaction table).

Log new transactions and return a summary.

Retries if Solana API/db call fails (but max 2 retries).

👉 Purpose: This is where the heavy lifting happens → it looks at raw blockchain data, parses it, and saves meaningful financial info.

4. parse_transaction

Helper function to interpret raw Solana transaction data.

Compares balances before and after to detect SOL transfers.

Figures out:

How much was transferred.

Who sent it (sender).

Returns structured transaction info (amount, from).

👉 Purpose: Converts Solana’s raw blockchain format into something human-readable + storable in DB.

How They Work Together

Every 60s → update_sol_price updates SOL/USD price.

Every 15s → check_all_monitored_wallets finds wallets that need monitoring.

It spawns multiple check_wallet_transactions tasks → each checks a single wallet’s blockchain history.

check_wallet_transactions fetches raw txns → parses → saves new ones in DB.

All tasks communicate via Redis (broker).

So:

Beat → triggers schedule

Worker → executes jobs

Redis → handles communication

DB → stores final results
"""
