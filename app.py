import matplotlib
import matplotlib.pyplot as plt
import io
import base64
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request

matplotlib.use("Agg")


DB_NAME = "aceest.db"


def create_app(test_db=None):
    app = Flask(__name__)
    DB = test_db if test_db else DB_NAME

    def init_db():
        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        if test_db:
            cur.execute("DROP TABLE IF EXISTS clients")
            cur.execute("DROP TABLE IF EXISTS progress")
            cur.execute("DROP TABLE IF EXISTS metrics")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            age INTEGER,
            height REAL,
            weight REAL,
            program TEXT,
            calories INTEGER,
            target_weight REAL,
            target_adherence INTEGER
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            week TEXT,
            adherence INTEGER
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            date TEXT,
            weight REAL,
            waist REAL,
            bodyfat REAL
        )
        """)

        conn.commit()
        conn.close()

    init_db()

    programs = {
        "Fat Loss (FL) – 3 day": 22,
        "Fat Loss (FL) – 5 day": 24,
        "Muscle Gain (MG) – PPL": 35,
        "Beginner (BG)": 26,
    }

    @app.route("/", methods=["GET", "POST"])
    def home():
        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        summary = ""
        chart = ""

        if request.method == "POST":
            action = request.form.get("action")
            name = request.form.get("name")

            # SAVE CLIENT
            if action == "save_client":
                weight = float(request.form.get("weight", 0))
                program = request.form.get("program")

                calories = int(weight * programs.get(program, 1))

                cur.execute("""
                INSERT OR REPLACE INTO clients
                (name, age, height, weight, program, calories, target_weight, target_adherence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    name,
                    request.form.get("age"),
                    request.form.get("height"),
                    weight,
                    program,
                    calories,
                    request.form.get("target_weight"),
                    request.form.get("target_adherence")
                ))
                conn.commit()

            # LOAD CLIENT
            elif action == "load_client":
                if not name:
                    summary = "⚠️ Please select a client"
                else:
                    cur.execute("SELECT * FROM clients WHERE name=?", (name,))
                    row = cur.fetchone()

                    if row:
                        summary = f"""
CLIENT PROFILE
--------------
Name: {row[1]}
Weight: {row[4]}
Program: {row[5]}
Calories: {row[6]}
"""

            # SAVE PROGRESS
            elif action == "save_progress":
                cur.execute("""
                INSERT INTO progress (client_name, week, adherence)
                VALUES (?, ?, ?)
                """, (
                    name,
                    datetime.now().strftime("Week %U - %Y"),
                    int(request.form.get("adherence", 0))
                ))
                conn.commit()

            # SAVE METRICS
            elif action == "save_metrics":
                cur.execute("""
                INSERT INTO metrics (client_name, date, weight, waist, bodyfat)
                VALUES (?, ?, ?, ?, ?)
                """, (
                    name,
                    datetime.now().strftime("%Y-%m-%d"),
                    float(request.form.get("weight", 0)),
                    float(request.form.get("waist", 0)),
                    float(request.form.get("bodyfat", 0))
                ))
                conn.commit()

            # SHOW CHART
            elif action == "show_chart":
                cur.execute("""
                SELECT week, adherence FROM progress
                WHERE client_name=? ORDER BY id
                """, (name,))
                data = cur.fetchall()

                if data:
                    x = [d[0] for d in data]
                    y = [d[1] for d in data]

                    fig, ax = plt.subplots()
                    ax.plot(x, y, marker="o")

                    buf = io.BytesIO()
                    plt.savefig(buf, format="png")
                    buf.seek(0)

                    chart = base64.b64encode(buf.getvalue()).decode()

        # 🔥 FETCH CLIENT LIST
        cur.execute("SELECT name FROM clients ORDER BY name")
        clients = [row[0] for row in cur.fetchall()]

        conn.close()

        return render_template(
            "index.html",
            programs=programs,
            summary=summary,
            chart=chart,
            clients=clients
        )

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)