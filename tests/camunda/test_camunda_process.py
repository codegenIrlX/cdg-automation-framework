import uuid

import allure
import pytest

from framework.clients import CamundaClient


@allure.parent_suite("Camunda")
@allure.title("Camunda: запуск процесса sample_process")
@pytest.mark.smoke
def test_camunda_start_sample_process(camunda_client: CamundaClient) -> None:
    # Arrange
    business_key = f"sample_process_{uuid.uuid4()}"
    variables = {"requested_by": "pytest", "trace_id": str(uuid.uuid4())}

    # Act
    with allure.step("Запустить процесс sample_process"):
        process_instance = camunda_client.start_process(
            process_key="sample_process",
            business_key=business_key,
            variables=variables,
        )

    # Assert
    with allure.step("Проверить, что процесс успешно инициирован"):
        assert process_instance is not None
        assert process_instance.id_
        assert process_instance.definition_id
        assert process_instance.business_key == business_key
