"""
VoltGuard - Main Application

Integrates:
1. Command Simulator
2. Physics Engine
3. Decision Engine
4. Event Logger
"""

from command_simulator import generate_command
from decision_engine import evaluate_command
from event_logger import log_event


# ---------------------------------------
# PROCESS INDUSTRIAL COMMAND
# ---------------------------------------

def process_command(command_type):

    print("\n------------------------------------")

    # Step 1: Generate command
    command = generate_command(command_type)

    print("Command Type:", command_type)
    print("Generated Command:", command)

    # Step 2: Evaluate command
    result = evaluate_command(command)

    print("Decision:", result["decision"])
    print("Reason:", result["reason"])

    # Step 3: Display predicted pressure
    if result["details"]:

        print(
            "Predicted Pressure:",
            result["details"]["predicted_pressure"],
            "bar"
        )

    # Step 4: Log event
    log_event(command, result)

    print("------------------------------------")


# ---------------------------------------
# MAIN EXECUTION
# ---------------------------------------

def main():

    print("\n========== VOLTGUARD ICS/SCADA SYSTEM ==========\n")

    command_types = [
        "NORMAL",
        "SUSPICIOUS",
        "INVALID"
    ]

    for command_type in command_types:

        process_command(command_type)

    print("\n========== VOLTGUARD EXECUTION COMPLETED ==========\n")


if __name__ == "__main__":

    main()
