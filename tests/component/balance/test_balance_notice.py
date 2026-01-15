import allure
import pytest

from framework.services import BalanceService


@allure.title("Порог баланса: получение")
@pytest.mark.smoke
def test_get_balance_notice_positive(balance_service: BalanceService) -> None:
    # Arrange
    service = balance_service

    # Act
    with allure.step("Выполнить запрос на получение порога баланса"):
        response, notice = service.get_balance_notice()

    # Assert
    with allure.step("Проверить успешный ответ и корректное значение порога"):
        assert response.status_code == 200
        assert notice.amount is not None
