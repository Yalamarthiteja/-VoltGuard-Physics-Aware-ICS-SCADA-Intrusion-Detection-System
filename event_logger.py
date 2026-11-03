"""
VoltGuard - Event Logger

Purpose:
Record industrial commands, safety decisions,
predicted pressure, and timestamps in a CSV file.
"""

import csv
import os
from datetime import datetime


# CSV LOG FILE
LOG_FILE = os.path.join("logs", "voltguard_events.csv")


# ---------------------------------------
# CREATE LOG DIRECTORY
# ---------------------------------------

def initialize_logger():

    os.makedirs("logs", exist_ok=True)

    if not os.path.exists(LOG_FILE):

        with open(LOG_FILE, "w", newline="") as file:

            writer = csv.writer(file)

            writer.writerow([
                "timestamp",
                "command_type",
                "pump_rpm",
                "valve_opening",
                "predicted_pressure",
                "decision",
                "reason"
            ])


# ---------------------------------------
# LOG INDUSTRIAL EVENT
# ---------------------------------------

def log_event(command, decision_result):

    initialize_logger()

    details = decision_result.get("details")

    predicted_pressure = (
        details.get("predicted_pressure")
        if details else None
    )

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    record = [
        timestamp,
        command.get("command_type", "UNKNOWN"),
        command.get("pump_rpm"),
        command.get("valve_opening"),
        predicted_pressure,
        decision_result.get("decision"),
        decision_result.get("reason")
    ]

    with open(LOG_FILE, "a", newline="") as file:

        writer = csv.writer(file)

        writer.writerow(record)

    print("Event successfully logged.")


# ---------------------------------------
# STANDALONE TEST
# ---------------------------------------

if __name__ == "__main__":

    print("\n========== VOLTGUARD EVENT LOGGER ==========\n")

    sample_command = {
        "pump_rpm": 1000,
        "valve_opening": 100,
        "command_type": "NORMAL"
    }

    sample_decision = {
        "decision": "ALLOW",
        "reason": "Command satisfies safety limits.",
        "details": {
            "predicted_pressure": 1.5
        }
    }

    log_event(sample_command, sample_decision)

    print("\nLog file:", LOG_FILE)

    print("\n========== EVENT LOGGING COMPLETED ==========\n")