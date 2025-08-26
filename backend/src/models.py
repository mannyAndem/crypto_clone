
from datetime import datetime, timezone
import uuid
from decimal import Decimal
from src.base import Base
import sqlalchemy as sa
class Campaign(Base):
    __tablename__ = 'campaigns'
    
    id = sa.Column(sa.String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    campaign_id = sa.Column(sa.String(20), unique=True, nullable=False, index=True)
    wallet_address = sa.Column(sa.String(44), nullable=False)  # Escrow wallet
    is_active = sa.Column(sa.Boolean, default=True)
    
    #from creating the endpoint
    contract_address = sa.Column(sa.String(44), nullable=False)  # Token contract
    goal_amount = sa.Column(sa.Numeric(15, 2), nullable=False)  # Goal in USD
    expires_at = sa.Column(sa.DateTime(timezone=True), nullable=False)
    campaign_type = sa.Column(sa.String(50), nullable=False)
    
    #from dexscrenner api
    name = sa.Column(sa.String(255), nullable=False)  # Token name
    symbol = sa.Column(sa.String(20), nullable=False)  # Token symbol
    image_url = sa.Column(sa.Text)  # Token image
    status = sa.Column(sa.String(20), default='active') #use enum later
    created_at = sa.Column(sa.DateTime(timezone=True), default=datetime.now(timezone.utc))
    social_twitter = sa.Column(sa.Text)
    social_website = sa.Column(sa.Text)
    description = sa.Column(sa.Text)
    token_launchpad = sa.Column(sa.String(50))
    token_source = sa.Column(sa.String(50))
    liquidity = sa.Column(sa.String(20))
    market_cap = sa.Column(sa.String(20))
    price_usd = sa.Column(sa.String(20))
    volume_24h = sa.Column(sa.String(20))

class TokenCache(Base):
    __tablename__ = 'token_cache'
    
    contract_address = sa.Column(sa.String(44), primary_key=True, index=True)
    name = sa.Column(sa.String(255))
    symbol = sa.Column(sa.String(20))
    decimals = sa.Column(sa.Integer)
    price_usd = sa.Column(sa.Numeric(15, 8))
    total_supply = sa.Column(sa.BigInteger)
    holders_count = sa.Column(sa.Integer)
    last_updated = sa.Column(sa.DateTime(timezone=True), default=datetime.now(timezone.utc))

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = sa.Column(sa.String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    campaign_id = sa.Column(sa.String(20), nullable=False, index=True)
    signature = sa.Column(sa.String(88), unique=True, nullable=False)  # Changed from tx_hash
    amount = sa.Column(sa.Numeric(20, 9), nullable=False)  # Amount in SOL
    from_wallet = sa.Column(sa.String(44), nullable=False)  # Changed from sender_wallet
    to_wallet = sa.Column(sa.String(44), nullable=False)  # Changed from recipient_wallet
    timestamp = sa.Column(sa.Integer, nullable=False)  # Unix timestamp
    amount_usd = sa.Column(sa.Numeric(15, 2))
    block_time = sa.Column(sa.DateTime(timezone=True))
    processed_at = sa.Column(sa.DateTime(timezone=True), default=datetime.now(timezone.utc))
