from flask import Flask, render_template_string

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>VoltGuard Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #101827;
            color: white;
            text-align: center;
            padding: 40px;
        }

        h1 {
            color: #00d4ff;
        }

        .card {
            background: #1e293b;
            padding: 25px;
            margin: 20px auto;
            width: 300px;
            border-radius: 12px;
        }
    </style>
</head>

<body>

    <h1>VoltGuard</h1>
    <h2>Physics-Aware ICS/SCADA Intrusion Detection System</h2>

    <div class="card">
        <h3>System Status</h3>
        <h2 style="color: #00ff99;">ONLINE</h2>
    </div>

    <div class="card">
        <h3>Dashboard</h3>
        <p>VoltGuard Flask Application Started Successfully!</p>
    </div>

</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
