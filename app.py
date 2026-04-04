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

    # ---------- DB INIT ----------
    def init_db():
        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        # Clients
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

        # Progress
        cur.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            week TEXT,
            adherence INTEGER
        )
        """)

        # Metrics
        cur.execute("""
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            date TEXT,
            weight REAL
        )
        """)

        conn.commit()
        conn.close()

    init_db()

    # ---------- PROGRAMS ----------
    programs = {
        "Fat Loss (FL)": 22,
        "Muscle Gain (MG)": 35,
        "Beginner (BG)": 26
    }

    # ---------- ROUTE ----------
    @app.route("/", methods=["GET", "POST"])
    def home():
        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        summary = ""
        chart = None

        if request.method == "POST":
            action = request.form.get("action")
            name = request.form.get("name")

            # ---------- SAVE CLIENT ----------
            if action == "save_client":
                try:
                    age = request.form.get("age")
                    height = request.form.get("height")
                    weight = float(request.form.get("weight", 0))
                    program = request.form.get("program")

                    if program not in programs:
                        raise ValueError("Invalid program")

                    calories = int(weight * programs[program])

                    cur.execute("""
                    INSERT OR REPLACE INTO clients
                    (name, age, height, weight, program, calories, target_weight, target_adherence)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        name,
                        age if age else None,
                        height if height else None,
                        weight,
                        program,
                        calories,
                        request.form.get("target_weight") or None,
                        request.form.get("target_adherence") or None
                    ))

                    conn.commit()

                except Exception as e:
                    print("Error saving client:", e)

            # ---------- LOAD CLIENT ----------
            elif action == "load_client":
                cur.execute("SELECT * FROM clients WHERE name=?", (name,))
                row = cur.fetchone()

                if row:
                    summary = f"""
CLIENT PROFILE
--------------
Name       : {row[1]}
Age        : {row[2]}
Height     : {row[3]} cm
Weight     : {row[4]} kg
Program    : {row[5]}
Calories   : {row[6]} kcal/day
Target Wt  : {row[7]}
Target Adh : {row[8]}
"""

            # ---------- SAVE PROGRESS ----------
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

            # ---------- SAVE METRICS ----------
            elif action == "save_metrics":
                cur.execute("""
                INSERT INTO metrics (client_name, date, weight)
                VALUES (?, ?, ?)
                """, (
                    name,
                    datetime.now().strftime("%Y-%m-%d"),
                    float(request.form.get("weight", 0))
                ))
                conn.commit()

            # ---------- SHOW CHART ----------
            elif action == "show_chart":
                cur.execute("""
                SELECT week, adherence
                FROM progress
                WHERE client_name=?
                ORDER BY id
                """, (name,))
                data = cur.fetchall()

                if data:
                    weeks = [d[0] for d in data]
                    adherence_vals = [d[1] for d in data]

                    fig, ax = plt.subplots()
                    ax.plot(weeks, adherence_vals, marker="o")
                    ax.set_title(f"Adherence - {name}")
                    ax.set_ylabel("Adherence %")
                    plt.xticks(rotation=45)

                    buf = io.BytesIO()
                    plt.savefig(buf, format="png")
                    buf.seek(0)

                    chart = base64.b64encode(buf.getvalue()).decode()

        conn.close()

        return render_template(
            "index.html",
            programs=programs,
            summary=summary,
            chart=chart
        )

    return app


# ---------- RUN ----------
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)