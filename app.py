import sqlite3
import random
from flask import Flask, render_template, request, redirect, session
from fpdf import FPDF


DB_NAME = "aceest.db"


def create_app(test_db=None):
    app = Flask(__name__)
    app.secret_key = "secret123"

    DB = test_db if test_db else DB_NAME

    def init_db():
        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        if test_db:
            cur.execute("DROP TABLE IF EXISTS users")
            cur.execute("DROP TABLE IF EXISTS clients")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
        """)

        cur.execute("""
        INSERT OR IGNORE INTO users (username,password,role)
        VALUES ('admin','admin','Admin')
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            age INTEGER,
            height REAL,
            weight REAL,
            program TEXT,
            calories INTEGER,
            membership_expiry TEXT
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

    # ---------- HELPERS ----------
    def safe_float(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return 0.0

    # ---------- LOGIN ----------
    @app.route("/", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            conn = sqlite3.connect(DB)
            cur = conn.cursor()
            cur.execute("SELECT role FROM users WHERE username=? AND password=?",
                        (username, password))
            row = cur.fetchone()
            conn.close()

            if row:
                session["user"] = username
                return redirect("/dashboard")

        return render_template("login.html")

    # ---------- DASHBOARD ----------
    @app.route("/dashboard", methods=["GET", "POST"])
    def dashboard():
        if "user" not in session:
            return redirect("/")

        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        summary = ""
        ai_program = []

        if request.method == "POST":
            action = request.form.get("action")

            new_name = request.form.get("new_name")
            selected = request.form.get("selected_client")
            name = selected if selected else new_name

            if not name:
                summary = "⚠️ Please enter or select a client"
            else:

                if action == "save_client":
                    weight = safe_float(request.form.get("weight"))
                    program = request.form.get("program")
                    calories = int(weight * programs.get(program, 1))

                    cur.execute("""
                    INSERT OR REPLACE INTO clients
                    (name, age, height, weight, program, calories, membership_expiry)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        name,
                        request.form.get("age"),
                        request.form.get("height"),
                        weight,
                        program,
                        calories,
                        request.form.get("membership")
                    ))
                    conn.commit()

                elif action == "load_client":
                    cur.execute("SELECT * FROM clients WHERE name=?", (name,))
                    row = cur.fetchone()
                    if row:
                        summary = f"""
Name: {row[1]}
Weight: {row[4]}
Program: {row[5]}
Calories: {row[6]}
"""

                elif action == "generate_ai":
                    exercises = ["Squat", "Bench", "Deadlift", "Row", "Pullup"]
                    for i in range(3):
                        ai_program.append({
                            "day": f"Day {i + 1}",
                            "exercise": random.choice(exercises),
                            "sets": random.randint(3, 5),
                            "reps": random.randint(8, 12)
                        })

                elif action == "export_pdf":
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    pdf.cell(200, 10, txt=f"Report: {name}", ln=True)
                    pdf.output(f"{name}.pdf")

        cur.execute("SELECT name FROM clients")
        clients = [c[0] for c in cur.fetchall()]

        conn.close()

        return render_template(
            "index.html",
            programs=programs,
            clients=clients,
            summary=summary,
            ai_program=ai_program
        )

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)