import allure
import pytest

from domains.api.plusofon.balance import BalanceService


@allure.parent_suite("API")
@allure.suite("Balance")
@allure.title("Автоплатеж: получение статуса")
@pytest.mark.smoke
def test_get_autopay_positive(balance_service: BalanceService) -> None:
    # Arrange
    service = balance_service

    # Act
    with allure.step("Выполнить запрос на получение статуса автоплатежа"):
        response, autopay = service.get_autopay()

    # Assert
    with allure.step("Проверить успешный ответ и базовую структуру полей"):
        assert response.status_code == 200
        assert isinstance(autopay.access, bool)
        assert isinstance(autopay.active, bool)
        assert autopay.sum is None or isinstance(autopay.sum, int)
        assert autopay.success is True
