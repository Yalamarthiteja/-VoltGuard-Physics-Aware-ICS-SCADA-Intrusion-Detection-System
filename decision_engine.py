"""
VoltGuard - Safety Decision Engine

Purpose:
Evaluate industrial commands using the Physics Engine
and classify them as ALLOW, BLOCK, or INVALID.
"""

from physics_engine import check_physical_safety


# --------------------------------------------------
# DECISION ENGINE
# --------------------------------------------------

def evaluate_command(command):

    # Step 1: Validate command structure

    if not isinstance(command, dict):

        return {
            "decision": "INVALID",
            "reason": "Command must be a dictionary.",
            "details": None
        }

    required_fields = ["pump_rpm", "valve_opening"]

    for field in required_fields:

        if field not in command:

            return {
                "decision": "INVALID",
                "reason": f"Missing required field: {field}",
                "details": None
            }

    # Step 2: Check physical safety

    try:

        safety_result = check_physical_safety(
            command["pump_rpm"],
            command["valve_opening"]
        )

    except (ValueError, TypeError) as error:

        return {
            "decision": "INVALID",
            "reason": str(error),
            "details": None
        }

    # Step 3: Make safety decision

    if not safety_result["safe"]:

        return {
            "decision": "BLOCK",
            "reason": "Physical safety violation detected.",
            "details": safety_result
        }

    # Step 4: Allow safe commands

    return {
        "decision": "ALLOW",
        "reason": "Command satisfies configured physical safety limits.",
        "details": safety_result
    }


# --------------------------------------------------
# STANDALONE TEST
# --------------------------------------------------

if __name__ == "__main__":

    print("\n========== VOLTGUARD DECISION ENGINE ==========\n")

    test_commands = [

        {
            "pump_rpm": 1000,
            "valve_opening": 100
        },

        {
            "pump_rpm": 3000,
            "valve_opening": 100
        },

        {
            "pump_rpm": -100,
            "valve_opening": 50
        },

        {
            "pump_rpm": 2000,
            "valve_opening": 0
        },

        {
            "pump_rpm": 1500
        }

    ]

    for command in test_commands:

        result = evaluate_command(command)

        print("------------------------------------")

        print("Command:", command)

        print("Decision:", result["decision"])

        print("Reason:", result["reason"])

        if result["details"]:

            print(
                "Predicted Pressure:",
                result["details"]["predicted_pressure"],
                "bar"
            )

    print("\n========== DECISION ENGINE COMPLETED ==========\n")
