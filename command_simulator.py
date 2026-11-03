"""
VoltGuard - Industrial Command Simulator

Purpose:
Generate normal, suspicious, and invalid
industrial pump commands for simulation.
"""

import random


# ---------------------------------------
# NORMAL INDUSTRIAL COMMANDS
# ---------------------------------------

def generate_normal_command():

    return {
        "pump_rpm": random.choice([800, 1000, 1200, 1500]),
        "valve_opening": random.choice([70, 80, 90, 100]),
        "command_type": "NORMAL"
    }


# ---------------------------------------
# SUSPICIOUS INDUSTRIAL COMMANDS
# ---------------------------------------

def generate_suspicious_command():

    return {
        "pump_rpm": random.choice([2800, 3000, 3500]),
        "valve_opening": random.choice([0, 10, 20]),
        "command_type": "SUSPICIOUS"
    }


# ---------------------------------------
# INVALID INDUSTRIAL COMMANDS
# ---------------------------------------

def generate_invalid_command():

    return random.choice([

        {
            "pump_rpm": -100,
            "valve_opening": 50,
            "command_type": "INVALID"
        },

        {
            "pump_rpm": 1000,
            "valve_opening": 150,
            "command_type": "INVALID"
        },

        {
            "pump_rpm": 1500,
            "command_type": "INVALID"
        }

    ])


# ---------------------------------------
# GENERATE ALL COMMAND TYPES
# ---------------------------------------

def generate_command(command_type):

    if command_type == "NORMAL":
        return generate_normal_command()

    elif command_type == "SUSPICIOUS":
        return generate_suspicious_command()

    elif command_type == "INVALID":
        return generate_invalid_command()

    else:
        raise ValueError("Unknown command type.")


# ---------------------------------------
# STANDALONE TEST
# ---------------------------------------

if __name__ == "__main__":

    print("\n========== VOLTGUARD COMMAND SIMULATOR ==========\n")

    command_types = [
        "NORMAL",
        "SUSPICIOUS",
        "INVALID"
    ]

    for command_type in command_types:

        command = generate_command(command_type)

        print("------------------------------------")

        print("Command Type:", command_type)

        print("Generated Command:", command)

    print("\n========== SIMULATION COMPLETED ==========\n")
