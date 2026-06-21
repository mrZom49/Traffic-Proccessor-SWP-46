from typing import Annotated
from datetime import datetime
import uuid
import types as tp
from typing import AsyncGenerator

from sqlalchemy import func, types
from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    async_sessionmaker, 
    AsyncAttrs, 
    AsyncSession
)
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

from ..config import DB_URL

engine = create_async_engine(
    DB_URL, 
    echo=False,
)
session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

uuid_pk = Annotated[uuid.UUID, mapped_column(types.Uuid, primary_key=True, default_factory=uuid.uuid4)]
crd_at = Annotated[datetime, mapped_column(server_default=func.now())]
upd_at = Annotated[datetime, mapped_column(server_default=func.now(), onupdate=datetime.now())]
unq_str = Annotated[str, mapped_column(unique=True)]


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[uuid_pk]
    created_at: Mapped[crd_at]
    upd_at: Mapped[upd_at]

    __abstract__ = True


async def session_getter():
    async with session_factory() as session:
        yield session
