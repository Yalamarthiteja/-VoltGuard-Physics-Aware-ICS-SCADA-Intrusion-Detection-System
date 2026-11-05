
"""
VoltGuard - Flask Monitoring Dashboard

Connects:
1. Command Simulator
2. Physics Engine through Decision Engine
3. Event Logger
4. CSV Event History
"""

import csv
import os
import io

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

from flask import Flask, render_template_string, request, send_file

from command_simulator import generate_command
from decision_engine import evaluate_command
from event_logger import log_event, initialize_logger
from physics_engine import MAX_SAFE_PRESSURE


app = Flask(__name__)

LOG_FILE = os.path.join("logs", "voltguard_events.csv")


# --------------------------------------------------
# READ EVENT HISTORY
# --------------------------------------------------

def get_events():

    initialize_logger()

    with open(LOG_FILE, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return list(reader)


# --------------------------------------------------
# CALCULATE DASHBOARD STATISTICS
# --------------------------------------------------

def get_statistics(events):

    stats = {
        "total": len(events),
        "allowed": 0,
        "blocked": 0,
        "invalid": 0
    }

    for event in events:

        decision = event.get("decision", "").upper()

        if decision == "ALLOW":
            stats["allowed"] += 1

        elif decision == "BLOCK":
            stats["blocked"] += 1

        elif decision == "INVALID":
            stats["invalid"] += 1

    return stats


# --------------------------------------------------
# PROCESS INDUSTRIAL COMMAND
# --------------------------------------------------

def process_dashboard_command(command_type):

    command = generate_command(command_type)

    result = evaluate_command(command)

    log_event(command, result)

    return {
        "command": command,
        "result": result
    }


# --------------------------------------------------
# DASHBOARD HTML
# --------------------------------------------------

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width, initial-scale=1">

    <title>VoltGuard Monitoring Dashboard</title>

    <style>

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            padding: 25px;
            font-family: Arial, sans-serif;
            background: #101827;
            color: white;
        }

        header {
            text-align: center;
            margin-bottom: 30px;
        }

        header h1 {
            color: #00d4ff;
            font-size: 36px;
        }

        header p {
            color: #b8c7d9;
        }

        .status {
            color: #00ff99;
            font-weight: bold;
        }

        /* STATISTICS CARDS */

        .cards {
            display: grid;
            grid-template-columns:
                repeat(auto-fit, minmax(180px, 1fr));
            gap: 18px;
            margin-bottom: 30px;
        }

        .card {
            background: #1e293b;
            padding: 22px;
            border-radius: 12px;
            text-align: center;
        }

        .card h3 {
            color: #b8c7d9;
            font-size: 15px;
        }

        .card h2 {
            font-size: 32px;
        }

        .allowed {
            color: #00ff99;
        }

        .blocked {
            color: #ff5555;
        }

        .invalid {
            color: #ffcc66;
        }

        /* DASHBOARD SECTIONS */

        .section {
            background: #1e293b;
            padding: 22px;
            border-radius: 12px;
            margin-bottom: 25px;
        }

        /* COMMAND BUTTONS */

        .buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-top: 20px;
        }

        button {
            padding: 13px 22px;
            border: none;
            border-radius: 7px;
            cursor: pointer;
            font-weight: bold;
            color: white;
            font-size: 14px;
        }

        .normal {
            background: #138a57;
        }

        .suspicious {
            background: #c0392b;
        }

        .invalid-btn {
            background: #a97817;
        }

        button:hover {
            opacity: 0.8;
        }

        /* LATEST RESULT */

        .result {
            background: #26364c;
            padding: 18px;
            border-radius: 8px;
            margin-top: 22px;
            overflow-wrap: anywhere;
        }

        .decision-allow {
            color: #00ff99;
            font-weight: bold;
        }

        .decision-block {
            color: #ff5555;
            font-weight: bold;
        }

        .decision-invalid {
            color: #ffcc66;
            font-weight: bold;
        }

        /* EVENT HISTORY TABLE */

        table {
            width: 100%;
            border-collapse: collapse;
            overflow-wrap: anywhere;
        }

        th, td {
            padding: 12px;
            border-bottom: 1px solid #3c4b60;
            text-align: left;
        }

        th {
            color: #00d4ff;
        }

        .table-container {
            overflow-x: auto;
        }

        /* RESPONSIVE DESIGN */

        @media(max-width: 600px) {

            body {
                padding: 12px;
            }

            header h1 {
                font-size: 27px;
            }

            .section {
                padding: 15px;
            }

        }

    </style>

