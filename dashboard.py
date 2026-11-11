"""
VoltGuard - Flask Monitoring Dashboard

Features:
1. Industrial command simulation (NORMAL / SUSPICIOUS / INVALID)
2. Physics-aware ALLOW / BLOCK / INVALID decisions
3. CSV event logging and recent event history
4. Industrial pressure monitoring chart
5. Security decision distribution chart
6. Daily security-event trend chart
7. Pressure-safety analytics

This is a local simulation dashboard, not a controller for live industrial equipment.
"""

import csv
import io
import os
from collections import defaultdict
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from flask import Flask, render_template_string, request, send_file

from command_simulator import generate_command
from decision_engine import evaluate_command
from event_logger import log_event, initialize_logger
from physics_engine import MAX_SAFE_PRESSURE


app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "logs", "voltguard_events.csv")


# --------------------------------------------------
# EVENT HISTORY
# --------------------------------------------------

def get_events():
    initialize_logger()

    with open(LOG_FILE, "r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def get_statistics(events):
    stats = {
        "total": len(events),
        "allowed": 0,
        "blocked": 0,
        "invalid": 0,
        "pressure_violations": 0,
        "valid_pressure_readings": 0,
        "highest_pressure": None,
    }

    for event in events:
        decision = event.get("decision", "").upper()

        if decision == "ALLOW":
            stats["allowed"] += 1
        elif decision == "BLOCK":
            stats["blocked"] += 1
        elif decision == "INVALID":
            stats["invalid"] += 1

        try:
            pressure = float(event.get("predicted_pressure", ""))
        except (TypeError, ValueError):
            continue

        stats["valid_pressure_readings"] += 1
        if stats["highest_pressure"] is None or pressure > stats["highest_pressure"]:
            stats["highest_pressure"] = pressure
        if pressure > MAX_SAFE_PRESSURE:
            stats["pressure_violations"] += 1

    stats["highest_pressure"] = (
        round(stats["highest_pressure"], 2)
        if stats["highest_pressure"] is not None else None
    )
    return stats


# --------------------------------------------------
# COMMAND PROCESSING
# --------------------------------------------------

def process_dashboard_command(command_type):
    command = generate_command(command_type)
    result = evaluate_command(command)
    log_event(command, result)

    return {
        "command": command,
        "result": result,
    }


# --------------------------------------------------
# CHART HELPERS
# --------------------------------------------------

def chart_response(fig):
    buffer = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buffer, format="png", dpi=110, bbox_inches="tight")
    plt.close(fig)
    buffer.seek(0)
    return send_file(buffer, mimetype="image/png")


def parse_pressure_events(events):
    readings = []
    for event in events:
        try:
            pressure = float(event.get("predicted_pressure", ""))
            readings.append((event.get("timestamp", ""), pressure))
        except (TypeError, ValueError):
            continue
    return readings


