
import pytest

from physics_engine import (
    predict_pressure,
    check_physical_safety
)

def test_normal_pressure_prediction():
    assert predict_pressure(1000, 100) == 1.5

def test_high_rpm_pressure_prediction():
    assert predict_pressure(3000, 100) == 9.5

def test_unsafe_high_rpm():
    result = check_physical_safety(3000, 100)
    assert result["safe"] is False

def test_safe_command():
    result = check_physical_safety(1000, 100)
    assert result["safe"] is True

def test_invalid_negative_rpm():
    with pytest.raises(ValueError):
        predict_pressure(-100, 50)

def test_invalid_valve_opening():
    with pytest.raises(ValueError):
        predict_pressure(1000, 120)
