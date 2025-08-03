from abstraction import abstraction
from datetime import datetime
from tabulate import tabulate
import sqlite3

DB_PATH = 'tournament_scheduler.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    # Create tournaments table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tournaments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            description TEXT
        )
    ''')
    # Create matches table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tournament_id INTEGER NOT NULL,
            team1 TEXT NOT NULL,
            team2 TEXT NOT NULL,
            date TEXT,
            time TEXT,
            FOREIGN KEY (tournament_id) REFERENCES tournaments(id)
        )
    ''')
    conn.commit()
    conn.close()

def insert_tournament(name, start_date, end_date, description):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO tournaments (name, start_date, end_date, description)
        VALUES (?, ?, ?, ?)
    ''', (name, start_date, end_date, description))
    conn.commit()
    tournament_id = cur.lastrowid
    conn.close()
    return tournament_id

def fetch_tournament_by_id(tournament_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM tournaments WHERE id = ?', (tournament_id,))
    tournament = cur.fetchone()
    conn.close()
    return tournament

def migrate_add_location_column():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(matches)")
    columns = [row[1] for row in cur.fetchall()]
    if 'location' not in columns:
        cur.execute('ALTER TABLE matches ADD COLUMN location TEXT')
        conn.commit()
    conn.close()

def migrate_add_duration_column():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(matches)")
    columns = [row[1] for row in cur.fetchall()]
    if 'duration' not in columns:
        cur.execute('ALTER TABLE matches ADD COLUMN duration INTEGER DEFAULT 1')
        conn.commit()
    conn.close()

migrate_add_location_column()
migrate_add_duration_column()

def insert_match(tournament_id, team1, team2, date=None, time=None, location=None, duration=1):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO matches (tournament_id, team1, team2, date, time, location, duration)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (tournament_id, team1, team2, date, time, location, duration))
    conn.commit()
    match_id = cur.lastrowid
    conn.close()
    return match_id

def fetch_matches_by_tournament(tournament_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM matches WHERE tournament_id = ?', (tournament_id,))
    matches = cur.fetchall()
    conn.close()
    return matches

def update_match_in_db(match_id, date, time, location=None, duration=None):
    conn = get_db_connection()
    cur = conn.cursor()
    if location is not None and duration is not None:
        cur.execute('UPDATE matches SET date = ?, time = ?, location = ?, duration = ? WHERE id = ?', (date, time, location, duration, match_id))
    elif location is not None:
        cur.execute('UPDATE matches SET date = ?, time = ?, location = ? WHERE id = ?', (date, time, location, match_id))
    elif duration is not None:
        cur.execute('UPDATE matches SET date = ?, time = ?, duration = ? WHERE id = ?', (date, time, duration, match_id))
    else:
        cur.execute('UPDATE matches SET date = ?, time = ? WHERE id = ?', (date, time, match_id))
    conn.commit()
    conn.close()

def fetch_all_tournaments():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM tournaments ORDER BY id DESC')
    tournaments = cur.fetchall()
    conn.close()
    return tournaments

def delete_tournament_by_id(tournament_id):
    conn = get_db_connection()
    cur = conn.cursor()
    # Delete matches first (to maintain referential integrity)
    cur.execute('DELETE FROM matches WHERE tournament_id = ?', (tournament_id,))
    cur.execute('DELETE FROM tournaments WHERE id = ?', (tournament_id,))
    conn.commit()
    conn.close()

# Call init_db() when this module is imported
init_db()

class MatchScheduler:
    def __init__(self):
        self.matches = []

    def generate_matches(self, teams):
        self.matches = []
        match_id = 1
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                self.matches.append({"id": match_id, "teams": [teams[i], teams[j]]})
                match_id += 1
        print("Matches generated successfully!")

    def schedule_matches(self):
        if not self.matches:
            print("No matches available to schedule.")
            return

        print("\nLet's schedule the matches. Enter the date and time for each match.")
        for match in self.matches:
            print(f"\nMatch ID: {match['id']}, Teams: {match['teams'][0]} vs {match['teams'][1]}")
            while True:
                date = input("Enter match date (YYYY-MM-DD): ").strip()
                time = input("Enter match time (HH:MM): ").strip()
                try:
                    datetime.strptime(date, "%Y-%m-%d")
                    datetime.strptime(time, "%H:%M")
                    match["date"] = date
                    match["time"] = time
                    break
                except ValueError:
                    print("Invalid date or time format. Please try again.")
        print("All matches have been scheduled successfully! 👍👍")

    def view_matches(self):
        if not self.matches:
            print("No matches scheduled.")
        else:
            headers = ["ID", "Teams", "Date", "Time"]
            table = [
                [match["id"], f"{match['team1']} vs {match['team2']}", match.get("date", "Not Scheduled"),
                 match.get("time", "Not Scheduled")]
                for match in self.matches
            ]
            print("\nMatch Schedule:")
            print(tabulate(table, headers=headers, tablefmt="grid"))

    def update_match(self):
        if not self.matches:
            print("No matches to update.")
            return

        try:
            match_id = int(input("Enter the Match ID to update: ").strip())
        except ValueError:
            print("Invalid ID. Please enter a valid number.")
            return

        for match in self.matches:
            if match["id"] == match_id:
                print(f"\nCurrent Details for Match ID {match_id}: Teams: {match['team1']} vs {match['team2']}, "
                      f"Date: {match.get('date', 'Not Scheduled')}, Time: {match.get('time', 'Not Scheduled')}")
                while True:
                    date = input("Enter new match date (YYYY-MM-DD): ").strip()
                    time = input("Enter new match time (HH:MM): ").strip()
                    try:
                        datetime.strptime(date, "%Y-%m-%d")
                        datetime.strptime(time, "%H:%M")
                        match["date"] = date
                        match["time"] = time
                        print("Match updated successfully!")
                        return
                    except ValueError:
                        print("Invalid date or time format. Please try again.")
        print("Match not found.")

    def cancel_match(self):
        if not self.matches:
            print("No matches to cancel.")
            return

        try:
            match_id = int(input("Enter the Match ID to cancel: ").strip())
        except ValueError:
            print("Invalid ID. Please enter a valid number.")
            return

        for match in self.matches:
            if match["id"] == match_id:
                print(f"\nMatch ID: {match_id}, Teams: {match['team1']} vs {match['team2']}")
                weather = input("What is the weather like? (Sunny/Rainy/Cloudy): ").strip().lower()
                if weather == "rainy":
                    self.matches.remove(match)
                    print(f"Match ID {match_id} canceled due to rainy weather! 🌧️")
                else:
                    print("The match can continue. No cancellation required. ☀️")
                return
        print("Match not found.")

    def check_conflicts(self):
        if not self.matches:
            print("No matches scheduled.")
            return

        conflicts = []
        match_schedule = {}

        for match in self.matches:
            if "date" in match and "time" in match:
                key = (match["date"], match["time"])
                if key not in match_schedule:
                    match_schedule[key] = []
                match_schedule[key].append(match)

        for key, conflict_matches in match_schedule.items():
            if len(conflict_matches) > 1:
                conflicts.append((key, conflict_matches))

        if conflicts:
            print("\nConflicts Found:")
            for (date, time), conflict_matches in conflicts:
                print(f"\nDate: {date}, Time: {time}")
                for conflict in conflict_matches:
                    print(f"  Match ID: {conflict['id']}, Teams: {conflict['team1']} vs {conflict['team2']}")
        else:
            print("No conflicts found. All matches are scheduled properly.")