# --------------------------------------------------
# DASHBOARD HTML
# --------------------------------------------------

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>VoltGuard Monitoring Dashboard</title>
    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0; padding: 25px; font-family: Arial, sans-serif;
            background: #101827; color: white;
        }
        header { text-align: center; margin-bottom: 30px; }
        header h1 { color: #00d4ff; font-size: 36px; margin-bottom: 8px; }
        header p { color: #b8c7d9; }
        .status { color: #00ff99; font-weight: bold; }
        .cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 18px; margin-bottom: 25px;
        }
        .card, .section {
            background: #1e293b; border-radius: 12px;
        }
        .card { padding: 20px; text-align: center; }
        .card h3 { color: #b8c7d9; font-size: 14px; }
        .card h2 { font-size: 30px; margin: 12px 0 4px; }
        .allowed { color: #00ff99; }
        .blocked { color: #ff6262; }
        .invalid { color: #ffcc66; }
        .warning { color: #ff8c42; }
        .muted { color: #aebdd0; font-size: 13px; }
        .section { padding: 22px; margin-bottom: 25px; }
        .section h2 { margin-top: 0; }
        .buttons { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 20px; }
        button {
            padding: 13px 22px; border: 0; border-radius: 7px;
            cursor: pointer; font-weight: bold; color: white; font-size: 14px;
        }
        button:hover { opacity: .82; }
        .normal { background: #138a57; }
        .suspicious { background: #c0392b; }
        .invalid-btn { background: #a97817; }
        .result {
            background: #26364c; padding: 18px; border-radius: 8px;
            margin-top: 22px; overflow-wrap: anywhere;
        }
        .decision-allow { color: #00ff99; font-weight: bold; }
        .decision-block { color: #ff6262; font-weight: bold; }
        .decision-invalid { color: #ffcc66; font-weight: bold; }
        .chart {
            width: 100%; max-width: 100%; background: white;
            border-radius: 9px; display: block;
        }
        .chart-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 18px; align-items: start;
        }
        .chart-panel { min-width: 0; }
        .chart-panel h3 { margin-top: 0; }
        .table-container { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; min-width: 650px; }
        th, td {
            padding: 12px; border-bottom: 1px solid #3c4b60; text-align: left;
        }
        th { color: #00d4ff; }
        .empty-chart {
        background: #26364c; padding: 30px; text-align: center;
            border-radius: 8px; color: #b8c7d9;
        }
        @media(max-width: 600px) {
            body { padding: 12px; }
            header h1 { font-size: 27px; }
            .section { padding: 15px; }
        }
    </style>
</head>
<body>
<header>
    <h1>VOLTGUARD</h1>
    <h2>Physics-Aware ICS/SCADA Intrusion Detection System</h2>
    <p>System Status: <span class="status">ONLINE</span></p>
    <p class="muted">Local simulation dashboard — no live industrial equipment is controlled.</p>
</header>

<!-- OVERVIEW CARDS -->
<div class="cards">
    <div class="card"><h3>Total Commands</h3><h2>{{ stats.total }}</h2></div>
    <div class="card"><h3>Allowed Commands</h3><h2 class="allowed">{{ stats.allowed }}</h2></div>
    <div class="card"><h3>Blocked Commands</h3><h2 class="blocked">{{ stats.blocked }}</h2></div>
    <div class="card"><h3>Invalid Commands</h3><h2 class="invalid">{{ stats.invalid }}</h2></div>
    <div class="card"><h3>Pressure Violations</h3><h2 class="warning">{{ stats.pressure_violations }}</h2></div>
    <div class="card">
        <h3>Highest Predicted Pressure</h3>
        <h2>{{ stats.highest_pressure if stats.highest_pressure is not none else "N/A" }}</h2>
        <span class="muted">bar</span>
    </div>
</div>

<!-- COMMAND SIMULATION -->
<div class="section">
    <h2>Industrial Command Simulation</h2>
    <p>Generate simulated pump commands and evaluate their physical safety.</p>
    <form method="POST" action="/simulate">
        <div class="buttons">
            <button class="normal" type="submit" name="command_type" value="NORMAL">Normal Command</button>
            <button class="suspicious" type="submit" name="command_type" value="SUSPICIOUS">Suspicious Command</button>
            <button class="invalid-btn" type="submit" name="command_type" value="INVALID">Invalid Command</button>
        </div>
    </form>

    {% if latest %}
    <div class="result">
        <h3>Latest Simulation Result</h3>
        <p><strong>Command Type:</strong> {{ latest.command.command_type }}</p>
        <p><strong>Generated Command:</strong> {{ latest.command }}</p>
        <p><strong>Decision:</strong>
            {% if latest.result.decision == "ALLOW" %}
                <span class="decision-allow">ALLOW</span>
            {% elif latest.result.decision == "BLOCK" %}
                <span class="decision-block">BLOCK</span>
            {% else %}
                <span class="decision-invalid">INVALID</span>
            {% endif %}
        </p>
        <p><strong>Reason:</strong> {{ latest.result.reason }}</p>
        {% if latest.result.details %}
            <p><strong>Predicted Pressure:</strong> {{ latest.result.details.predicted_pressure }} bar</p>
            <p><strong>Configured Pressure Limit:</strong> {{ latest.result.details.pressure_limit }} bar</p>
        {% else %}
            <p><strong>Predicted Pressure:</strong> Not available because the command is invalid.</p>
        {% endif %}
    </div>
    {% endif %}
</div>

<!-- SECURITY ANALYTICS -->
<div class="section">
    <h2>Security Event Analytics</h2>
    <p class="muted">Charts are calculated from recorded CSV events. Invalid commands may not have a pressure reading.</p>
    <div class="chart-grid">
        <div class="chart-panel">
            <h3>Command Decision Distribution</h3>
            <img class="chart" src="/decision-chart.png" alt="Command decision distribution chart">
        </div>
        <div class="chart-panel">
            <h3>Daily Security Event Trend</h3>
            <img class="chart" src="/event-trend.png" alt="Daily security event trend chart">
        </div>
    </div>
</div>

<!-- PRESSURE MONITORING -->
<div class="section">
    <h2>Industrial Pressure Monitoring</h2>
    <p>Predicted pressure readings compared with the configured {{ pressure_limit }}-bar safety threshold.</p>
    <img class="chart" src="/pressure-chart.png" alt="VoltGuard pressure monitoring chart">
</div>

<!-- RECENT SECURITY EVENTS -->
<div class="section">
    <h2>Recent Security Events</h2>
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th>Timestamp</th><th>Type</th><th>RPM</th>
                    <th>Valve</th><th>Pressure (bar)</th><th>Decision</th>
                </tr>
            </thead>
            <tbody>
                {% for event in recent_events %}
                <tr>
                    <td>{{ event.timestamp }}</td>
                    <td>{{ event.command_type }}</td>
                    <td>{{ event.pump_rpm }}</td>
                    <td>{{ event.valve_opening }}</td>
                    <td>{{ event.predicted_pressure if event.predicted_pressure else "N/A" }}</td>
                    <td>{{ event.decision }}</td>
                </tr>
                {% else %}
                <tr><td colspan="6">No events recorded yet.</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
</body>
</html>
"""


# --------------------------------------------------
# SHARED DASHBOARD RENDERING
# --------------------------------------------------

def render_dashboard(latest=None):
    events = get_events()
    stats = get_statistics(events)

    return render_template_string(
        HTML_PAGE,
        stats=stats,
        recent_events=events[-10:][::-1],
        latest=latest,
        pressure_limit=MAX_SAFE_PRESSURE,
    )


@app.route("/", methods=["GET"])
def home():
    return render_dashboard()


@app.route("/simulate", methods=["POST"])
def simulate():
    command_type = request.form.get("command_type", "").upper()

    if command_type not in {"NORMAL", "SUSPICIOUS", "INVALID"}:
        return "Invalid command type", 400

    latest = process_dashboard_command(command_type)
    return render_dashboard(latest=latest)


# --------------------------------------------------
# PRESSURE MONITORING CHART
# --------------------------------------------------

@app.route("/pressure-chart.png")
def pressure_chart():
    events = get_events()
    readings = parse_pressure_events(events)

    fig, ax = plt.subplots(figsize=(10, 4))

    if readings:
        x_values = list(range(1, len(readings) + 1))
        pressures = [item[1] for item in readings]

        ax.plot(x_values, pressures, marker="o", linewidth=2,
                label="Predicted Pressure")
        unsafe_x = [x for x, value in zip(x_values, pressures)
                    if value > MAX_SAFE_PRESSURE]
        unsafe_y = [value for value in pressures
                    if value > MAX_SAFE_PRESSURE]

        if unsafe_x:
            ax.scatter(unsafe_x, unsafe_y, color="red", s=65,
                       label="Above Safety Limit", zorder=5)
    else:
        ax.text(0.5, 0.5, "No valid pressure readings available",
                ha="center", va="center", transform=ax.transAxes)

    ax.axhline(MAX_SAFE_PRESSURE, color="red", linestyle="--",
               linewidth=2, label=f"Safety Limit ({MAX_SAFE_PRESSURE} bar)")
    ax.set_title("VoltGuard - Industrial Pressure Monitoring")
    ax.set_xlabel("Valid Pressure Reading Number")
    ax.set_ylabel("Predicted Pressure (bar)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    return chart_response(fig)


# --------------------------------------------------
# SECURITY DECISION DISTRIBUTION CHART
# --------------------------------------------------

@app.route("/decision-chart.png")
def decision_chart():
    stats = get_statistics(get_events())
    labels = ["ALLOW", "BLOCK", "INVALID"]
    values = [stats["allowed"], stats["blocked"], stats["invalid"]]
    nonzero = [(label, value) for label, value in zip(labels, values) if value > 0]

    fig, ax = plt.subplots(figsize=(6, 4))

    if not nonzero:
        ax.text(0.5, 0.5, "No command decisions recorded yet",
                ha="center", va="center", transform=ax.transAxes)
    else:
        chart_labels, chart_values = zip(*nonzero)
        ax.pie(chart_values, labels=chart_labels, autopct="%1.1f%%",
               startangle=90)
        ax.axis("equal")

    ax.set_title("Command Decision Distribution")
    return chart_response(fig)


# --------------------------------------------------
# DAILY SECURITY EVENT TREND
# --------------------------------------------------

@app.route("/event-trend.png")
def event_trend_chart():
    events = get_events()
    daily_counts = defaultdict(lambda: {"ALLOW": 0, "BLOCK": 0, "INVALID": 0})

    for event in events:
        timestamp = event.get("timestamp", "")
        decision = event.get("decision", "").upper()

        try:
            event_date = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S").date()
        except (TypeError, ValueError):
            continue

        if decision in daily_counts[event_date.isoformat()]:
            daily_counts[event_date.isoformat()][decision] += 1

    fig, ax = plt.subplots(figsize=(7, 4))

    dates = sorted(daily_counts.keys())
    if not dates:
        ax.text(0.5, 0.5, "No dated security events available",
                ha="center", va="center", transform=ax.transAxes)
    else:
        x_values = list(range(len(dates)))
        for decision, label in [
            ("ALLOW", "Allowed"),
            ("BLOCK", "Blocked"),
            ("INVALID", "Invalid"),
        ]:
            values = [daily_counts[day][decision] for day in dates]
            ax.plot(x_values, values, marker="o", linewidth=2, label=label)

        ax.set_xticks(x_values)
        ax.set_xticklabels(dates, rotation=35, ha="right")
        ax.set_ylabel("Number of Events")
        ax.grid(True, alpha=0.3)
        ax.legend()

    ax.set_title("Daily Security Event Trend")
    ax.set_xlabel("Event Date")
    return chart_response(fig)


# --------------------------------------------------
# START FLASK APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    initialize_logger()
    print("\\n========== VOLTGUARD DASHBOARD ==========\\n")
    app.run(host="127.0.0.1", port=5000, debug=True)

                            
