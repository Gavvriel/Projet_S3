import sqlite3
import hashlib

DB_NAME = "base.db"

def hash_mdp(mdp):
    return hashlib.sha256(mdp.encode()).hexdigest()

conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

# Activer les clés étrangères (utile pour les relations)
cur.execute("PRAGMA foreign_keys = ON;")

# On repart propre
cur.execute("DROP TABLE IF EXISTS annonces;")
cur.execute("DROP TABLE IF EXISTS utilisateurs;")

# Table utilisateurs
cur.execute("""
CREATE TABLE utilisateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

# Table annonces
cur.execute("""
CREATE TABLE annonces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre TEXT NOT NULL,
    description TEXT NOT NULL,
    ville TEXT,
    loyer REAL,
    auteur_id INTEGER NOT NULL,
    date_creation TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(auteur_id) REFERENCES utilisateurs(id)
)
""")

# Utilisateurs de test
cur.execute(
    "INSERT INTO utilisateurs (username, password, role) VALUES (?, ?, ?)",
    ("admin", hash_mdp("admin123"), "admin")
)
cur.execute(
    "INSERT INTO utilisateurs (username, password, role) VALUES (?, ?, ?)",
    ("test", hash_mdp("1234"), "user")
)

# On récupère l'id de "test" pour lui attribuer des annonces
cur.execute("SELECT id FROM utilisateurs WHERE username = ?", ("test",))
row = cur.fetchone()
test_id = row[0]

# Quelques annonces de démo
cur.execute("""
INSERT INTO annonces (titre, description, ville, loyer, auteur_id)
VALUES (?, ?, ?, ?, ?)
""", ("Colocation proche université", "Grande chambre dans appart 3 pièces.", "Nanterre", 550, test_id))

cur.execute("""
INSERT INTO annonces (titre, description, ville, loyer, auteur_id)
VALUES (?, ?, ?, ?, ?)
""", ("Chambre à louer à Paris", "Coloc calme, métro ligne 1.", "Paris", 700, test_id))

conn.commit()
conn.close()

print("Base recréée avec utilisateurs + annonces.")
print("Admin : admin / admin123")
print("User  : test / 1234")
