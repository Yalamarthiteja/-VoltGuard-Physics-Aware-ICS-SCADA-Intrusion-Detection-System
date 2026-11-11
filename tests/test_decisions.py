
import pytest

from decision_engine import evaluate_command


def test_safe_command_returns_allow():
    command = {
        "pump_rpm": 1000,
        "valve_opening": 100
    }

    result = evaluate_command(command)

    assert result["decision"] == "ALLOW"


def test_unsafe_command_returns_block():
    command = {
        "pump_rpm": 3000,
        "valve_opening": 100
    }

    result = evaluate_command(command)

    assert result["decision"] == "BLOCK"


def test_negative_rpm_returns_invalid():
    command = {
        "pump_rpm": -100,
        "valve_opening": 50
    }

    result = evaluate_command(command)

    assert result["decision"] == "INVALID"


def test_missing_field_returns_invalid():
    command = {
        "pump_rpm": 1500
    }

    result = evaluate_command(command)

    assert result["decision"] == "INVALID"


def test_invalid_valve_returns_invalid():
    command = {
        "pump_rpm": 1000,
        "valve_opening": 120
    }

    result = evaluate_command(command)

    assert result["decision"] == "INVALID"


def test_non_dictionary_returns_invalid():
    result = evaluate_command("invalid command")

    assert result["decision"] == "INVALID"

