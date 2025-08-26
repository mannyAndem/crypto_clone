from pydantic import BaseModel
from typing import Optional
from datetime import datetime
# Pydantic models for request/response
class CampaignCreate(BaseModel):
    contract_address: str
    goal_amount: float
    expires_at: str 
    campaign_type:str
    social_twitter: Optional[str] = None
    social_website: Optional[str] = None
    description: Optional[str] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    


class CampaignData(BaseModel):
    id: str
    name: str
    symbol: Optional[str] = None
    contract_address: str
    image_url: Optional[str] = None
    wallet_address: str
    goal_amount: float
    status: str
    created_at: datetime
    expires_at: datetime
    campaign_type: Optional[str] = None
    social_twitter: Optional[str] = None
    social_website: Optional[str] = None
    description: Optional[str] = None
    current_balance: float
    contributor_count: int
    token_launchpad: Optional[str] = None
    token_source: Optional[str] = None
    liquidity: Optional[str] = "0"
    market_cap: Optional[str] = "0"
    price_usd: Optional[str] = "0"
    volume_24h: Optional[str] = "0"


class CampaignResponse(BaseModel):
    success: bool
    campaign_id: Optional[str] = None
    escrow_address: Optional[str] = None
    error: Optional[str] = None
    campaign: Optional[CampaignData] = None