</head>


<body>

    <!-- HEADER -->

    <header>

        <h1>VOLTGUARD</h1>

        <h2>
            Physics-Aware ICS/SCADA Intrusion Detection System
        </h2>

        <p>
            System Status:
            <span class="status">ONLINE</span>
        </p>

    </header>


    <!-- STATISTICS -->

    <div class="cards">

        <div class="card">

            <h3>Total Commands</h3>

            <h2>{{ stats.total }}</h2>

        </div>


        <div class="card">

            <h3>Allowed Commands</h3>

            <h2 class="allowed">
                {{ stats.allowed }}
            </h2>

        </div>


        <div class="card">

            <h3>Blocked Commands</h3>

            <h2 class="blocked">
                {{ stats.blocked }}
            </h2>

        </div>


        <div class="card">

            <h3>Invalid Commands</h3>

            <h2 class="invalid">
                {{ stats.invalid }}
            </h2>

        </div>

    </div>


    <!-- INDUSTRIAL COMMAND SIMULATION -->

    <div class="section">

        <h2>Industrial Command Simulation</h2>

        <p>
            Generate simulated industrial commands
            and evaluate their physical safety.
        </p>


        <form method="POST" action="/simulate">

            <div class="buttons">

                <button
                    class="normal"
                    type="submit"
                    name="command_type"
                    value="NORMAL">

                    Normal Command

                </button>


                <button
                    class="suspicious"
                    type="submit"
                    name="command_type"
                    value="SUSPICIOUS">

                    Suspicious Command

                </button>


                <button
                    class="invalid-btn"
                    type="submit"
                    name="command_type"
                    value="INVALID">

                    Invalid Command

                </button>

            </div>

        </form>


        <!-- LATEST SIMULATION RESULT -->

        {% if latest %}

        <div class="result">

            <h3>Latest Simulation Result</h3>

            <p>
                <strong>Command Type:</strong>
                {{ latest.command.command_type }}
            </p>

            <p>
                <strong>Generated Command:</strong>
                {{ latest.command }}
            </p>

            <p>
                <strong>Decision:</strong>

                {% if latest.result.decision == "ALLOW" %}

                    <span class="decision-allow">
                        ALLOW
                    </span>

                {% elif latest.result.decision == "BLOCK" %}

                    <span class="decision-block">
                        BLOCK
                    </span>

                {% else %}

                    <span class="decision-invalid">
                        INVALID
                    </span>

                {% endif %}

            </p>

            <p>
                <strong>Reason:</strong>
                {{ latest.result.reason }}
            </p>


            {% if latest.result.details %}

            <p>
                <strong>Predicted Pressure:</strong>
                {{ latest.result.details.predicted_pressure }} bar
            </p>

            <p>
                <strong>Configured Pressure Limit:</strong>
                {{ latest.result.details.pressure_limit }} bar
            </p>

            {% else %}

            <p>
                <strong>Predicted Pressure:</strong>
                Not available because the command is invalid.
            </p>

            {% endif %}

        </div>

        {% endif %}

    </div>

    <!-- PRESSURE MONITORING -->

<div class="section">

    <h2>Industrial Pressure Monitoring</h2>

    <p>
        Monitor predicted pressure readings against
        the configured 8-bar safety threshold.
    </p>

    <div class="table-container">

        <img
            src="/pressure-chart.png"
            alt="VoltGuard Pressure Monitoring Chart"
            style="width:100%; max-width:100%; border-radius:10px;"
        >

    </div>

