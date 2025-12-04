from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = "dev_key"

DATABASE = "base.db"

# -----------------------------
# Connexion à SQLite
# -----------------------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def hash_mdp(mdp):
    return hashlib.sha256(mdp.encode()).hexdigest()

# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        db = get_db()
        user = db.execute(
            "SELECT * FROM utilisateurs WHERE username = ?",
            (username,)
        ).fetchone()

        if user and user["password"] == hash_mdp(password):
            session["username"] = user["username"]
            session["role"] = user["role"]

            if user["role"] == "admin":
                return redirect(url_for("panel_admin"))
            else:
                return redirect(url_for("annonces"))
        else:
            error = "Identifiants incorrects"

    return render_template("login.html", error=error)

@app.route("/panel_admin")
def panel_admin():
    if session.get("role") != "admin":
        return redirect(url_for("home"))
    return render_template("panel_admin.html", username=session.get("username"))

@app.route("/annonces")
def annonces():
    if session.get("role") != "user":
        return redirect(url_for("home"))
    return render_template("Annonces.html", username=session.get("username"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
