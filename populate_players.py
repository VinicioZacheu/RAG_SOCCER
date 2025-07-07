import sqlite3
import os

# === populate_players.py ===

# Connect to the SQLite database
db_path = os.path.join("data", "db.sqlite3")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Ensure the group 'Biolab Lenzi' exists and get its ID
cursor.execute("INSERT OR IGNORE INTO groups (name) VALUES (?)", ("Biolab Lenzi",))
conn.commit()
cursor.execute("SELECT id FROM groups WHERE name = ?", ("Biolab Lenzi",))
group_id = cursor.fetchone()[0]

# Define all players with attributes:
# (name, ik, speed, stamina, passing, shooting, dribbling, defense, physical, goalkeeper)
players = [
    ("bel", 0, 0, 0, 0, 0, 0, 0, 0, True),
    ("lucas piazo", 0, 0, 0, 0, 0, 0, 0, 0, True),
    ("deyvid", 50, 25, 35, 65, 55, 60, 65, 50, False),
    ("Gasolina", 60, 20, 25, 65, 85, 45, 55, 40, False),
    ("Thiago Piana", 75, 60, 65, 85, 90, 75, 70, 90, False),
    ("Wiliam", 75, 65, 60, 85, 90, 80, 60, 90, False),
    ("neto", 65, 65, 55, 75, 70, 75, 45, 35, False),
    ("rogerinho", 35, 25, 30, 30, 30, 20, 35, 10, False),
    ("jorge", 70, 40, 55, 80, 80, 70, 60, 60, False),
    ("lucas veloso", 30, 82, 78, 69, 84, 75, 60, 77, False),
    ("Gui", 60, 75, 75, 75, 85, 80, 60, 60, False),
    ("vini", 60, 85, 90, 70, 40, 80, 80, 75, False),
    ("averlan", 40, 65, 60, 40, 40, 50, 65, 80, False),
    ("cezar", 80, 40, 50, 80, 90, 70, 40, 75, False),
    ("Gabriel", 60, 55, 55, 70, 60, 55, 60, 45, False),
    ("Joao vitor", 35, 85, 80, 60, 70, 90, 55, 60, False),
]

# Insert players into the database
for name, ik, speed, stamina, passing, shooting, dribbling, defense, physical, gk in players:
    cursor.execute("""
        INSERT INTO players (
            name, IQ, speed, stamina, passing, shooting,
            dribbling, defense, physical, goalkeeper, group_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name, ik, speed, stamina, passing, shooting,
        dribbling, defense, physical, int(gk), group_id
    ))

conn.commit()
conn.close()

print("✅ Players populated successfully.")
