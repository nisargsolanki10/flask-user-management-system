from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


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


# Home page - Add and Display data
@app.route("/", methods=["GET", "POST"])
def home():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        age = request.form["age"]

        cursor.execute(
            "INSERT INTO users(name, email, age) VALUES (?, ?, ?)",
            (name, email, age)
        )

        conn.commit()

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

    return redirect("/")


# Edit/Update user
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        age = request.form["age"]

        cursor.execute(
            "UPDATE users SET name=?, email=?, age=? WHERE id=?",
            (name, email, age, id)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    cursor.execute(
        "SELECT * FROM users WHERE id=?",
        (id,)
    )

    user = cursor.fetchone()

    conn.close()

    return render_template("edit.html", user=user)


# Run Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)