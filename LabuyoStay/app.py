
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "labuyostay_secret_key"

DATABASE = "labuyostay.db"


# Connect to database
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# Create database tables
def initialize_database():
    conn = get_db()

    sql_file = Path("database.sql")
    conn.executescript(sql_file.read_text(encoding="utf-8"))

    # Sample boarding houses
    count = conn.execute(
        "SELECT COUNT(*) FROM boarding_houses"
    ).fetchone()[0]

    if count == 0:
        conn.execute("""
            INSERT INTO boarding_houses
            (name, address, price, capacity, description)
            VALUES (?, ?, ?, ?, ?)
        """, (
            "Rose Boarding House",
            "Poblacion, Philippines",
            2500,
            4,
            "Affordable boarding house with WiFi."
        ))

        conn.execute("""
            INSERT INTO boarding_houses
            (name, address, price, capacity, description)
            VALUES (?, ?, ?, ?, ?)
        """, (
            "Green Dormitory",
            "Town Center, Philippines",
            3000,
            2,
            "Comfortable rooms with clean facilities."
        ))

    conn.commit()
    conn.close()


# Homepage
@app.route("/")
def index():
    conn = get_db()

    houses = conn.execute("""
        SELECT * FROM boarding_houses
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template("index.html", houses=houses)


# Add boarding house
@app.route("/add-house", methods=["POST"])
def add_house():
    name = request.form.get("name", "").strip()
    address = request.form.get("address", "").strip()
    description = request.form.get("description", "").strip()

    try:
        price = float(request.form.get("price", ""))
        capacity = int(request.form.get("capacity", ""))
    except ValueError:
        flash("Please enter valid price and capacity.")
        return redirect(url_for("index"))

    if not name or not address or price <= 0 or capacity <= 0:
        flash("Please complete all required fields correctly.")
        return redirect(url_for("index"))

    conn = get_db()

    conn.execute("""
        INSERT INTO boarding_houses
        (name, address, price, capacity, description)
        VALUES (?, ?, ?, ?, ?)
    """, (name, address, price, capacity, description))

    conn.commit()
    conn.close()

    flash("Boarding house successfully added!")
    return redirect(url_for("index"))


# Reservation page
@app.route("/reserve/<int:house_id>")
def reserve(house_id):
    conn = get_db()

    house = conn.execute("""
        SELECT * FROM boarding_houses
        WHERE id = ?
    """, (house_id,)).fetchone()

    conn.close()

    if house is None:
        return "Boarding house not found", 404

    return render_template("reserve.html", house=house)


# Submit reservation
@app.route("/submit-reservation/<int:house_id>",
           methods=["POST"])
def submit_reservation(house_id):

    tenant_name = request.form.get("tenant_name", "").strip()
    contact = request.form.get("contact", "").strip()
    reservation_date = request.form.get(
        "reservation_date", ""
    ).strip()

    if not tenant_name or not contact or not reservation_date:
        flash("Please complete all reservation fields.")
        return redirect(url_for("reserve", house_id=house_id))

    conn = get_db()

    house = conn.execute("""
        SELECT * FROM boarding_houses
        WHERE id = ?
    """, (house_id,)).fetchone()

    if house is None:
        conn.close()
        return "Boarding house not found", 404

    if house["status"] != "Available":
        conn.close()
        flash("This boarding house is currently unavailable.")
        return redirect(url_for("index"))

    conn.execute("""
        INSERT INTO reservations
        (tenant_name, contact, boarding_house_id, reservation_date)
        VALUES (?, ?, ?, ?)
    """, (tenant_name, contact, house_id, reservation_date))

    conn.commit()
    conn.close()

    flash("Reservation submitted successfully!")
    return redirect(url_for("reservations"))


# View reservations
@app.route("/reservations")
def reservations():
    conn = get_db()

    records = conn.execute("""
        SELECT
            reservations.*,
            boarding_houses.name AS house_name
        FROM reservations
        JOIN boarding_houses
        ON reservations.boarding_house_id = boarding_houses.id
        ORDER BY reservations.id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "reservations.html",
        records=records
    )


# Update reservation status
@app.route("/update-status/<int:reservation_id>",
           methods=["POST"])
def update_status(reservation_id):

    status = request.form.get("status")

    if status not in ["Pending", "Approved", "Rejected"]:
        flash("Invalid reservation status.")
        return redirect(url_for("reservations"))

    conn = get_db()

    conn.execute("""
        UPDATE reservations
        SET status = ?
        WHERE id = ?
    """, (status, reservation_id))

    conn.commit()
    conn.close()

    flash("Reservation status updated!")
    return redirect(url_for("reservations"))


if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)
