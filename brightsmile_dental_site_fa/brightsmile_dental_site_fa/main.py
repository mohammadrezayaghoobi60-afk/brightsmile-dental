from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import date
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "change-this-demo-secret-key"
DB_PATH = Path(__file__).with_name("clinic.db")

SERVICES = [
    ("checkup", "معاینه دندان"),
    ("cleaning", "جرم‌گیری و پاک‌سازی"),
    ("filling", "ترمیم و پرکردن دندان"),
    ("orthodontics", "ارتودنسی"),
    ("whitening", "سفید کردن دندان"),
    ("implants", "ایمپلنت دندان"),
    ("root-canal", "مشاوره درمان ریشه"),
]

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL,
                service TEXT NOT NULL,
                appointment_date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

@app.route("/")
def home():
    return render_template("index.html", services=SERVICES)

@app.route("/services")
def services():
    return render_template("services.html", services=SERVICES)

@app.route("/team")
def team():
    doctors = [
        ("دکتر الکس مورگان", "دندان‌پزشک عمومی", "ارائه‌دهنده مراقبت‌های پیشگیرانه و راهنمایی بیماران."),
        ("دکتر مایا چن", "متخصص ارتودنسی", "ارائه مشاوره ارتودنسی و برنامه‌ریزی درمان."),
        ("دکتر سمیر پاتل", "دندان‌پزشک ترمیمی", "کمک به بیماران برای شناخت گزینه‌های درمانی ترمیمی."),
    ]
    return render_template("team.html", doctors=doctors)

@app.route("/appointments", methods=["GET", "POST"])
def appointments():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip()
        service_key = request.form.get("service", "").strip()
        appointment_date = request.form.get("appointment_date", "").strip()
        service_names = dict(SERVICES)

        if not full_name or not email or service_key not in service_names or not appointment_date:
            flash("لطفاً همه فیلدها را به‌درستی تکمیل کنید.", "error")
            return redirect(url_for("appointments"))

        try:
            chosen_date = date.fromisoformat(appointment_date)
        except ValueError:
            flash("لطفاً یک تاریخ معتبر انتخاب کنید.", "error")
            return redirect(url_for("appointments"))

        if chosen_date < date.today():
            flash("لطفاً امروز یا یک تاریخ در آینده را انتخاب کنید.", "error")
            return redirect(url_for("appointments"))

        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                """INSERT INTO appointments
                   (full_name, email, service, appointment_date)
                   VALUES (?, ?, ?, ?)""",
                (full_name, email, service_names[service_key], appointment_date)
            )

        return render_template("success.html", full_name=full_name)

    return render_template("appointments.html", services=SERVICES, today=date.today().isoformat())

@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404

init_db()

if __name__ == "__main__":
    app.run(debug=True)
