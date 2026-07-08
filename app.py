from flask import Flask, render_template, request, redirect, flash, Response
import sqlite3
import csv
import io

app = Flask(__name__)
app.secret_key = "mysecretkey"


# Create database and table
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        age INTEGER
    )
    """)

    conn.commit()
    conn.close()


init_db()


# Home page
@app.route("/", methods=["GET", "POST"])
def home():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        age = request.form["age"]

        # Duplicate email check
        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            flash("Email already exists!")
        else:
            cursor.execute(
                "INSERT INTO users(name, email, age) VALUES (?, ?, ?)",
                (name, email, age)
            )

            conn.commit()
            flash("User added successfully!")

    # Search functionality
    search = request.args.get("search")

    if search:
        cursor.execute(
            """
            SELECT * FROM users
            WHERE name LIKE ? OR email LIKE ?
            """,
            (f"%{search}%", f"%{search}%")
        )
    else:
        cursor.execute("SELECT * FROM users")

    users = cursor.fetchall()

    conn.close()

    return render_template("index.html", users=users)


# Delete user
@app.route("/delete/<int:id>")
def delete(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM users WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    flash("User deleted successfully!")

    return redirect("/")


# Edit user
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        age = request.form["age"]

        cursor.execute(
            """
            UPDATE users
            SET name=?, email=?, age=?
            WHERE id=?
            """,
            (name, email, age, id)
        )

        conn.commit()
        conn.close()

        flash("User updated successfully!")

        return redirect("/")

    cursor.execute(
        "SELECT * FROM users WHERE id=?",
        (id,)
    )

    user = cursor.fetchone()

    conn.close()

    return render_template("edit.html", user=user)


# Export CSV
@app.route("/export")
def export():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["ID", "Name", "Email", "Age"])

    for user in users:
        writer.writerow(user)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=users.csv"
        }
    )


# Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)