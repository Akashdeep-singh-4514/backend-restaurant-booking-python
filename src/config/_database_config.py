import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config._logger import logger


class Base(DeclarativeBase):
    pass


class DatabaseConfig:
    _engine = None
    _session_factory = None

    @classmethod
    def get_db_url(cls) -> str:
        """
        Dynamically constructs the database URL from individual environment variables.
        """
        # First, check if a full URI is already provided (fallback for production)
        full_uri = os.getenv("SQLALCHEMY_DATABASE_URI")
        if full_uri:
            return full_uri

        # Otherwise, build it from parts
        user = os.getenv("DB_USER", "postgres")
        password = os.getenv("DB_PASSWORD", "postgres")
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "5432")
        name = os.getenv("DB_NAME", "little-lemon")

        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"

    @classmethod
    def get_engine(cls):
        if cls._engine is None:
            db_uri = cls.get_db_url()

            # Basic validation
            if "@localhost" in db_uri and os.getenv("DOCKER_RUNNING"):
                logger.warning("App is in Docker but trying to connect to localhost!")

            cls._engine = create_async_engine(
                db_uri,
                echo=os.getenv("SQLALCHEMY_ECHO_SQL", "False").lower() == "true",
                pool_size=int(os.getenv("SQLALCHEMY_POOL_SIZE", 5)),
                max_overflow=int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", 10)),
            )
            logger.info(
                f"SQLAlchemy AsyncEngine created for host: {os.getenv('DB_HOST', 'localhost')}"
            )
        return cls._engine

    @classmethod
    def _get_session_factory(cls):
        if cls._session_factory is None:
            cls._session_factory = async_sessionmaker(
                bind=cls.get_engine(), class_=AsyncSession, expire_on_commit=False
            )
            logger.info("SQLAlchemy AsyncSessionMaker created.")
        return cls._session_factory

    @classmethod
    async def get_db_session(cls) -> AsyncSession:
        session_factory = cls._get_session_factory()
        async with session_factory() as session:
            try:
                yield session
            finally:
                await session.close()

    @classmethod
    async def disconnect_db(cls):
        if cls._engine:
            await cls._engine.dispose()
            cls._engine = None
            cls._session_factory = None
            logger.info("SQLAlchemy AsyncEngine disposed.")
