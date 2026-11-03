"""
VoltGuard - Physics Engine

Purpose:
Simulate the physical behaviour of an industrial pump and valve system.
Estimate pressure and identify potentially unsafe operating conditions.

NOTE:
This is an illustrative simulation model for project demonstration.
It is not a validated industrial fluid-dynamics model.
"""

import math


# --------------------------------------------------
# CONFIGURABLE SAFETY PARAMETERS
# --------------------------------------------------

MAX_SAFE_RPM = 2500
MAX_SAFE_PRESSURE = 8.0  # bar

MIN_RPM = 0
MIN_VALVE_OPENING = 0
MAX_VALVE_OPENING = 100


# --------------------------------------------------
# INPUT VALIDATION
# --------------------------------------------------

def validate_inputs(pump_rpm, valve_opening):

    if isinstance(pump_rpm, bool) or not isinstance(pump_rpm, (int, float)):
        raise ValueError("Pump RPM must be a numeric value.")

    if isinstance(valve_opening, bool) or not isinstance(valve_opening, (int, float)):
        raise ValueError("Valve opening must be a numeric value.")

    if not math.isfinite(pump_rpm) or not math.isfinite(valve_opening):
        raise ValueError("Input values must be finite.")

    if pump_rpm < MIN_RPM:
        raise ValueError("Pump RPM cannot be negative.")

    if not MIN_VALVE_OPENING <= valve_opening <= MAX_VALVE_OPENING:
        raise ValueError("Valve opening must be between 0 and 100.")

    return True


# --------------------------------------------------
# PHYSICS SIMULATION
# --------------------------------------------------

def predict_pressure(pump_rpm, valve_opening):

    validate_inputs(pump_rpm, valve_opening)

    # Illustrative pump pressure calculation
    valve_factor = 1 + ((100 - valve_opening) / 100)

    predicted_pressure = (
        0.5 + 0.000001 * (pump_rpm ** 2) * valve_factor
    )

    return round(predicted_pressure, 2)


# --------------------------------------------------
# PHYSICAL SAFETY VALIDATION
# --------------------------------------------------

def check_physical_safety(pump_rpm, valve_opening):

    predicted_pressure = predict_pressure(
        pump_rpm,
        valve_opening
    )

    violations = []

    if pump_rpm > MAX_SAFE_RPM:
        violations.append(
            "Pump RPM exceeds the configured safety limit."
        )

    if predicted_pressure > MAX_SAFE_PRESSURE:
        violations.append(
            "Predicted pressure exceeds the configured safety limit."
        )

    return {

        "pump_rpm": pump_rpm,

        "valve_opening": valve_opening,

        "predicted_pressure": predicted_pressure,

        "pressure_limit": MAX_SAFE_PRESSURE,

        "safe": len(violations) == 0,

        "violations": violations

    }


# --------------------------------------------------
# STANDALONE TEST
# --------------------------------------------------

if __name__ == "__main__":

    print("\n========== VOLTGUARD PHYSICS ENGINE ==========\n")

    test_commands = [
        (1000, 100),
        (1500, 80),
        (2000, 100),
        (3000, 100),
        (2000, 0)
    ]

    for rpm, valve in test_commands:

        result = check_physical_safety(rpm, valve)

        print("------------------------------------")

        print("Pump RPM:", result["pump_rpm"])

        print("Valve Opening:", result["valve_opening"], "%")

        print("Predicted Pressure:", result["predicted_pressure"], "bar")

        print("Safety Status:", "SAFE" if result["safe"] else "UNSAFE")

        print("Violations:", result["violations"])

    print("\n========== SIMULATION COMPLETED ==========\n")
