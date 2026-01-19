from __future__ import annotations

import allure
from loguru import logger

from domains.db.users.contracts import UserCreate
from domains.db.users.repositories.user_repository import UserRepository
from domains.db.users.models import User


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    @allure.step("Получить последнего пользователя по имени")
    def get_last_user_by_name_prefix(self, prefix: str = "user_") -> User:
        last_user = self._repository.get_last_by_name_prefix(prefix)
        if not last_user:
            logger.error("Код 404: Пользователи с префиксом {prefix} не найдены", prefix=prefix)
            raise ValueError("Пользователь с указанным префиксом не найден")
        return last_user

    @allure.step("Создать пользователя")
    def create_user(self, user_data: UserCreate) -> User:
        user = User(name=user_data.name, email=user_data.email)
        return self._repository.add(user)
