from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from domains.db.users.models import User
from framework.db.repositories import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: Session) -> None:
        super().__init__(session=session, model=User)

    def exists_by_name_email(self, name: str, email: str) -> bool:
        return self.exists(name=name, email=email)

    def get_last_by_name_prefix(self, prefix: str) -> User | None:
        query = (
            select(User)
            .where(User.name.like(f"{prefix}%"))
            .order_by(User.name.desc())
            .limit(1)
        )
        return self._session.execute(query).scalars().one_or_none()

    def get_by_name(self, name: str) -> User | None:
        query = select(User).where(User.name == name).limit(1)
        return self._session.execute(query).scalars().one_or_none()
