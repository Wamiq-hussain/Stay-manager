import sqlite3
import click
from flask import Flask, g, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "change-this-secret-key"   # session (login cookie) ko sign karne ke liye
DATABASE = "stay_manager.db"


# ---------- Database helpers ----------
def get_db():
    """Har request ke liye ek database connection."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row            # row["email"] jaise access ke liye
        g.db.execute("PRAGMA foreign_keys = ON")  # SQLite me foreign key ON karna padta hai
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        with open("schema.sql") as f:
            db.executescript(f.read())
        db.commit()


# ---------- Routes ----------
@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form["full_name"].strip()
        email = request.form["email"].strip().lower()
        phone = request.form["phone_number"].strip()
        password = request.form["password"]

        # Validation
        if not full_name or not email or not phone or not password:
            flash("Saari fields bharna zaroori hai.")
        elif len(password) < 6:
            flash("Password kam se kam 6 character ka rakho.")
        elif not phone.isdigit() or len(phone) != 10:
            flash("Phone number 10 digit ka hona chahiye.")
        else:
            db = get_db()
            try:
                # role yahan set nahi hota -> hamesha 'guest' (schema ka default)
                db.execute(
                    "INSERT INTO users (full_name, email, phone_number, password_hash) "
                    "VALUES (?, ?, ?, ?)",
                    (full_name, email, phone, generate_password_hash(password)),
                )
                db.commit()
                flash("Account ban gaya. Ab login karo.")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("Yeh email pehle se registered hai.")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        user = get_db().execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["user_id"]
            session["full_name"] = user["full_name"]
            session["role"] = user["role"]
            return redirect(url_for("dashboard"))
        flash("Email ya password galat hai.")   # jaanbujh kar dono ek hi message
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html")


# ---------- Command line: owner banana ----------
@app.cli.command("make-owner")
@click.argument("email")
def make_owner(email):
    """Kisi registered user ko owner banata hai: flask --app app make-owner email"""
    db = get_db()
    cur = db.execute("UPDATE users SET role = 'owner' WHERE email = ?", (email.lower(),))
    db.commit()
    print("Owner bana diya." if cur.rowcount else "Yeh email nahi mila.")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
