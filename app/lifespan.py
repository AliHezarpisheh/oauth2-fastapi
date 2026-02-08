"""Module for setting lifespan context manager for FastAPI application."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from config.base import db, logger


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    """Set lifespan context manager for FastAPI application."""
    yield
    logger.info("Cleaning up the application...")
    await db.close_engine()
