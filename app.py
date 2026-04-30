import sqlite3
import random
from flask import Flask, render_template, request, redirect, session
from fpdf import FPDF
from datetime import date

DB_NAME = "aceest.db"


def create_app(test_db=None):
    app = Flask(__name__)
    app.secret_key = "secret123"

    DB = test_db if test_db else DB_NAME

    # ---------- DB ----------
    def init_db():
        conn = sqlite3.connect(DB)
        cur = conn.cursor()

        if test_db:
            cur.execute("DROP TABLE IF EXISTS users")
            cur.execute("DROP TABLE IF EXISTS clients")
            cur.execute("DROP TABLE IF EXISTS workouts")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            role TEXT
        )
        """)

        cur.execute("""
        INSERT OR IGNORE INTO users VALUES ('admin','admin','Admin')
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            program TEXT,
            membership_status TEXT,
            membership_end TEXT
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            date TEXT,
            workout_type TEXT,
            duration_min INTEGER,
            notes TEXT
        )
        """)

        conn.commit()
        conn.close()

    init_db()

    program_templates = {
        "Fat Loss": ["HIIT", "Circuit", "Cardio + Weights"],
        "Muscle Gain": ["Push/Pull/Legs", "Upper/Lower", "Strength"],
        "Beginner": ["Full Body", "Mobility"]
    }

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

        message = ""
        program = ""
        workouts = []

        new_name = request.form.get("new_name")
        selected = request.form.get("selected_client")
        name = selected if selected else new_name

        if request.method == "POST" and name:

            action = request.form.get("action")

            # SAVE CLIENT
            if action == "save_client":
                cur.execute("""
                INSERT OR IGNORE INTO clients (name, membership_status)
                VALUES (?, ?)
                """, (name, "Active"))
                conn.commit()
                message = f"Client {name} saved"

            # LOAD CLIENT
            elif action == "load_client":
                cur.execute("SELECT program FROM clients WHERE name=?", (name,))
                row = cur.fetchone()
                if row:
                    program = row[0] or ""

            # GENERATE PROGRAM
            elif action == "generate_program":
                ptype = random.choice(list(program_templates.keys()))
                pvalue = random.choice(program_templates[ptype])
                cur.execute("UPDATE clients SET program=? WHERE name=?", (pvalue, name))
                conn.commit()
                program = pvalue
                message = f"Program: {pvalue}"

            # ADD WORKOUT
            elif action == "add_workout":
                cur.execute("""
                INSERT INTO workouts (client_name, date, workout_type, duration_min, notes)
                VALUES (?, ?, ?, ?, ?)
                """, (
                    name,
                    request.form.get("date") or date.today().isoformat(),
                    request.form.get("type"),
                    request.form.get("duration"),
                    request.form.get("notes")
                ))
                conn.commit()

            # EXPORT PDF
            elif action == "export_pdf":
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt=f"Report: {name}", ln=True)
                pdf.output(f"{name}.pdf")

        # FETCH DATA
        cur.execute("SELECT name FROM clients")
        clients = [c[0] for c in cur.fetchall()]

        if name:
            cur.execute("SELECT date, workout_type, duration_min FROM workouts WHERE client_name=?", (name,))
            workouts = cur.fetchall()

        conn.close()

        return render_template(
            "index.html",
            clients=clients,
            program=program,
            workouts=workouts,
            message=message
        )

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)