"""Custom fixtures, hooks, and configurations for pytest tests."""

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_scoped_session

from app.main import app
from config.base import settings
from config.database import AsyncDatabaseConnection
from toolkit.api.dependencies import get_async_db_session
from toolkit.database.orm import Base

# Database-related hooks


@pytest.fixture(scope="session")
def db() -> AsyncDatabaseConnection:
    """Async database connection objects for testing."""
    return AsyncDatabaseConnection(database_url=settings.database_url)


@pytest_asyncio.fixture
async def db_engine(db: AsyncDatabaseConnection) -> AsyncGenerator[None]:
    """
    Fixture providing a SQLAlchemy async engine instance connected to the database.

    The main purpose of the fixture is creating and dropping tables, at start and end
    of the test session. Also, it close the engine after the test session.

    Parameters
    ----------
    db : AsyncDatabaseConnection
        The object for managing database objects.

    Yields
    ------
    AsyncGenerator[Engine]
        An async generator yielding the SQLAlchemy engine instance.
    """
    engine = db.get_engine()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await db.close_engine()


@pytest_asyncio.fixture
async def db_session(
    db: AsyncDatabaseConnection, db_engine: AsyncEngine
) -> AsyncGenerator[async_scoped_session[AsyncSession]]:
    """
    Fixture providing an async scoped SQLAlchemy session.

    Parameters
    ----------
    db : AsyncDatabaseConnection
        The object for managing database objects.

    Returns
    -------
    async_scoped_session[AsyncSession]
        An async scoped SQLAlchemy session.
    """
    session = db.get_session()
    yield session
    await session.rollback()

    # Truncate all tables after each test function.
    for table in reversed(Base.metadata.sorted_tables):
        stmt = text(f"TRUNCATE {table.name} CASCADE;")
        await session.execute(stmt)
        await session.commit()

    await session.close()


@pytest.fixture(autouse=True)
def override_get_async_db_session(
    db_session: async_scoped_session[AsyncSession], db_engine: AsyncEngine
) -> None:
    """
    Override the `get_async_db_session` dependency to use the provided database session.

    Parameters
    ----------
    db_session : async_scoped_session[AsyncSession]
        The test database session to be used instead of the default session.
    """

    async def _get_async_test_db_session() -> AsyncGenerator[
        async_scoped_session[AsyncSession]
    ]:
        """
        Get a test database session.

        Yields
        ------
        Session
            A test database session.
        """
        yield db_session

    app.dependency_overrides[get_async_db_session] = _get_async_test_db_session


# API-related hooks


@pytest.fixture(scope="session")
def sync_api_client() -> TestClient:
    """Fixture to create a synchronous FastAPI test client."""
    return TestClient(app=app)


@pytest_asyncio.fixture
async def async_api_client() -> AsyncGenerator[AsyncClient]:
    """Fixture to create an asynchronous FastAPI test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
