import csv
import event_logger


def test_event_logging(tmp_path, monkeypatch):

    log_file = tmp_path / "test_events.csv"

    monkeypatch.setattr(
        event_logger,
        "LOG_FILE",
        str(log_file)
    )

    command = {
        "pump_rpm": 1000,
        "valve_opening": 100,
        "command_type": "NORMAL"
    }

    result = {
        "decision": "ALLOW",
        "reason": "Command is safe.",
        "details": {
            "predicted_pressure": 1.5
        }
    }

    event_logger.log_event(command, result)

    with open(log_file, "r", newline="") as file:
        rows = list(csv.DictReader(file))

    assert len(rows) == 1
    assert rows[0]["decision"] == "ALLOW"
    assert rows[0]["pump_rpm"] == "1000"
    assert rows[0]["predicted_pressure"] == "1.5"