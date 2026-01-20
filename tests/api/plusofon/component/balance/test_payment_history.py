import allure
import pytest

from domains.api.plusofon.balance import BalanceService

@allure.parent_suite("API")
@allure.suite("Balance")
@allure.title("История операций: получение истории для типа {operation_type}")
@pytest.mark.smoke
@pytest.mark.parametrize("operation_type", ["payment", "charge", "subscription"])
def test_get_payment_history_positive(
    balance_service: BalanceService, operation_type: str
) -> None:
    # Arrange
    service = balance_service
    # Act
    with allure.step("Выполнить запрос истории операций"):
        response, history_response = service.get_payment_history(
            operation_type=operation_type,
        )

    # Assert
    with allure.step("Проверить успешный ответ"):
        assert response.status_code == 200
        assert history_response.success is True

    with allure.step("Проверить структуру ответа"):
        assert history_response.history

    with allure.step("Проверить формат записей истории"):
        for item in history_response.history:
            assert isinstance(item.money, int)
            assert item.money >= 0