</div>


    <!-- RECENT SECURITY EVENTS -->

    <div class="section">

        <h2>Recent Security Events</h2>

        <div class="table-container">

            <table>

                <thead>

                    <tr>

                        <th>Timestamp</th>

                        <th>Type</th>

                        <th>RPM</th>

                        <th>Valve</th>

                        <th>Pressure</th>

                        <th>Decision</th>

                    </tr>

                </thead>


                <tbody>

                    {% for event in recent_events %}

                    <tr>

                        <td>{{ event.timestamp }}</td>

                        <td>{{ event.command_type }}</td>

                        <td>{{ event.pump_rpm }}</td>

                        <td>{{ event.valve_opening }}</td>

                        <td>
                            {% if event.predicted_pressure %}
                                {{ event.predicted_pressure }}
                            {% else %}
                                N/A
                            {% endif %}
                        </td>

                        <td>{{ event.decision }}</td>

                    </tr>

                    {% else %}

                    <tr>

                        <td colspan="6">
                            No events recorded yet.
                        </td>

                    </tr>

                    {% endfor %}

                </tbody>

            </table>

        </div>

    </div>


</body>

</html>
"""


# --------------------------------------------------
# HOME ROUTE
# --------------------------------------------------

@app.route("/", methods=["GET"])
def home():

    events = get_events()

    stats = get_statistics(events)

    return render_template_string(
        HTML_PAGE,
        stats=stats,
        recent_events=events[-10:][::-1],
        latest=None
    )


# --------------------------------------------------
# SIMULATION ROUTE
# --------------------------------------------------

@app.route("/simulate", methods=["POST"])
def simulate():

    command_type = request.form.get(
        "command_type", ""
    ).upper()

    if command_type not in [
        "NORMAL",
        "SUSPICIOUS",
        "INVALID"
    ]:

        return "Invalid command type", 400


    # Generate and evaluate command

    latest = process_dashboard_command(command_type)


    # Refresh dashboard data

    events = get_events()

    stats = get_statistics(events)


    return render_template_string(
        HTML_PAGE,
        stats=stats,
        recent_events=events[-10:][::-1],
        latest=latest
    )


# --------------------------------------------------
# PRESSURE MONITORING CHART
# --------------------------------------------------

@app.route("/pressure-chart.png")
def pressure_chart():

    events = get_events()

    pressure_values = []

    for event in events:

        try:
            pressure = float(event.get("predicted_pressure", ""))

            pressure_values.append(pressure)

        except (ValueError, TypeError):
            continue

    # Create chart

    fig, ax = plt.subplots(figsize=(10, 4))

    if pressure_values:

        event_numbers = list(
            range(1, len(pressure_values) + 1)
        )

        ax.plot(
            event_numbers,
            pressure_values,
            marker="o",
            linewidth=2,
            label="Predicted Pressure"
        )

        ax.scatter(
            event_numbers,
            pressure_values
        )

        # Highlight readings above the safety limit

        unsafe_x = [
            x for x, pressure in zip(event_numbers, pressure_values)
            if pressure > MAX_SAFE_PRESSURE
        ]

        unsafe_y = [
            pressure for pressure in pressure_values
            if pressure > MAX_SAFE_PRESSURE
        ]

        if unsafe_x:

            ax.scatter(
                unsafe_x,
                unsafe_y,
                color="red",
                s=70,
                label="Above Safety Limit",
                zorder=5
            )

    else:

        ax.text(
            0.5,
            0.5,
            "No valid pressure readings available",
            horizontalalignment="center",
            verticalalignment="center",
            transform=ax.transAxes
        )

    # Safety threshold

    ax.axhline(
        y=MAX_SAFE_PRESSURE,
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Safety Limit ({MAX_SAFE_PRESSURE} bar)"
    )

    ax.set_title("VoltGuard - Industrial Pressure Monitoring")

    ax.set_xlabel("Simulation Event Number")

    ax.set_ylabel("Predicted Pressure (bar)")

    ax.grid(True, alpha=0.3)

    ax.legend()

    fig.tight_layout()

    # Convert chart into an image

    image_buffer = io.BytesIO()

    fig.savefig(
        image_buffer,
        format="png",
        dpi=100
    )

    plt.close(fig)

    image_buffer.seek(0)

    return send_file(
        image_buffer,
        mimetype="image/png"
    )

# --------------------------------------------------
# START FLASK APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    initialize_logger()

    print("\n========== VOLTGUARD DASHBOARD ==========\n")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
