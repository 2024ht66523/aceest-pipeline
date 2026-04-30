import matplotlib
import matplotlib.pyplot as plt
import io
import base64
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request

matplotlib.use("Agg")
DB_NAME = "aceest.db"

def create_app():
    app = Flask(__name__)

    # ---------- DB ----------
    def init_db():
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                age INTEGER,
                weight REAL,
                program TEXT,
                calories INTEGER
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

        conn.commit()
        conn.close()

    init_db()

    # ---------- PROGRAMS ----------
    programs = {
        "Fat Loss (FL)": 22,
        "Muscle Gain (MG)": 35,
        "Beginner (BG)": 26
    }

    # ---------- HOME ----------
    @app.route("/", methods=["GET", "POST"])
    def home():
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        summary = ""
        chart = None

        # SAVE CLIENT
        if request.method == "POST" and request.form.get("action") == "save_client":
            name = request.form.get("name")
            age = request.form.get("age", 0)
            weight = float(request.form.get("weight", 0))
            program = request.form.get("program")

            calories = int(weight * programs[program])

            cur.execute("""
                INSERT OR REPLACE INTO clients (name, age, weight, program, calories)
                VALUES (?, ?, ?, ?, ?)
            """, (name, age, weight, program, calories))
            conn.commit()

        # LOAD CLIENT
        if request.method == "POST" and request.form.get("action") == "load_client":
            name = request.form.get("name")

            cur.execute("SELECT * FROM clients WHERE name=?", (name,))
            row = cur.fetchone()

            if row:
                _, name, age, weight, program, calories = row
                summary = f"""
                CLIENT PROFILE
                --------------
                Name     : {name}
                Age      : {age}
                Weight   : {weight} kg
                Program  : {program}
                Calories : {calories} kcal/day
                """

        # SAVE PROGRESS
        if request.method == "POST" and request.form.get("action") == "save_progress":
            name = request.form.get("name")
            adherence = int(request.form.get("adherence", 0))
            week = datetime.now().strftime("Week %U - %Y")

            cur.execute("""
                INSERT INTO progress (client_name, week, adherence)
                VALUES (?, ?, ?)
            """, (name, week, adherence))
            conn.commit()

        # FETCH PROGRESS FOR CHART
        cur.execute("SELECT client_name, adherence FROM progress")
        data = cur.fetchall()

        if data:
            names = [d[0] for d in data]
            adherence_vals = [d[1] for d in data]

            fig, ax = plt.subplots()
            ax.bar(names, adherence_vals)
            ax.set_ylabel("Adherence %")

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


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)