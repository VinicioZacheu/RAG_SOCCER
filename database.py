import sqlite3
import os

DB_PATH = os.path.join("data", "db.sqlite3")

def get_connection():
    """Returns a connection to the SQLite database."""
    if not os.path.exists("data"):
        os.makedirs("data")
    return sqlite3.connect(DB_PATH)

def init_db():
    """Creates the necessary tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create groups table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS groups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    );
    """)

    # Create players table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        IQ INTEGER, 
        speed INTEGER,
        stamina INTEGER,
        passing INTEGER,
        shooting INTEGER,
        dribbling INTEGER,
        defense INTEGER,
        physical INTEGER,
        goalkeeper BOOLEAN DEFAULT 0,
        matches_played INTEGER DEFAULT 0,
        matches_won INTEGER DEFAULT 0,
        matches_lost INTEGER DEFAULT 0,
        best_player_awards INTEGER DEFAULT 0,
        goals_scored INTEGER DEFAULT 0,
        assists INTEGER DEFAULT 0,
        avg_defensive INTEGER DEFAULT 0,
        avg_offensive INTEGER DEFAULT 0,
        avg_total INTEGER DEFAULT 0,
        group_id INTEGER,
        FOREIGN KEY (group_id) REFERENCES groups(id)
        
    );
    """)

    # Create matches table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS matches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        winner_team TEXT CHECK(winner_team IN ('A', 'B', 'Draw')),
        team_a_score INTEGER,
        team_b_score INTEGER,
        group_id INTEGER,
        FOREIGN KEY (group_id) REFERENCES groups(id)
    );
    """)

    # Create match_players linking table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS match_players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        match_id INTEGER,
        player_id INTEGER,
        team TEXT CHECK(team IN ('A', 'B')),
        is_winner BOOLEAN,
        goals INTEGER DEFAULT 0,
        assists INTEGER DEFAULT 0,
        is_best_player BOOLEAN DEFAULT 0,
        FOREIGN KEY (match_id) REFERENCES matches(id),
        FOREIGN KEY (player_id) REFERENCES players(id)
    );
    """)

    # Insert default groups (if not already present)
    cursor.executemany("""
    INSERT OR IGNORE INTO groups (name) VALUES (?)
    """, [("Biolab Lenzi",), ("UFC",), ("Saturday",)])

    conn.commit()
    conn.close()

def add_player(player):
    """Inserts a player with calculated averages into the database."""

    # Lookup group ID by name
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM groups WHERE name = ?", (player["group"],))
    result = cursor.fetchone()
    if not result:
        raise ValueError(f"Group '{player['group']}' not found.")
    group_id = result[0]

    # Calculate averages
    avg_defensive = (
        player["defense"] * 3 +
        player["physical"] +
        player["stamina"] +
        player["speed"]
    ) // 6

    avg_offensive = (
        player["speed"] +
        player["stamina"] +
        player["passing"] +
        player["shooting"] * 2 +
        player["dribbling"] * 2 +
        player["physical"]
    ) // 8

    avg_total = (avg_defensive + avg_offensive) // 2

    # Insert player
    cursor.execute("""
        INSERT INTO players (
            name, speed, stamina, passing, shooting, dribbling,
            defense, physical, goalkeeper, group_id,
            avg_defensive, avg_offensive, avg_total
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        player["name"],
        player["speed"],
        player["stamina"],
        player["passing"],
        player["shooting"],
        player["dribbling"],
        player["defense"],
        player["physical"],
        int(player["goalkeeper"]),
        group_id,
        avg_defensive,
        avg_offensive,
        avg_total
    ))

    conn.commit()
    conn.close()


# Optional direct run
if __name__ == "__main__":
    init_db()
    print("Database initialized.")
