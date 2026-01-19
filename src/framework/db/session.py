from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.orm import Session, sessionmaker


def create_engine_from_dsn(dsn: str, *, echo: bool = False) -> Engine:
    return create_engine(dsn, pool_pre_ping=True, echo=echo)


def create_session_factory(bind: Engine | Connection) -> sessionmaker[Session]:
    return sessionmaker(bind=bind, autoflush=False, autocommit=False, expire_on_commit=False)
