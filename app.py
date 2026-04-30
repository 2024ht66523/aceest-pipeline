import matplotlib
import matplotlib.pyplot as plt
import io
import base64
from flask import Flask, jsonify, render_template, request

matplotlib.use("Agg")  # ✅ moved AFTER all imports

def create_app():
    app = Flask(__name__)

    clients = []

    programs = {
        "Fat Loss (FL)": {
            "workout": "Back Squat, Cardio, Bench, Deadlift, Recovery",
            "diet": "Egg Whites, Chicken, Fish Curry",
            "color": "#e74c3c",
            "calorie_factor": 22
        },
        "Muscle Gain (MG)": {
            "workout": "Squat, Bench, Deadlift, Press, Rows",
            "diet": "Eggs, Biryani, Mutton Curry",
            "color": "#2ecc71",
            "calorie_factor": 35
        },
        "Beginner (BG)": {
            "workout": "Air Squats, Ring Rows, Push-ups",
            "diet": "Balanced Tamil Meals",
            "color": "#3498db",
            "calorie_factor": 26
        }
    }

    @app.route("/")
    def home():
        return {"message": "Welcome to ACEest Fitness API"}

    @app.route("/programs")
    def get_programs():
        return jsonify(programs)

    @app.route("/programs/<name>")
    def get_program(name):
        if name in programs:
            return jsonify(programs[name])
        return {"error": "Program not found"}, 404

    @app.route("/ui", methods=["GET", "POST"])
    def ui():
        chart = None

        if request.method == "POST":
            name = request.form.get("name")
            age = request.form.get("age")
            weight = float(request.form.get("weight", 0))
            program = request.form.get("program")
            adherence = int(request.form.get("adherence", 0))
            notes = request.form.get("notes")

            if name and program:
                clients.append((name, age, weight, program, adherence, notes))

        # Generate chart
        if clients:
            names = [c[0] for c in clients]
            adherence_vals = [c[4] for c in clients]

            fig, ax = plt.subplots()
            ax.bar(names, adherence_vals)
            ax.set_ylabel("Adherence %")
            ax.set_title("Client Progress")

            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)

            chart = base64.b64encode(buf.getvalue()).decode()

        return render_template(
            "index.html",
            programs=programs,
            clients=clients,
            chart=chart
        )

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)