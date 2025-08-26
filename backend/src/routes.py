import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from fastapi import HTTPException, Depends, Query, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from solders.pubkey import Pubkey
import asyncio

from src.config import solana_client, get_db
from src.models import Campaign, Transaction, TokenCache
from src.services import TokenService, QRCodeService, SolanaMonitor, get_monitoring_status, start_monitoring_campaign, CampaignService
from src.schema import CampaignCreate, CampaignResponse, ErrorResponse
from src.config import config
from src.logger import setup_logger



routers = APIRouter(prefix="/api")
logger = setup_logger("routes", "route.log")
# monitor = SolanaMonitor()


def get_solana_monitor(db: AsyncSession = Depends(get_db)):
    return SolanaMonitor(db=db) 

def get_campaign_service(db: AsyncSession = Depends(get_db)):
    return  CampaignService(db=db) 

@routers.post('/campaigns', response_model=CampaignResponse)
#create the campaigns from the backend, the frontend just pass the contact address to the verify endpoint 
async def create_campaign(
            campaign_data: CampaignCreate,
            get_campaign: CampaignService = Depends(get_campaign_service)):
    
    """Create a new campaign"""
    logger.info(f"Attempting to create a new campaign with data: {campaign_data}")
    try:
        campaign = await get_campaign.create(campaign_data)
        logger.info(f"Campaign created successfully: {campaign.campaign_id}")
        return campaign.model_dump()
    except HTTPException as http_exc:
        logger.warning(f"HTTPException while creating campaign: {http_exc.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating campaign: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@routers.get('/campaign-detail/{contract_address}')
async def get_campaign_detail(
    contract_address: str, 
    get_campaign: CampaignService = Depends(get_campaign_service)):
    
    """Get campaign details by contract address"""
    logger.info(f"Attempting to get campaign details for contract address: {contract_address}")
    try:
        details = await get_campaign.get_campaign_details(contract_address)
        logger.info(f"Campaign details retrieved successfully for contract address: {contract_address}")
        return details.model_dump()
        #TODO pass through pydantic
    except HTTPException as http_exc:
        logger.warning(f"HTTPException while getting campaign details for {contract_address}: {http_exc.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting campaign details for {contract_address}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
    
    
@routers.get('/escrow-transactions/{wallet_address}')
async def get_escrow_transactions(wallet_address: str, db: AsyncSession = Depends(get_db)):
    """Get transactions for an escrow address"""
    logger.info(f"Attempting to get escrow transactions for wallet address: {wallet_address}")
    try:
        # Find campaign by escrow address (async)
        stmt = select(Campaign).where(Campaign.wallet_address == wallet_address)
        result = await db.execute(stmt)
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            logger.warning(f"Campaign not found for wallet address: {wallet_address}")
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Get transactions (async)
        tx_stmt = select(Transaction).where(
            Transaction.campaign_id == campaign.campaign_id
        ).order_by(Transaction.timestamp.desc())
        tx_result = await db.execute(tx_stmt)
        transactions = tx_result.scalars().all()
        
        # Get unique contributors
        contributors = list(set(tx.from_wallet for tx in transactions if tx.from_wallet != "Unknown"))
        
        transaction_list = []
        for tx in transactions:
            transaction_list.append({
                "signature": tx.signature,
                "amount": float(tx.amount),
                "from": tx.from_wallet,
                "timestamp": tx.timestamp
            })
        
        response_data = {
            "transactionCount": len(transactions),
            "contributors": contributors,
            "transactions": transaction_list
        }
        logger.info(f"Retrieved {len(transactions)} transactions for wallet address: {wallet_address}")
        return response_data
        
    except HTTPException as http_exc:
        logger.warning(f"HTTPException while getting escrow transactions for {wallet_address}: {http_exc.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting escrow transactions for {wallet_address}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
@routers.get('/escrow-balance')
async def get_escrow_balance(wallet: str = Query(...), db: AsyncSession = Depends(get_db)):
    """Get escrow wallet balance"""
    logger.info(f"Attempting to get escrow balance for wallet: {wallet}")
    try:
        # Get balance from Solana RPC (run in thread pool)
        async def get_balance():
            try:
                pubkey = Pubkey.from_string(wallet)
                balance_response = await asyncio.get_event_loop().run_in_executor(
                    None, solana_client.get_balance, pubkey
                )
                balance_lamports = balance_response.value
                balance_sol = balance_lamports / 1e9
                current_sol_price = await SolanaMonitor.get_current_sol_price()
                balance_usd = balance_sol * current_sol_price
                logger.debug(f"Successfully fetched Solana balance for {wallet}: {balance_sol} SOL, {balance_usd} USD")
                return balance_sol, balance_usd
            except Exception as e:
                logger.error(f"Error fetching Solana balance for {wallet}: {e}", exc_info=True)
                return 0, 0
        
        balance_sol, balance_usd = await get_balance()
        
        # Get transaction count from database (async)
        stmt = select(Campaign).where(Campaign.wallet_address == wallet)
        result = await db.execute(stmt)
        campaign = result.scalar_one_or_none()
        
        transaction_count = 0
        recent_transactions = []
        
        if campaign:
            logger.debug(f"Campaign found for wallet {wallet}, fetching transactions.")
            # Get all transactions
            tx_stmt = select(Transaction).where(Transaction.campaign_id == campaign.campaign_id)
            tx_result = await db.execute(tx_stmt)
            transactions = tx_result.scalars().all()
            transaction_count = len(transactions)
            
            # Get recent transactions
            recent_stmt = select(Transaction).where(
                Transaction.campaign_id == campaign.campaign_id
            ).order_by(Transaction.timestamp.desc()).limit(5)
            recent_result = await db.execute(recent_stmt)
            recent = recent_result.scalars().all()
            
            for tx in recent:
                recent_transactions.append({
                    "signature": tx.signature,
                    "amount": float(tx.amount),
                    "from": tx.from_wallet,
                    "timestamp": tx.timestamp
                })
            logger.debug(f"Retrieved {transaction_count} total transactions and {len(recent_transactions)} recent transactions for campaign {campaign.campaign_id}")
        else:
            logger.debug(f"No campaign found for wallet: {wallet}")
        
        response_data = {
            "success": True,
            "data": {
                "address": wallet,
                "balanceSOL": balance_sol,
                "balanceUSD": balance_usd,
                "transactionCount": transaction_count,
                "recentTransactions": recent_transactions
            }
        }
        logger.info(f"Escrow balance and transaction data retrieved for wallet: {wallet}")
        return response_data
        
    except Exception as e:
        logger.error(f"Unexpected error getting escrow balance for {wallet}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@routers.get('/campaigns/{campaign_id}/qr')
async def get_campaign_qr(campaign_id: str, amount: Optional[float] = Query(None), db: AsyncSession = Depends(get_db)):
    """Generate QR code for campaign"""
    logger.info(f"Attempting to generate QR code for campaign ID: {campaign_id} with amount: {amount}")
    try:
        # Find campaign (async)
        stmt = select(Campaign).where(Campaign.campaign_id == campaign_id)
        result = await db.execute(stmt)
        campaign = result.scalar_one_or_none()
        
        if not campaign:
            logger.warning(f"Campaign not found for ID: {campaign_id}")
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Generate QR code (now async)
        qr_code_data, solana_pay_uri = await QRCodeService.generate_qr_code(
            campaign.wallet_address,
            amount
        )
        logger.info(f"QR code generated successfully for campaign ID: {campaign_id}")
        return {
            "qr_code": qr_code_data,
            "solana_pay_uri": solana_pay_uri,
            "escrow_address": campaign.wallet_address
        }
        
    except HTTPException as http_exc:
        logger.warning(f"HTTPException while generating QR code for campaign {campaign_id}: {http_exc.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error generating QR code for campaign {campaign_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
    
@routers.get('/token/{contract_address}')
async def get_token_info(contract_address: str, db: AsyncSession = Depends(get_db)):
    """Get token information"""
    logger.info(f"Attempting to get token information for contract address: {contract_address}")
    try:
        # Check cache first (async)
        stmt = select(TokenCache).where(TokenCache.contract_address == contract_address)
        result = await db.execute(stmt)
        cached_token = result.scalar_one_or_none()
        
        if cached_token and (datetime.now(timezone.utc) - cached_token.last_updated).seconds < 300:
            token_data = {
                "contract_address": cached_token.contract_address,
                "name": cached_token.name,
                "symbol": cached_token.symbol,
                "decimals": cached_token.decimals,
                "price_usd": float(cached_token.price_usd) if cached_token.price_usd else 0,
                "total_supply": str(cached_token.total_supply),
                "holders_count": cached_token.holders_count
            }
            logger.info(f"Token data for {contract_address} retrieved from cache.")
        else:
            # Fetch fresh data (now async)
            token_data = await TokenService.fetch_token_metadata(contract_address)
            if not token_data:
                logger.warning(f"Token not found for contract address: {contract_address}")
                raise HTTPException(status_code=404, detail="Token not found")
            
            # Update cache (async)
            if cached_token:
                cached_token.name = token_data["name"]
                cached_token.symbol = token_data["symbol"]
                cached_token.price_usd = Decimal(str(token_data["price_usd"]))
                cached_token.last_updated = datetime.now(timezone.utc)
                logger.info(f"Updated token cache for {contract_address}.")
            else:
                cached_token = TokenCache(
                    contract_address=contract_address,
                    name=token_data["name"],
                    symbol=token_data["symbol"],
                    decimals=token_data.get("decimals", 9),
                    price_usd=Decimal(str(token_data["price_usd"])),
                    total_supply=0,
                    holders_count=0
                )
                db.add(cached_token)
                logger.info(f"Added new token to cache: {contract_address}.")
            
            await db.commit()
        
        return {"status": "success", "data": token_data}
        
    except HTTPException as http_exc:
        logger.warning(f"HTTPException while getting token info for {contract_address}: {http_exc.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting token info for {contract_address}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
    
@routers.get('/health')
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint"""
    logger.info("Performing health check.")
    try:
        # Test database connection (async)
        await db.execute(select(1))
        logger.debug("Database connection successful.")
        
        # Test Solana RPC (run in thread pool)
        await asyncio.get_event_loop().run_in_executor(
            None, solana_client.get_slot
        )
        logger.debug("Solana RPC connection successful.")
        
        # Get monitoring status (now async)
        monitoring_status = await get_monitoring_status()
        logger.debug(f"Monitoring status retrieved: {monitoring_status}")
        
        logger.info("Health check completed successfully.")
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sol_price": monitoring_status.get("current_sol_price", 180.0),
            "campaign_status": monitoring_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=503, 
            detail={"status": "unhealthy", "error": str(e)}
        )
