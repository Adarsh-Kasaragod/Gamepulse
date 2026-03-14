# src/database.py
import sqlite3
import logging
from typing import List, Optional, Dict, Any
from .models import Team, Player, Match
from datetime import datetime
# Add logger
logger = logging.getLogger(__name__)

class CricketDatabase:
    def __init__(self, db_path: str = "cricket_analytics.db"):
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        """Get a new database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_db(self):
        """Initialize database: create tables if missing, upgrade schema safely"""
        conn = self._get_conn()
        cursor = conn.cursor()

        # === STEP 1: Check if tables exist ===
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='teams'")
        teams_exists = cursor.fetchone() is not None

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='players'")
        players_exists = cursor.fetchone() is not None

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='matches'")
        matches_exists = cursor.fetchone() is not None

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='batting_performances'")
        batting_exists = cursor.fetchone() is not None

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bowling_performances'")
        bowling_exists = cursor.fetchone() is not None

        # === STEP 2: Create tables if they don't exist ===
        if not teams_exists:
            cursor.execute("""
                CREATE TABLE teams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    status TEXT DEFAULT 'active',
                    description TEXT,
                    rating REAL DEFAULT 5.0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("Created 'teams' table")

        if not players_exists:
            cursor.execute("""
                CREATE TABLE players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    team_id INTEGER,
                    specialization TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(team_id) REFERENCES teams(id) ON DELETE CASCADE
                )
            """)
            print("Created 'players' table")

        if not matches_exists:
            cursor.execute("""
                CREATE TABLE matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    date TEXT NOT NULL,
                    team_id INTEGER,
                    team1_id INTEGER,
                    team2_id INTEGER,
                    type TEXT DEFAULT 'T20',
                    score1 TEXT DEFAULT '0/0',
                    score2 TEXT DEFAULT '0/0',
                    run_rate1 REAL DEFAULT 0.0,
                    run_rate2 REAL DEFAULT 0.0,
                    result TEXT,
                    mom TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(team_id) REFERENCES teams(id) ON DELETE SET NULL,
                    FOREIGN KEY(team1_id) REFERENCES teams(id) ON DELETE SET NULL,
                    FOREIGN KEY(team2_id) REFERENCES teams(id) ON DELETE SET NULL
                )
            """)
            print("Created 'matches' table")

        if not batting_exists:
            cursor.execute("""
                CREATE TABLE batting_performances (
                    match_id INTEGER,
                    player_id INTEGER,
                    runs INTEGER DEFAULT 0,
                    balls_faced INTEGER DEFAULT 0,
                    PRIMARY KEY (match_id, player_id),
                    FOREIGN KEY(match_id) REFERENCES matches(id) ON DELETE CASCADE,
                    FOREIGN KEY(player_id) REFERENCES players(id) ON DELETE CASCADE
                )
            """)
            print("Created 'batting_performances' table")

        if not bowling_exists:
            cursor.execute("""
                CREATE TABLE bowling_performances (
                    match_id INTEGER,
                    player_id INTEGER,
                    overs REAL DEFAULT 0.0,
                    wickets INTEGER DEFAULT 0,
                    runs_conceded INTEGER DEFAULT 0,
                    PRIMARY KEY (match_id, player_id),
                    FOREIGN KEY(match_id) REFERENCES matches(id) ON DELETE CASCADE,
                    FOREIGN KEY(player_id) REFERENCES players(id) ON DELETE CASCADE
                )
            """)
            print("Created 'bowling_performances' table")

        # === STEP 3: Safe schema upgrades (only if tables exist) ===
        if teams_exists:
            cursor.execute("PRAGMA table_info(teams)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'status' not in columns:
                cursor.execute("ALTER TABLE teams ADD COLUMN status TEXT DEFAULT 'active'")
            if 'description' not in columns:
                cursor.execute("ALTER TABLE teams ADD COLUMN description TEXT")
            if 'rating' not in columns:
                cursor.execute("ALTER TABLE teams ADD COLUMN rating REAL DEFAULT 5.0")

        if players_exists:
            cursor.execute("PRAGMA table_info(players)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'specialization' not in columns:
                cursor.execute("ALTER TABLE players ADD COLUMN specialization TEXT")

        # For matches: we already created full schema above if missing, so no need to alter

        conn.commit()
        conn.close()
        print("Database initialized successfully!")

    # CRUD Operations
    def create_team(self, name: str, status: str = 'active', description: str = None, rating: float = 5.0) -> int:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO teams (name, status, description, rating) VALUES (?, ?, ?, ?)", 
                      (name, status, description, rating))
        team_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return team_id

    def get_teams(self) -> List[Team]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, status, description, rating, created_at FROM teams ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        
        teams = []
        for row in rows:
            # Get statistics for each team
            stats = self.get_team_statistics(row['id'])
            teams.append(Team(
                id=row['id'], 
                name=row['name'], 
                status=row['status'],
                description=row['description'],
                rating=row['rating'],
                player_count=stats["player_count"],
                match_count=stats["match_count"],
                created_at=row['created_at']
            ))
        return teams

    def get_team(self, team_id: int) -> Optional[Team]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, status, description, rating, created_at FROM teams WHERE id = ?", (team_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            # Get statistics for the team
            stats = self.get_team_statistics(team_id)
            return Team(
                id=row['id'], 
                name=row['name'], 
                status=row['status'],
                description=row['description'],
                rating=row['rating'],
                player_count=stats["player_count"],
                match_count=stats["match_count"],
                created_at=row['created_at']
            )
        return None

    def update_team(self, team_id: int, name: str = None, status: str = None, description: str = None, rating: float = None) -> bool:
        """Update team information"""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            # Build update query dynamically based on provided fields
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if status is not None:
                updates.append("status = ?")
                params.append(status)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            if rating is not None:
                updates.append("rating = ?")
                params.append(rating)
            
            if not updates:
                conn.close()
                return False
            
            params.append(team_id)
            query = f"UPDATE teams SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except Exception as e:
            logger.error(f"Error updating team: {e}")
            return False

    def delete_team(self, team_id: int) -> bool:
        """Delete a team and all its associated data"""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            # Delete team (cascade will handle players and performances)
            cursor.execute("DELETE FROM teams WHERE id = ?", (team_id,))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except Exception as e:
            logger.error(f"Error deleting team: {e}")
            return False

    def create_player(self, name: str, role: str, team_id: int, specialization: str = None) -> int:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO players (name, role, team_id, specialization) VALUES (?, ?, ?, ?)",
                       (name, role, team_id, specialization))
        player_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return player_id

    def get_players(self, team_id: Optional[int] = None) -> List[Player]:
        conn = self._get_conn()
        cursor = conn.cursor()
        if team_id:
            cursor.execute("SELECT id, name, role, team_id, specialization, created_at FROM players WHERE team_id = ? ORDER BY name", (team_id,))
        else:
            cursor.execute("SELECT id, name, role, team_id, specialization, created_at FROM players ORDER BY name")
        rows = cursor.fetchall()
        conn.close()
        players = []
        for row in rows:
            players.append(Player(
                id=row['id'], 
                name=row['name'], 
                role=row['role'],
                team_id=row['team_id'],
                specialization=row['specialization'],
                created_at=row['created_at']
            ))
        return players

    def get_player(self, player_id: int) -> Optional[Player]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, role, team_id, specialization, created_at FROM players WHERE id = ?", (player_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Player(
                id=row['id'], 
                name=row['name'], 
                role=row['role'],
                team_id=row['team_id'],
                specialization=row['specialization'],
                created_at=row['created_at']
            )
        return None

    def update_player(self, player_id: int, name: str = None, role: str = None, specialization: str = None) -> bool:
        """Update player information"""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if role is not None:
                updates.append("role = ?")
                params.append(role)
            if specialization is not None:
                updates.append("specialization = ?")
                params.append(specialization)
            
            if not updates:
                conn.close()
                return False
            
            params.append(player_id)
            query = f"UPDATE players SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except Exception as e:
            logger.error(f"Error updating player: {e}")
            return False

    def delete_player(self, player_id: int) -> bool:
        """Delete a player"""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM players WHERE id = ?", (player_id,))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except Exception as e:
            logger.error(f"Error deleting player: {e}")
            return False
        
    def create_match(self, name: str, date: str, team_id: Optional[int] = None, 
            team1_id: Optional[int] = None, team2_id: Optional[int] = None, 
            type: str = 'T20', score1: str = '0/0', score2: str = '0/0',
            run_rate1: float = 0.0, run_rate2: float = 0.0, 
            result: Optional[str] = None, mom: Optional[str] = None) -> Match:
            """
            Create a new match and return the full Match object
            """
            conn = self._get_conn()
            cursor = conn.cursor()
    
            try:
                # Validation
                if team1_id and team2_id and team1_id == team2_id:
                    raise ValueError("team1_id and team2_id cannot be the same")
        
                if team1_id and not self.get_team(team1_id):
                    raise ValueError(f"Team with id {team1_id} does not exist")
                if team2_id and not self.get_team(team2_id):
                    raise ValueError(f"Team with id {team2_id} does not exist")
        
        # Backward compatibility: if only team_id provided, use as team1_id
                if team_id and not team1_id and not team2_id:
                    team1_id = team_id

                cursor.execute("""
            INSERT INTO matches (
                name, date, team_id, team1_id, team2_id, type, 
                score1, score2, run_rate1, run_rate2, result, mom
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, date, team_id, team1_id, team2_id, type, 
              score1, score2, run_rate1, run_rate2, result, mom))
        
                match_id = cursor.lastrowid
                conn.commit()

        # Return full Match object
                return Match(
            id=match_id,
            name=name,
            date=date,
            team_id=team_id,
            team1_id=team1_id,
            team2_id=team2_id,
            type=type,
            score1=score1,
            score2=score2,
            run_rate1=run_rate1,
            run_rate2=run_rate2,
            result=result,
            mom=mom,
            created_at=datetime.now().isoformat()
        )
    
            except Exception as e:
                conn.rollback()
                logger.error(f"Error creating match: {e}")
                raise
            finally:
                conn.close()

    def get_matches(self, team_id: Optional[int] = None) -> List[Match]:
        conn = self._get_conn()
        cursor = conn.cursor()
    
        if team_id:
            cursor.execute("PRAGMA table_info(matches)")
            columns = [col[1] for col in cursor.fetchall()]
        
            if 'team1_id' in columns:
                cursor.execute("""
                SELECT id, name, date, team_id, team1_id, team2_id, type, score1, score2, 
                       run_rate1, run_rate2, result, mom, created_at 
                FROM matches 
                WHERE team1_id = ? OR team2_id = ?
                ORDER BY created_at DESC  -- ← Changed from date to created_at
            """, (team_id, team_id))
            else:
                cursor.execute("""
                SELECT id, name, date, team_id, created_at 
                FROM matches 
                WHERE team_id = ?
                ORDER BY created_at DESC  -- ← Changed here too
            """, (team_id,))
        else:
            cursor.execute("PRAGMA table_info(matches)")
            columns = [col[1] for col in cursor.fetchall()]
        
            if 'team1_id' in columns:
                cursor.execute("""
                SELECT id, name, date, team_id, team1_id, team2_id, type, score1, score2, 
                       run_rate1, run_rate2, result, mom, created_at 
                FROM matches 
                ORDER BY created_at DESC  -- ← THIS IS THE KEY FIX
            """)
            else:
                cursor.execute("""
                SELECT id, name, date, team_id, created_at 
                FROM matches 
                ORDER BY created_at DESC  -- ← And here
            """)
            
        rows = cursor.fetchall()
        conn.close()
        matches = []
        for row in rows:
            # Create match object based on available columns
            if 'type' in dict(row).keys():
                matches.append(Match(
                    id=row['id'],
                    name=row['name'],
                    date=row['date'],
                    team_id=row['team_id'],
                    team1_id=row['team1_id'] if 'team1_id' in dict(row).keys() else None,
                    team2_id=row['team2_id'] if 'team2_id' in dict(row).keys() else None,
                    type=row['type'] if 'type' in dict(row).keys() else 'T20',
                    score1=row['score1'] if 'score1' in dict(row).keys() else '0/0',
                    score2=row['score2'] if 'score2' in dict(row).keys() else '0/0',
                    run_rate1=row['run_rate1'] if 'run_rate1' in dict(row).keys() else 0.0,
                    run_rate2=row['run_rate2'] if 'run_rate2' in dict(row).keys() else 0.0,
                    result=row['result'] if 'result' in dict(row).keys() else None,
                    mom=row['mom'] if 'mom' in dict(row).keys() else None,
                    created_at=row['created_at']
                ))
            else:
                matches.append(Match(
                    id=row['id'],
                    name=row['name'],
                    date=row['date'],
                    team_id=row['team_id'],
                    created_at=row['created_at']
                ))
        return matches

    def add_batting_performance(self, match_id: int, player_id: int, runs: int, balls_faced: int):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO batting_performances 
            (match_id, player_id, runs, balls_faced) 
            VALUES (?, ?, ?, ?)
        """, (match_id, player_id, runs, balls_faced))
        conn.commit()
        conn.close()

    def add_bowling_performance(self, match_id: int, player_id: int, overs: float, wickets: int, runs_conceded: int):
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO bowling_performances 
            (match_id, player_id, overs, wickets, runs_conceded) 
            VALUES (?, ?, ?, ?, ?)
        """, (match_id, player_id, overs, wickets, runs_conceded))
        conn.commit()
        conn.close()

    def get_player_performances(self, player_id: int) -> Optional[Dict]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT name, role, specialization FROM players WHERE id = ?", (player_id,))
        player_row = cursor.fetchone()
        if not player_row:
            conn.close()
            return None

        # Batting history
        cursor.execute("""
            SELECT m.date, bp.runs, bp.balls_faced
            FROM batting_performances bp
            JOIN matches m ON bp.match_id = m.id
            WHERE bp.player_id = ?
            ORDER BY m.date DESC
        """, (player_id,))
        batting = cursor.fetchall()

        # Bowling history
        cursor.execute("""
            SELECT m.date, bp.overs, bp.wickets, bp.runs_conceded
            FROM bowling_performances bp
            JOIN matches m ON bp.match_id = m.id
            WHERE bp.player_id = ?
            ORDER BY m.date DESC
        """, (player_id,))
        bowling = cursor.fetchall()

        conn.close()

        return {
            "player": {
                "name": player_row["name"], 
                "role": player_row["role"],
                "specialization": player_row["specialization"]
            },
            "batting_history": [{"date": r["date"], "runs": r["runs"], "balls_faced": r["balls_faced"]} for r in batting],
            "bowling_history": [{"date": r["date"], "overs": r["overs"], "wickets": r["wickets"], "runs_conceded": r["runs_conceded"]} for r in bowling]
        }

    def get_team_statistics(self, team_id: int) -> Dict[str, Any]:
        """Get team statistics including player count and match count"""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            # Get player count
            cursor.execute("SELECT COUNT(*) as count FROM players WHERE team_id = ?", (team_id,))
            player_result = cursor.fetchone()
            player_count = player_result['count'] if player_result else 0
            
            # Get match count
            cursor.execute("PRAGMA table_info(matches)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'team1_id' in columns:
                cursor.execute("SELECT COUNT(*) as count FROM matches WHERE team1_id = ? OR team2_id = ?", (team_id, team_id))
            else:
                cursor.execute("SELECT COUNT(*) as count FROM matches WHERE team_id = ?", (team_id,))
            
            match_result = cursor.fetchone()
            match_count = match_result['count'] if match_result else 0
            
            conn.close()
            
            return {
                "player_count": player_count,
                "match_count": match_count
            }
        except Exception as e:
            logger.error(f"Error getting team statistics: {e}")
            return {"player_count": 0, "match_count": 0}