import sqlite3
import hashlib

conn = sqlite3.connect("base.db")
cursor = conn.cursor()

# Supprime la table si elle existe déjà
cursor.execute("DROP TABLE IF EXISTS utilisateurs")

# Création de la table
cursor.execute("""
CREATE TABLE utilisateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")

def hash_mdp(mdp):
    return hashlib.sha256(mdp.encode()).hexdigest()

# Ajout admin
cursor.execute("""
INSERT INTO utilisateurs (username, password, role)
VALUES (?, ?, ?)
""", ("admin", hash_mdp("admin123"), "admin"))

# Ajout user
cursor.execute("""
INSERT INTO utilisateurs (username, password, role)
VALUES (?, ?, ?)
""", ("test", hash_mdp("1234"), "user"))

conn.commit()
conn.close()

print("Base créée !")
print("Admin : admin / admin123")
print("User  : test / 1234")
