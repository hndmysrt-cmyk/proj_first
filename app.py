from __future__ import annotations

from datetime import datetime
from typing import Any

from flask import Flask, redirect, render_template, request, session, url_for


def predict_consumption(
    date_text: str,
    temperature: float,
    working_day: bool,
    devices: int,
) -> dict[str, Any]:
    """Return a stable demonstration prediction for the submitted inputs."""
    date_value = datetime.strptime(date_text, "%Y-%m-%d").date()
    weekday_load = 4.8 if working_day else 2.1
    temperature_load = max(temperature - 18, 0) * 0.55
    device_load = devices * 1.35
    seasonal_load = (date_value.month % 6) * 0.7
    weekend_adjustment = 1.5 if date_value.weekday() >= 5 else 0

    prediction = round(
        8.5 + weekday_load + temperature_load + device_load + seasonal_load + weekend_adjustment,
        2,
    )
    mae = round(max(prediction * 0.075, 1.2), 2)

    chart = [
        round(prediction * 0.72, 2),
        round(prediction * 0.86, 2),
        round(prediction * 0.94, 2),
        prediction,
    ]

    return {
        "prediction": prediction,
        "mae": mae,
        "chart": chart,
        "date": date_text,
        "temperature": temperature,
        "working_day": working_day,
        "devices": devices,
    }


def create_app(config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__, template_folder=".", static_folder="static")
    app.config.update(
        SECRET_KEY="dev-secret-change-before-production",
    )

    if config:
        app.config.update(config)

    @app.get("/")
    def home():
        return render_template("index.html")

    @app.get("/index.html")
    def home_alias():
        return home()

    @app.get("/sc1.html")
    def sc1_alias():
        return home()

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "").strip()

            if not username or "@" not in email or len(password) < 6:
                return (
                    render_template(
                        "sc2.html",
                        error="أدخل اسم المستخدم وبريدا إلكترونيا صحيحا وكلمة مرور من 6 أحرف على الأقل.",
                    ),
                    400,
                )

            session["user"] = {"username": username, "email": email}
            return redirect(url_for("predict"))

        return render_template("sc2.html")

    @app.route("/sc2.html", methods=["GET", "POST"])
    def login_alias():
        return login()

    @app.get("/predict")
    def predict():
        if "user" not in session:
            return redirect(url_for("login"))

        return render_template("sc3.html", user=session["user"])

    @app.get("/sc3.html")
    def predict_alias():
        return predict()

    @app.post("/training")
    def training():
        if "user" not in session:
            return redirect(url_for("login"))

        form_data = {
            "date": request.form.get("date", ""),
            "temperature": request.form.get("temperature", ""),
            "working_day": request.form.get("working_day", ""),
            "devices": request.form.get("devices", ""),
        }
        return render_template("sc4.html", user_data=form_data)

    @app.get("/training")
    def training_page():
        if "user" not in session:
            return redirect(url_for("login"))

        return redirect(url_for("predict"))

    @app.get("/sc4.html")
    def training_alias():
        return training_page()

    @app.route("/preprocess", methods=["POST"])
    def preprocess():
        if "user" not in session:
            return redirect(url_for("login"))

        try:
            date_text = request.form["date"]
            temperature = float(request.form["temperature"])
            working_day = request.form["working_day"] == "1"
            devices = int(request.form["devices"])
            datetime.strptime(date_text, "%Y-%m-%d")

            if devices <= 0:
                raise ValueError("devices must be positive")
        except (KeyError, ValueError):
            return (
                render_template(
                    "sc3.html",
                    user=session["user"],
                    error="أدخل قيما صحيحة للتاريخ ودرجة الحرارة وعدد الأجهزة.",
                ),
                400,
            )

        result = predict_consumption(date_text, temperature, working_day, devices)
        session["last_result"] = result
        return render_template("sc5.html", result=result, user=session["user"])

    @app.get("/result")
    @app.get("/sc5.html")
    def result_page():
        if "user" not in session:
            return redirect(url_for("login"))

        result = session.get("last_result")
        if not result:
            return redirect(url_for("predict"))

        return render_template("sc5.html", result=result, user=session["user"])

    @app.get("/logout")
    def logout():
        session.clear()
        return redirect(url_for("home"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
