
from pathlib import Path
import redis.asyncio as redis
from solana.rpc.api import Client
from typing import AsyncGenerator
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, StaticPool
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from pydantic_settings import BaseSettings, SettingsConfigDict
from src.base import Base
from src.logger import setup_logger

logger = setup_logger("config", "config.log")
class Config(BaseSettings):
    DATABASE_URL: str 
    SOLANA_RPC_URL: str
    WALLET: str
    REDIS_URL:str

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=Path(__file__).resolve().parent.parent / ".env",  # Adjusted to point to the root directory
        env_file_encoding="utf-8",
    )

config = Config()



# Sync engine/session
sync_engine = create_engine(config.DATABASE_URL)
SyncSessionLocal = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False)


#async config
engine = create_async_engine(url= config.DATABASE_URL)
async_session = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Creates and yields an asynchronous database session.

    This function is an asynchronous generator that creates a new database session
    using the async_session factory and yields it. The session is automatically
    closed when the generator is exhausted or the context is exited.

    Yields:
        AsyncSession: An asynchronous SQLAlchemy session object.

    Usage:
        async for session in get_session():
            # Use the session for database operations
            ...
    """
    async with async_session() as session:
        yield session


def get_db_session_sync():
    return SyncSessionLocal()

# for manual use (not in fastapi Dependency injection, normal class/aysnc func injection)
# async def get_db_session_sync() -> AsyncSession:
#     async with async_session() as session:
#         return session #every call will close this


# for manual use (not in fastapi Dependency injection, normal class/async func injection)
# async def get_manual_db_session() -> AsyncSession:
#     session = async_session()
#     return session   # caller must close it!

    




async def init_db():
    """
    Initialize the database by creating all tables defined in the Base metadata.

    This asynchronous function uses the SQLAlchemy engine to create all tables
    that are defined in the Base metadata. It's typically used when setting up
    the database for the first time or after a complete reset.

    The function uses a connection from the engine and runs the create_all
    method synchronously within the asynchronous context.
    """
    try:
        async with engine.begin() as conn:
            # Use run_sync to call the synchronous create_all method in an async context
            await conn.run_sync(Base.metadata.create_all)
    except SQLAlchemyError as e:
        logger.error(f"error creating the db: {e}")
# Redis configuration
try:
    redis_client = redis.from_url(url=config.REDIS_URL)
    redis_client.ping()
except:
    redis_client = None
    print("Warning: Redis not available, using in-memory cache")


async def drop_db():
    """
    Drop all tables in the database.

    This asynchronous function uses the SQLAlchemy engine to drop all tables
    that are defined in the Base metadata. It's typically used when you want
    to completely reset the database structure.

    Caution: This operation will delete all data in the tables. Use with care.
    """
    async with engine.begin() as conn:
        # Use run_sync to call the synchronous drop_all method in an async context
        await conn.run_sync(Base.metadata.drop_all)
        
# Solana RPC client
solana_client = Client(config.SOLANA_RPC_URL)

# Socket.IO configuration
# sio = socketio.AsyncServer(
#     cors_allowed_origins="*",
#     async_mode='asgi'
# )
# socket_app = socketio.ASGIApp(sio)