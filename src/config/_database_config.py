# src/config/_database_config.py
import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config._logger import logger  # Import your logger


class Base(DeclarativeBase):
    """
    Base class which all ORM models will inherit.
    This is used by SQLAlchemy's declarative system to map Python classes to database tables.
    """

    pass


class DatabaseConfig:
    """
    Manages SQLAlchemy asynchronous database connection.
    """

    _engine = None
    _session_factory = None

    @classmethod
    def get_engine(cls):
        """
        Returns the SQLAlchemy AsyncEngine instance.
        Creates it if it doesn't already exist.
        """
        if cls._engine is None:
            db_uri = os.getenv("SQLALCHEMY_DATABASE_URI")
            if not db_uri:
                logger.error("SQLALCHEMY_DATABASE_URI environment variable is not set!")
                raise ValueError(
                    "SQLALCHEMY_DATABASE_URI environment variable is not set."
                )

            # create_async_engine requires the 'asyncpg' driver for PostgreSQL
            # Example URI: postgresql+asyncpg://user:password@host:port/database_name
            cls._engine = create_async_engine(
                db_uri,
                echo=os.getenv("SQLALCHEMY_ECHO_SQL", "False").lower()
                == "true",  # Set to True to log all SQL queries
                pool_size=int(os.getenv("SQLALCHEMY_POOL_SIZE", 5)),
                max_overflow=int(os.getenv("SQLALCHEMY_MAX_OVERFLOW", 10)),
            )
            logger.info("SQLAlchemy AsyncEngine created.")
        return cls._engine

    @classmethod
    def _get_session_factory(cls):
        """
        Returns the SQLAlchemy async_sessionmaker instance.
        Creates it if it doesn't already exist.
        """
        if cls._session_factory is None:
            # expire_on_commit=False prevents attributes from being detached
            # after commit, allowing access to them in the same session.
            cls._session_factory = async_sessionmaker(
                bind=cls.get_engine(), class_=AsyncSession, expire_on_commit=False
            )
            logger.info("SQLAlchemy AsyncSessionMaker created.")
        return cls._session_factory

    @classmethod
    async def get_db_session(cls) -> AsyncSession:
        """
        Dependency for FastAPI to get a database session.
        Yields an AsyncSession and ensures it's closed after use.
        """
        session_factory = cls._get_session_factory()
        async with session_factory() as session:
            try:
                yield session
            finally:
                await session.close()
                logger.debug("Database session closed.")

    @classmethod
    async def disconnect_db(cls):
        """
        Closes the database engine connections.
        Call this during application shutdown.
        """
        if cls._engine:
            await cls._engine.dispose()
            cls._engine = None
            cls._session_factory = None  # Reset session factory as engine is disposed
            logger.info("SQLAlchemy AsyncEngine disposed.")
