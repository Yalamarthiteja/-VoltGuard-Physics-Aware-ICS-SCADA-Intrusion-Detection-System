from command_simulator import generate_command


def test_normal_command():
    command = generate_command("NORMAL")

    assert command["command_type"] == "NORMAL"
    assert 0 <= command["pump_rpm"] <= 2500
    assert 0 <= command["valve_opening"] <= 100


def test_suspicious_command():
    command = generate_command("SUSPICIOUS")

    assert command["command_type"] == "SUSPICIOUS"
    assert command["pump_rpm"] > 2500


def test_invalid_command():
    command = generate_command("INVALID")

    assert command["command_type"] == "INVALID"


def test_unknown_command():
    try:
        generate_command("UNKNOWN")
        assert False, "Expected ValueError"
    except ValueError:
        assert True