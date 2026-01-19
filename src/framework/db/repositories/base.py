from __future__ import annotations

from typing import Any, Generic, TypeVar

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(self, session: Session, model: type[ModelType]) -> None:
        self._session = session
        self._model = model

    def get_by_id(self, model_id: int) -> ModelType | None:
        return self._session.get(self._model, model_id)

    def select_by_filters(self, **filters: Any) -> list[ModelType]:
        query = self._apply_filters(select(self._model), filters)
        return list(self._session.execute(query).scalars().all())

    def exists(self, **filters: Any) -> bool:
        query = self._apply_filters(select(self._model), filters).limit(1)
        return self._session.execute(query).first() is not None

    def add(self, model: ModelType) -> ModelType:
        self._session.add(model)
        self._session.flush()
        return model

    def _apply_filters(
        self,
        query: Select[tuple[ModelType]],
        filters: dict[str, Any],
    ) -> Select[tuple[ModelType]]:
        for field, value in filters.items():
            query = query.where(getattr(self._model, field) == value)
        return query
