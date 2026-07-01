import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.config import settings
from app.schemas import ChatRequest
from tools.kpi_calculator import KPICalculator


def test_settings_load():
    assert settings.app_env is not None
    assert settings.aws_region is not None


def test_chat_request_schema():
    request = ChatRequest(question="Compara el promedio por regional")
    assert request.question == "Compara el promedio por regional"


def test_kpi_gap_calculation():
    calculator = KPICalculator()

    result = calculator.calculate_gap(
        value_a=72.63,
        value_b=68.27,
        label_a="Bogotá",
        label_b="Antioquia",
    )

    assert result["success"] is True
    assert result["absolute_gap"] == 4.36
    assert result["higher_value"] == "Bogotá"