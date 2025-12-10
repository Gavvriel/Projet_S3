from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = "dev_key"
DATABASE = "base.db"


# -----------------------------
# Connexion à la base
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

def hash_mdp(mdp: str) -> str:
    return hashlib.sha256(mdp.encode()).hexdigest()


# -----------------------------
# Décorateur login_required
# -----------------------------
from functools import wraps

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


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
            return redirect(url_for("home"))
        else:
            error = "Identifiants incorrects"

    return render_template("login.html", error=error)


@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role", "user")

        if not username or not password:
            error = "Veuillez remplir tous les champs."
        else:
            db = get_db()
            existing = db.execute(
                "SELECT id FROM utilisateurs WHERE username = ?",
                (username,)
            ).fetchone()

            if existing:
                error = "Ce nom d'utilisateur existe déjà."
            else:
                db.execute(
                    "INSERT INTO utilisateurs (username, password, role) VALUES (?, ?, ?)",
                    (username, hash_mdp(password), role)
                )
                db.commit()
                session["username"] = username
                session["role"] = role
                return redirect(url_for("home"))

    return render_template("register.html", error=error)


@app.route("/annonces")
def annonces():
    """Liste toutes les annonces."""
    db = get_db()
    rows = db.execute("""
        SELECT a.id, a.titre, a.description, a.ville, a.loyer,
               a.date_creation, u.username AS auteur
        FROM annonces a
        JOIN utilisateurs u ON a.auteur_id = u.id
        ORDER BY a.date_creation DESC
    """).fetchall()

    return render_template("annonces.html", annonces=rows)


@app.route("/creer_annonce", methods=["GET", "POST"])
@login_required
def creer_annonce():
    error = None

    if request.method == "POST":
        titre = request.form.get("titre")
        description = request.form.get("description")
        ville = request.form.get("ville")
        loyer = request.form.get("loyer")

        if not titre or not description:
            error = "Titre et description sont obligatoires."
        else:
            db = get_db()
            # On récupère l'id de l'auteur à partir du username en session
            user = db.execute(
                "SELECT id FROM utilisateurs WHERE username = ?",
                (session["username"],)
            ).fetchone()

            db.execute("""
                INSERT INTO annonces (titre, description, ville, loyer, auteur_id)
                VALUES (?, ?, ?, ?, ?)
            """, (titre, description, ville, loyer or None, user["id"]))
            db.commit()
            return redirect(url_for("annonces"))

    return render_template("creer_annonce.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
