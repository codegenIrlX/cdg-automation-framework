import allure
import pytest

from domains.api.plusofon.balance import BalanceService

@allure.parent_suite("API")
@allure.suite("Balance")
@allure.title("Баланс: получение текущего баланса")
@pytest.mark.smoke
def test_get_balance_positive(balance_service: BalanceService) -> None:
    # Arrange
    service = balance_service

    # Act
    with allure.step("Выполнить запрос на получение баланса"):
        response, balance = service.get_balance()

    # Assert
    with allure.step("Проверить успешный ответ и непустой баланс"):
        assert response.status_code == 200
        assert balance.balance is not None
