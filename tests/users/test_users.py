import allure
import pytest
from mimesis import Person
from sqlalchemy.orm import Session
from uuid import uuid4

from domains.db.users import UserRepository, UserService
from domains.db.users.contracts import UserCreate

@allure.parent_suite("DB")
@allure.title("Пользователи: запись user_9 присутствует в базе")
@pytest.mark.smoke
def test_user_9_exists(db_session: Session) -> None:
    # Arrange
    repository = UserRepository(db_session)

    # Act
    exists = repository.exists_by_name_email(
        name="user_9",
        email="user_9@example.test",
    )

    # Assert
    assert exists is True


@allure.title("Пользователи: создание пользователя с заданными данными")
def test_create_user_with_data(db_session: Session) -> None:
    # Arrange
    repository = UserRepository(db_session)
    service = UserService(repository)
    generator = Person("en")
    user_suffix = uuid4().hex
    user_data = UserCreate(
        name=f"user_{user_suffix}",
        email=generator.email(),
    )

    # Act
    created_user = service.create_user(user_data)
    fetched_user = repository.get_by_name(created_user.name)

    # Assert
    assert fetched_user is not None
    assert fetched_user.name == user_data.name
    assert fetched_user.email == user_data.email
