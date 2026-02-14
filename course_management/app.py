from flask import Flask, render_template, redirect, url_for, request, session, jsonify
import pymysql
from config import config
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(config)
app.secret_key = app.config['SECRET_KEY']


def get_db_connection():
    return pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DATABASE'],
        port=app.config['MYSQL_PORT']
    )


# ---------------- HOME ----------------

@app.route("/")
def home():
    return redirect(url_for("login"))



# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT id FROM users WHERE username=%s", (u,))
        if cur.fetchone():
            cur.close()
            conn.close()
            return render_template("register.html", msg="User already exists!")

        hashed_password = generate_password_hash(p)

        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (u, hashed_password)
        )
        conn.commit()

        cur.close()
        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT username, password FROM users WHERE username=%s", (u,))
        user_record = cur.fetchone()
        cur.close()
        conn.close()

        if user_record and check_password_hash(user_record[1], p):
            session["user"] = u
            return redirect(url_for("dashboard"))

        return render_template("login.html", msg="Invalid credentials")

    return render_template("login.html")



# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM courses WHERE created_by=%s", (session["user"],))
    courses = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("dashboard.html", user=session["user"], courses=courses)


# ---------------- ADD COURSE ----------------

@app.route("/add_course", methods=["POST"])
def add_course():
    if "user" not in session:
        return redirect(url_for("login"))

    title = request.form["title"]
    description = request.form["description"]

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO courses (title, description, created_by) VALUES (%s, %s, %s)",
        (title, description, session["user"])
    )
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("dashboard"))


# ---------------- DELETE COURSE ----------------

@app.route("/delete_course/<int:course_id>")
def delete_course(course_id):
    if "user" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM courses WHERE id=%s", (course_id,))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("dashboard"))


# ---------------- ENROLL STUDENT ----------------

@app.route("/enroll/<int:course_id>", methods=["POST"])
def enroll(course_id):
    if "user" not in session:
        return redirect(url_for("login"))

    student_name = request.form["student_name"]

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO enrollments (student_name, course_id) VALUES (%s, %s)",
        (student_name, course_id)
    )
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("dashboard"))


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
