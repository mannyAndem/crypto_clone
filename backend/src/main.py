import os
import uvicorn
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.config import get_db, init_db, drop_db
from src.models import Campaign
from src.services import SolanaMonitor
from src.routes import routers

# Initialize monitor
# monitor = SolanaMonitor()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up application...")
    
    # print(f"server is dropping....")
    # await drop_db()
    # print(f"server has dropping!!")
    
    print(f"server is starting....")
    await init_db()
    print(f"server has started!!")
    
    
    # Add sample campaigns if none exist
    async for db in get_db():
        try:
            # Count existing campaigns (async)
            stmt = select(func.count()).select_from(Campaign)
            result = await db.execute(stmt)
            campaign_count = result.scalar_one()
            
            if campaign_count == 0:
                # Create sample campaign matching frontend mock data
                sample_campaign = Campaign(
                    campaign_id="cmp_karen123",
                    name="Karen",
                    symbol="Karen",
                    contract_address="5LKmh8SLt4FkbddUhLHWP1ufsvdcBAovkH1Gyaw5pump",
                    campaign_type = "dex ads",
                    image_url="https://dd.dexscreener.com/ds-data/tokens/solana/5LKmh8SLt4FkbddUhLHWP1ufsvdcBAovkH1Gyaw5pump.png",
                    wallet_address="9o24Px7asSDJ1ZLyQhZd7vehm9kX4VuTeJh7VGryjXkm",
                    goal_amount=Decimal('115'),
                    expires_at=datetime.now(timezone.utc) + timedelta(hours=16),
                    social_twitter="https://x.com/i/communities/1957556044743201260",
                    social_website="https://spongebob.fandom.com/wiki/Karen_Plankton",
                    liquidity="11086.4",
                    market_cap="9194",
                    price_usd="0.000009195",
                    volume_24h="226917.14"
                )
                db.add(sample_campaign)
                await db.commit()
                print("Sample campaign created")
                
        except Exception as e:
            print(f"Error creating sample campaign: {e}")
        finally:
            break  # Only use the first session from the generator

    print("Application startup complete")
    
    yield
    
    # Shutdown
    print("Shutting down application...")
    # Add cleanup code here if needed


# Initialize FastAPI app
app = FastAPI(
    lifespan=lifespan,
    title="DexVault Campaign System",
    description="Campaign management and monitoring system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routers)

# Mount Socket.IO
# app.mount("/socket.io", socket_app)

# if __name__ == '__main__':
#     uvicorn.run(
#         "main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=True,
#         log_level="info"
#     )