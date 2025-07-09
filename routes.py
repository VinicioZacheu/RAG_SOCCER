from flask import Blueprint, render_template, request, redirect, url_for
from database import get_connection
from langchain_modules.llm_runner import generate_balanced_teams

routes = Blueprint("routes", __name__)

@routes.route("/")
def index():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, matches_won, matches_lost, best_player_awards, goals_scored, assists
        FROM players
        ORDER BY matches_won DESC
        LIMIT 10
    """)
    top_players = cursor.fetchall()
    conn.close()
    return render_template("index.html", players=top_players)


@routes.route("/add-player", methods=["GET", "POST"])
def add_player():
    if request.method == "POST":
        data = request.form
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO players (
                name, speed, stamina, passing, shooting,
                dribbling, defense, physical, goalkeeper
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["name"],
            int(data["speed"]),
            int(data["stamina"]),
            int(data["passing"]),
            int(data["shooting"]),
            int(data["dribbling"]),
            int(data["defense"]),
            int(data["physical"]),
            int(data.get("goalkeeper", 0))
        ))
        conn.commit()
        conn.close()
        return redirect(url_for("routes.index"))

    return render_template("add_player.html")

@routes.route("/create-match", methods=["GET"])
def create_match():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM players")
    players = cursor.fetchall()
    conn.close()
    return render_template("create_match.html", players=players)


@routes.route("/generate-teams", methods=["POST"])
def generate_teams():
    # 1. Get selected player IDs
    player_ids = request.form.getlist("player_ids")
    if len(player_ids) % 2 != 0:
        return "Numero de jogadores deve ser par.", 400

    # 2. Load player stats from DB
    conn = get_connection()
    cursor = conn.cursor()
    placeholders = ",".join("?" for _ in player_ids)
    cursor.execute(f"""
        SELECT id, name, iq, speed, stamina, passing,
               shooting, dribbling, defense, physical, goalkeeper, group_id
        FROM players
        WHERE id IN ({placeholders})
    """, player_ids)
    rows = cursor.fetchall()
    conn.close()

    # 3. Build dicts for LLM
    players = [
        {"id": r[0], "name": r[1], "iq": r[2], "speed": r[3], "stamina": r[4],
         "passing": r[5], "shooting": r[6], "dribbling": r[7],
         "defense": r[8], "physical": r[9], "goalkeeper": bool(r[10]),
         "group_id": r[11]}
        for r in rows
    ]

    # 4. Ask the LLM for balanced teams
    raw = generate_balanced_teams(players)

    # DEBUG: log what we got back
    print("🔍 LLM raw response:\n", raw)

    # 5) Parse the LLM response into two lists
    team_a, team_b = [], []
    current = None
    for line in raw.splitlines():
        line = line.strip()

        # switch to Portuguese markers
        if line.lower().startswith("time a"):
            current = team_a
            continue
        if line.lower().startswith("time b"):
            current = team_b
            continue

        # capture bullets
        if line.startswith("-") and current is not None:
            # strip leading "- " or "-"
            name = line.lstrip("- ").strip()
            current.append(name)

    # 6. Save the match to the DB
    conn = get_connection()
    cursor = conn.cursor()

    # Assuming all players are in the same group
    group_id = players[0]["group_id"]

    cursor.execute("""
        INSERT INTO matches (winner_team, team_a_score, team_b_score, group_id)
        VALUES (?, ?, ?, ?)
    """, ("Draw", 0, 0, group_id))
    match_id = cursor.lastrowid

    # 7. Link each player to the match
    name_to_id = {p["name"]: p["id"] for p in players}

    for name in team_a:
        pid = name_to_id.get(name)
        if pid:
            cursor.execute("""
                INSERT INTO match_players (match_id, player_id, team, is_winner)
                VALUES (?, ?, 'A', 0)
            """, (match_id, pid))
    for name in team_b:
        pid = name_to_id.get(name)
        if pid:
            cursor.execute("""
                INSERT INTO match_players (match_id, player_id, team, is_winner)
                VALUES (?, ?, 'B', 0)
            """, (match_id, pid))

    conn.commit()
    conn.close()

    players_a = [p for p in players if p["name"] in team_a]
    players_b = [p for p in players if p["name"] in team_b]

    # 8. Render result page
    return render_template(
        "generated_teams.html",
        team_a=team_a,
        team_b=team_b,
        raw=raw
    )

@routes.route("/confirm-match", methods=["POST"])
def confirm_match():
    # 1) Lê os arrays vindos dos hidden inputs
    team_a_ids = request.form.getlist("team_a[]")
    team_b_ids = request.form.getlist("team_b[]")
    all_ids = team_a_ids + team_b_ids
    if len(all_ids) < 2:
        return "Selecione pelo menos 2 jogadores.", 400

    conn = get_connection()
    cur = conn.cursor()

    # 2) Insere partida
    group_id = cur.execute(
        "SELECT group_id FROM players WHERE id = ?",
        (all_ids[0],)
    ).fetchone()[0]
    cur.execute(
        "INSERT INTO matches (winner_team, team_a_score, team_b_score, group_id) VALUES (?, ?, ?, ?)",
        ("Draw", 0, 0, group_id)
    )
    match_id = cur.lastrowid

    # 3) Insere jogadores na match_players
    for pid in team_a_ids:
        cur.execute(
            "INSERT INTO match_players (match_id, player_id, team, is_winner) VALUES (?, ?, 'A', 0)",
            (match_id, pid)
        )
    for pid in team_b_ids:
        cur.execute(
            "INSERT INTO match_players (match_id, player_id, team, is_winner) VALUES (?, ?, 'B', 0)",
            (match_id, pid)
        )

    conn.commit()
    conn.close()

    # 4) Redireciona para home ou página de sucesso
    return redirect(url_for("routes.index"))

