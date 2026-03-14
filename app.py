from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from src.database import CricketDatabase
import logging
import os
from datetime import datetime, timedelta
from src.models import Team, Player, Match
from src.analytics import CricketAnalytics
# from chat import chat_bp
import json
import time
from openai import OpenAI
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)


app = Flask(__name__, template_folder='templates')
CORS(app)

# app.register_blueprint(chat_bp)
# Serve static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

db = CricketDatabase()

# Import analytics after db is created
from src.analytics import CricketAnalytics
analytics = CricketAnalytics(db)

# Global variable for active sessions tracking
active_sessions = {
    'count': 1,
    'last_updated': time.time(),
    'sessions': {}
}

# ========== PAGE ROUTES ==========
@app.route('/')
def dashboard():
    # Track this session
    session_id = request.remote_addr + str(time.time())
    active_sessions['sessions'][session_id] = time.time()
    active_sessions['count'] = len(active_sessions['sessions'])
    active_sessions['last_updated'] = time.time()
    
    # Clean up old sessions (older than 30 minutes)
    current_time = time.time()
    expired = [sid for sid, ts in active_sessions['sessions'].items() 
               if current_time - ts > 1800]
    for sid in expired:
        del active_sessions['sessions'][sid]
    active_sessions['count'] = len(active_sessions['sessions'])
    
    return render_template('index.html')

@app.route('/teams')
def teams_page():
    return render_template('teams.html')

@app.route('/players')
def players_page():
    return render_template('players.html')

@app.route('/analytics')
def analytics_page():
    return render_template('analytics.html')

@app.route('/recommendations')
def recommendations_page():
    """AI Team Selector / Recommendations Page"""
    try:
        teams = db.get_teams()
        team_list = []
        for team in teams:
            team_dict = team.to_dict()
            # Add player count for display
            players = db.get_players(team_id=team.id)
            team_dict['player_count'] = len(players) if players else 0
            team_list.append(team_dict)
        
        return render_template('recommendations.html', teams=team_list)
    except Exception as e:
        logger.error(f"Error loading recommendations page: {e}")
        # Even on error, render page with empty teams
        return render_template('recommendations.html', teams=[])

@app.route('/create-team')
def create_team_page():
    return render_template('create_teams.html')

@app.route('/edit-team/<int:team_id>')
def edit_team_page(team_id):
    return render_template('edit_team.html', team_id=team_id)

@app.route('/manage-data')
def manage_data_page():
    """Data Management Page - Add players and record performances"""
    try:
        teams = db.get_teams()
        players = db.get_players()
        all_matches = db.get_matches()  # Get ALL matches

        if all_matches:
            # Sort by date descending (newest first)
            sorted_matches = sorted(
                all_matches,
                key=lambda m: m.date or '1900-01-01',
                reverse=True
            )
            # Take the latest 5
            recent_matches = sorted_matches[:5]
        else:
            recent_matches = []

        team_list = [team.to_dict() for team in teams]
        player_list = [player.to_dict() for player in players]
        recent_match_list = [match.to_dict() for match in recent_matches]

        return render_template(
            'manage_data.html',
            teams=team_list,
            players=player_list,
            matches=recent_match_list  # Always the 5 newest
        )
    except Exception as e:
        logger.error(f"Error loading manage data page: {e}")
        return render_template(
            'manage_data.html',
            teams=[], players=[], matches=[]
        )

@app.route('/create-match')
def create_match_data():
    """Page to create a new match"""
    try:
        teams = db.get_teams()  # Get all teams from database
        team_list = [team.to_dict() for team in teams]  # Convert to dicts for template
        return render_template('create_match.html', teams=team_list)
    except Exception as e:
        logger.error(f"Error loading create match page: {e}")
        # Fallback: render with empty list so page still loads
        return render_template('create_match.html', teams=[])

# ========== API ENDPOINTS ==========

@app.route('/api/dashboard/summary')
def dashboard_summary():
    """Get complete dashboard summary with real-time data"""
    try:
        # Get all data
        teams = db.get_teams()
        players = db.get_players()
        matches = db.get_matches()
        
        # Calculate real-time stats
        total_teams = len(teams) if teams else 0
        total_players = len(players) if players else 0
        total_matches = len(matches) if matches else 0
        
        # Calculate average rating from real player performances
        total_rating = 0
        rated_players = 0
        
        # Get batting leaders
        batting_leaders = []
        for player in players:
            stats = analytics.calculate_player_stats(player.id)
            if stats and stats.total_runs and stats.total_runs > 0:
                player_data = player.to_dict()
                player_data.update({
                    'total_runs': stats.total_runs or 0,
                    'batting_average': round(stats.batting_average, 1) if stats.batting_average else 0,
                    'strike_rate': round(stats.strike_rate, 1) if stats.strike_rate else 0,
                    'rating': calculate_player_rating(stats)
                })
                batting_leaders.append(player_data)
                rated_players += 1
                total_rating += player_data['rating']
        
        # Sort batting leaders
        batting_leaders.sort(key=lambda x: x.get('rating', 0), reverse=True)
        
        # Get bowling leaders
        bowling_leaders = []
        for player in players:
            stats = analytics.calculate_player_stats(player.id)
            if stats and stats.total_wickets and stats.total_wickets > 0:
                player_data = player.to_dict()
                player_data.update({
                    'total_wickets': stats.total_wickets or 0,
                    'bowling_average': round(stats.bowling_average, 1) if stats.bowling_average else 0,
                    'economy_rate': round(stats.economy_rate, 1) if stats.economy_rate else 0,
                    'rating': calculate_player_rating(stats)
                })
                bowling_leaders.append(player_data)
                if player_data['rating'] > 0:
                    rated_players += 1
                    total_rating += player_data['rating']
        
        # Sort bowling leaders
        bowling_leaders.sort(key=lambda x: x.get('rating', 0), reverse=True)
        
        # Calculate average rating
        avg_rating = round(total_rating / rated_players, 1) if rated_players > 0 else 7.8
        
        # Get recent activity
        recent_activity = []
        if matches:
            recent_matches = sorted(matches, key=lambda m: m.date or datetime.now(), reverse=True)[:3]
            for match in recent_matches:
                recent_activity.append({
                    'type': 'match',
                    'text': f"New match: {match.name}",
                    'time': format_time_ago(match.date) if match.date else 'Recently'
                })
        
        if players:
            recent_players = sorted(players, key=lambda p: p.id, reverse=True)[:2]
            for player in recent_players:
                recent_activity.append({
                    'type': 'player',
                    'text': f"New player: {player.name}",
                    'time': 'Recently'
                })
        
        # System status
        storage_used = calculate_storage_usage()
        ai_status = "Ready"
        
        return jsonify({
            "success": True,
            "stats": {
                "total_teams": total_teams,
                "total_players": total_players,
                "total_matches": total_matches,
                "avg_rating": avg_rating
            },
            "leaders": {
                "batting": batting_leaders[:3],
                "bowling": bowling_leaders[:3]
            },
            "recent_activity": recent_activity[:5],
            "system": {
                "storage_used": storage_used,
                "storage_available": 100 - storage_used,
                "ai_status": ai_status,
                "active_sessions": active_sessions['count']
            }
        })
    except Exception as e:
        logger.error(f"Error getting dashboard summary: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

def calculate_player_rating(stats):
    """
    Rating scale: 1.0 – 10.0
    Average players ≈ 6–7
    Top performers ≈ 8–9
    Exceptional ≈ 9.5+
    """
    rating = 5.5  # base

    # Batting impact
    if stats.batting_average:
        rating += min(stats.batting_average / 35, 1.8)

    if stats.strike_rate:
        rating += min(stats.strike_rate / 150, 1.5)

    # Bowling impact
    if stats.total_wickets:
        rating += min(stats.total_wickets * 0.4, 1.5)

    if stats.economy_rate:
        rating += max(0, (8.5 - stats.economy_rate) * 0.3)

    return round(max(1.0, min(rating, 10.0)), 1)


def format_time_ago(date_str):
    """Format date string to time ago"""
    try:
        if isinstance(date_str, str):
            date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            date = date_str
            
        now = datetime.now()
        diff = now - date
        
        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600}h ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60}m ago"
        else:
            return "Just now"
    except:
        return "Recently"

def calculate_storage_usage():
    """Calculate simulated storage usage"""
    try:
        # Count total records in database
        conn = db._get_conn()
        cursor = conn.cursor()
        
        # Get counts from all tables
        tables = ['teams', 'players', 'matches', 'batting_performances', 'bowling_performances']
        total_records = 0
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                total_records += count
            except:
                pass
        
        conn.close()
        
        # Calculate percentage (simulated)
        # Assuming each record uses ~1KB, and we have 100MB total storage
        storage_used = min(95, (total_records * 0.001) / 100 * 100)  # Convert to percentage
        
        return round(storage_used, 1)
    except:
        return 45.5  # Default fallback

@app.route('/api/dashboard/live')
def dashboard_live():
    """Get live updating data for dashboard"""
    try:
        # Update active sessions
        current_time = time.time()
        expired = [sid for sid, ts in active_sessions['sessions'].items() 
                  if current_time - ts > 1800]  # 30 minutes timeout
        for sid in expired:
            del active_sessions['sessions'][sid]
        active_sessions['count'] = len(active_sessions['sessions'])
        
        # Get quick counts
        teams = db.get_teams()
        players = db.get_players()
        matches = db.get_matches()
        
        # Calculate storage usage
        storage_used = calculate_storage_usage()
        
        return jsonify({
            "success": True,
            "live_data": {
                "total_teams": len(teams) if teams else 0,
                "total_players": len(players) if players else 0,
                "total_matches": len(matches) if matches else 0,
                "active_sessions": active_sessions['count'],
                "storage_used": storage_used,
                "timestamp": datetime.now().isoformat()
            }
        })
    except Exception as e:
        logger.error(f"Error getting live data: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/recommendations/team/<int:team_id>')
def get_team_recommendations(team_id):
    """API endpoint to get team recommendations"""
    try:
        recommendation = analytics.recommend_team_selection(team_id)
        return jsonify({
            'success': True,
            'data': recommendation.to_dict()
        })
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/predictions/team/<int:team_id>')
def get_team_predictions(team_id):
    """API endpoint to get predictions for all players in a team"""
    try:
        players = db.get_players(team_id)
        predictions = []
        
        for player in players:
            prediction = analytics.predict_player_performance(player.id)
            if prediction:
                predictions.append(prediction.to_dict())
        
        return jsonify({
            'success': True,
            'predictions': predictions
        })
    except Exception as e:
        logger.error(f"Error getting predictions: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/ai-recommendations')
def ai_recommendations():
    """Main AI recommendations page"""
    teams = db.get_teams()
    
    # Convert teams to dictionaries for JSON serialization
    team_dicts = [team.to_dict() for team in teams]
    
    return render_template('ai_recommendations.html', teams=team_dicts)

@app.route('/api/dashboard/stats')
def dashboard_stats():
    """Get summary stats for dashboard"""
    try:
        teams = db.get_teams()
        players = db.get_players()
        matches = db.get_matches()
        
        # Calculate average rating from player analytics
        total_rating = 0
        rated_players = 0
        
        if players:
            for player in players:
                stats = analytics.calculate_player_stats(player.id)
                if not stats or stats.total_matches == 0:
                    continue
                rating = 5.0 
                if stats.batting_average and stats.batting_average > 0:
                    rating += min(stats.batting_average / 15, 3)

                if stats.bowling_average and stats.bowling_average > 0:
                    rating += min(20 / stats.bowling_average, 3)
                rating = min(rating, 10)

                total_rating += rating
                rated_players += 1
        
        avg_rating = round(total_rating / rated_players, 1) if rated_players > 0 else 7.8
        
        return jsonify({
            "success": True,
            "stats": {
                "total_teams": len(teams) if teams else 0,
                "total_players": len(players) if players else 0,
                "total_matches": len(matches) if matches else 0,
                "avg_rating": avg_rating
            }
        })
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/dashboard/leaders')
def dashboard_leaders():
    """Get top performing players for dashboard"""
    try:
        players = db.get_players()
        
        batsmen = []
        bowlers = []
        
        for player in players:
            stats = analytics.calculate_player_stats(player.id)
            if stats:
                player_data = {
                    "id": player.id,
                    "name": player.name,
                    "role": player.role,
                    "team_id": player.team_id
                }
                
                # Add batting stats if available
                if stats.total_runs and stats.total_runs > 0:
                    player_data.update({
                        "runs": stats.total_runs,
                        "batting_average": round(stats.batting_average, 1) if stats.batting_average else 0,
                        "strike_rate": round(stats.strike_rate, 1) if stats.strike_rate else 0,
                        "rating": round(stats.batting_average / 10, 1) if stats.batting_average else 0
                    })
                    if player.role == 'batsman' or player.role == 'all-rounder':
                        batsmen.append(player_data)
                
                # Add bowling stats if available
                if stats.total_wickets and stats.total_wickets > 0:
                    player_data.update({
                        "wickets": stats.total_wickets,
                        "bowling_average": round(stats.bowling_average, 1) if stats.bowling_average else 0,
                        "economy_rate": round(stats.economy_rate, 1) if stats.economy_rate else 0,
                        "rating": round(10 - (stats.bowling_average / 5) if stats.bowling_average else 5, 1)
                    })
                    if player.role == 'bowler' or player.role == 'all-rounder':
                        bowlers.append(player_data)
        
        # Sort and limit
        batsmen.sort(key=lambda x: x.get('rating', 0), reverse=True)
        bowlers.sort(key=lambda x: x.get('rating', 0), reverse=True)
        
        return jsonify({
            "success": True,
            "batsmen": batsmen[:3],
            "bowlers": bowlers[:3]
        })
    except Exception as e:
        logger.error(f"Error getting dashboard leaders: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/teams', methods=['GET'])
def get_teams():
    try:
        teams = db.get_teams()
        teams_data = []
        
        for team in teams:
            team_dict = team.to_dict()
            
            # Get team players count
            players = db.get_players(team_id=team.id)
            
            # Get team matches count
            matches = db.get_matches(team_id=team.id)
            
            # Calculate team rating based on player performances
            rated_players = 0
            team_rating = 0

            for player in players:
                stats = analytics.calculate_player_stats(player.id)

    # IMPORTANT: skip players with no matches
                if not stats or stats.total_matches == 0:
                    continue

                rating = 5.0

                if stats.batting_average and stats.batting_average > 0:
                    rating += min(stats.batting_average / 15, 3)

                if stats.bowling_average and stats.bowling_average > 0:
                    rating += min(20 / stats.bowling_average, 3)

                rating = min(rating, 10)

                team_rating += rating
                rated_players += 1

            team_rating = round(team_rating / rated_players, 1) if rated_players else 0

            
            # Add additional fields needed for the frontend
            team_dict.update({
                "player_count": len(players) if players else 0,
                "match_count": len(matches) if matches else 0,
                "rating": team_rating,
                "status": "active",  # Default status - you might want to add this to your database
                "created_at": datetime.now().isoformat()  # Add created timestamp
            })
            teams_data.append(team_dict)
        
        return jsonify({
            "success": True,
            "teams": teams_data
        })
    except Exception as e:
        logger.error(f"Error getting teams: {e}")
        return jsonify({"success": False, "error": str(e), "teams": []}), 500

@app.route('/api/teams/<int:team_id>', methods=['GET'])
def get_single_team(team_id):
    try:
        team = db.get_team(team_id)
        if not team:
            return jsonify({"success": False, "error": "Team not found"}), 404
        
        team_dict = team.to_dict()
        
        # Get team players count
        players = db.get_players(team_id=team_id)
        
        # Get team matches count
        matches = db.get_matches(team_id=team_id)
        
        # Calculate team rating
        team_rating = 0
        if players:
            for player in players:
                stats = analytics.calculate_player_stats(player.id)
                if stats:
                    player_rating = 0
                    if stats.batting_average:
                        player_rating += min(stats.batting_average / 10, 5)
                    if stats.bowling_average and stats.bowling_average > 0:
                        player_rating += min(25 / stats.bowling_average, 5)
                    team_rating += player_rating
            team_rating = round(team_rating / len(players), 1) if players else 7.5
        
        team_dict.update({
            "player_count": len(players) if players else 0,
            "match_count": len(matches) if matches else 0,
            "rating": team_rating,
            "status": "active",
            "created_at": datetime.now().isoformat()
        })
        
        return jsonify({"success": True, "team": team_dict})
    except Exception as e:
        logger.error(f"Error getting team {team_id}: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

def get_matches_this_week(matches):
    one_week_ago = datetime.now() - timedelta(days=7)
    weekly_matches = []

    for m in matches:
        if not m.date:
            continue
        try:
            match_date = datetime.fromisoformat(m.date)
            if match_date >= one_week_ago:
                weekly_matches.append(m)
        except:
            continue

    return weekly_matches

@app.route('/api/teams', methods=['POST'])
def create_team():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"success": False, "error": "Name required"}), 400
    
    name = data['name'].strip()
    if not name:
        return jsonify({"success": False, "error": "Name cannot be empty"}), 400
    
    try:
        team_id = db.create_team(name)
        return jsonify({"success": True, "team_id": team_id, "message": f"Team '{name}' created"}), 201
    except Exception as e:
        logger.error(f"Error creating team: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/teams/<int:team_id>', methods=['PUT'])
def update_team(team_id):
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"success": False, "error": "Name required"}), 400
    
    name = data['name'].strip()
    if not name:
        return jsonify({"success": False, "error": "Name cannot be empty"}), 400
    
    try:
        team = db.get_team(team_id)
        if not team:
            return jsonify({"success": False, "error": "Team not found"}), 404
        
        # Update team name in database (you need to implement this method)
        success = db.update_team(team_id, name)
        if success:
            return jsonify({"success": True, "message": f"Team '{name}' updated"})
        else:
            return jsonify({"success": False, "error": "Failed to update team"}), 500
    except Exception as e:
        logger.error(f"Error updating team: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/teams/<int:team_id>', methods=['DELETE'])
def delete_team(team_id):
    try:
        team = db.get_team(team_id)
        if not team:
            return jsonify({"success": False, "error": "Team not found"}), 404
        
        # Delete team from database (you need to implement this method)
        success = db.delete_team(team_id)
        if success:
            return jsonify({"success": True, "message": "Team deleted successfully"})
        else:
            return jsonify({"success": False, "error": "Failed to delete team"}), 500
    except Exception as e:
        logger.error(f"Error deleting team: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/matches/player/<int:player_id>')
def get_player_recent_matches(player_id):
    try:
        conn = db._get_conn()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT 
                m.id, m.name, m.date,
                bp.runs, bp.balls_faced,
                bw.wickets, bw.runs_conceded
            FROM matches m
            LEFT JOIN batting_performances bp 
                ON m.id = bp.match_id AND bp.player_id = ?
            LEFT JOIN bowling_performances bw 
                ON m.id = bw.match_id AND bw.player_id = ?
            WHERE bp.player_id IS NOT NULL 
               OR bw.player_id IS NOT NULL
            ORDER BY m.date DESC
            LIMIT 3
        """, (player_id, player_id))

        rows = cursor.fetchall()
        conn.close()

        matches = []
        for row in rows:
            matches.append({
                "id": row["id"],
                "name": row["name"],
                "date": row["date"],
                "runs": row["runs"],
                "balls_faced": row["balls_faced"],
                "wickets": row["wickets"],
                "runs_conceded": row["runs_conceded"]
            })

        return jsonify({
            "success": True,
            "matches": matches
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "matches": []
        }), 500
    

def build_cricket_context():
    players = db.get_players()
    teams = db.get_teams()
    matches = db.get_matches()

    weekly_matches = get_matches_this_week(matches)
    weekly_match_ids = [m.id for m in weekly_matches]

    context = {
        "total_teams": len(teams),
        "total_players": len(players),
        "total_matches": len(matches),
        "weekly_matches": len(weekly_matches),
        "weekly_batsmen": [],
        "weekly_bowlers": []
    }

    for player in players:
        stats = analytics.calculate_player_stats(player.id)
        if not stats:
            continue

        # ✅ Weekly batting
        if stats.total_runs and stats.total_runs > 0:
            context["weekly_batsmen"].append({
                "name": player.name,
                "runs": stats.total_runs,
                "average": round(stats.batting_average, 1) if stats.batting_average else 0,
                "strike_rate": round(stats.strike_rate, 1) if stats.strike_rate else 0
            })

        # ✅ Weekly bowling
        if stats.total_wickets and stats.total_wickets > 0:
            context["weekly_bowlers"].append({
                "name": player.name,
                "wickets": stats.total_wickets,
                "average": round(stats.bowling_average, 1) if stats.bowling_average else 0,
                "economy": round(stats.economy_rate, 1) if stats.economy_rate else 0
            })

    # Sort & trim
    context["weekly_batsmen"] = sorted(
        context["weekly_batsmen"],
        key=lambda x: x["runs"],
        reverse=True
    )[:5]

    context["weekly_bowlers"] = sorted(
        context["weekly_bowlers"],
        key=lambda x: x["wickets"],
        reverse=True
    )[:5]

    return context



@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        user_msg = request.json.get('message', '').strip()
        if not user_msg:
            return jsonify({"reply": "Please enter a message"}), 400

        # 🔹 Build project-specific context
        context = build_cricket_context()

        system_prompt = f"""
You are Cricket Coach Pro AI.

You MUST answer strictly using the provided project data.
If data is missing or insufficient, say: "Not enough data available".

PROJECT SUMMARY:
- Teams: {context['total_teams']}
- Players: {context['total_players']}
- Total Matches: {context['total_matches']}
- Matches This Week: {context['weekly_matches']}

WEEKLY TOP BATSMEN:
{json.dumps(context['weekly_batsmen'], indent=2)}

WEEKLY TOP BOWLERS:
{json.dumps(context['weekly_bowlers'], indent=2)}

STRICT RULES:
- Use ONLY the above data
- If weekly_matches == 0 → say "No matches played this week"
- NEVER invent player names
- NEVER invent stats

PROJECT SUMMARY:
- Teams: {context['total_teams']}
- Players: {context['total_players']}
- Total Matches: {context['total_matches']}
- Matches This Week: {context['weekly_matches']}

WEEKLY TOP BATSMEN:
{json.dumps(context['weekly_batsmen'], indent=2)}

WEEKLY TOP BOWLERS:
{json.dumps(context['weekly_bowlers'], indent=2)}

STRICT RULES:
- Use ONLY the data provided above
- If weekly_matches == 0, say: "No matches were played this week"
- NEVER invent players
- NEVER invent statistics
- Prefer bullet points


RULES:
- Do NOT invent players or stats
- Prefer bullet points
- Be concise and actionable
"""

        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.4,   # 🔥 lower = factual
            max_tokens=400,
            stream=True
        )

        final_reply = ""

        for chunk in completion:
            choices = getattr(chunk, "choices", None)
            if not choices:
                continue

            delta = getattr(choices[0], "delta", None)
            if not delta:
                continue

            if getattr(delta, "reasoning_content", None):
                continue

            content = getattr(delta, "content", None)
            if content:
                final_reply += content

        return jsonify({
            "reply": final_reply.strip() or
                     "Not enough data available to answer this."
        })

    except Exception as e:
        print("CHAT ERROR:", repr(e))
        return jsonify({
            "reply": "AI service failed. Please try again."
        }), 500

@app.route('/api/players', methods=['GET'])
def get_players():
    try:
        team_id = request.args.get('team_id', type=int)
        raw_players = db.get_players(team_id)

        enriched_players = []

        for player in raw_players:
            # Get analytics data
            perf_data = analytics.calculate_player_stats(player.id)

            # Base player data
            player_dict = player.to_dict()

            if perf_data:
                player_dict.update({
                    # ⭐ CORE FIX (THIS WAS MISSING)
                    'total_matches': perf_data.total_matches or 0,

                    # Batting
                    'batting_average': round(perf_data.batting_average, 1)
                        if perf_data.batting_average else 0.0,
                    'strike_rate': round(perf_data.strike_rate, 1)
                        if perf_data.strike_rate else 0.0,
                    'total_runs': perf_data.total_runs or 0,

                    # Bowling
                    'bowling_average': round(perf_data.bowling_average, 1)
                        if perf_data.bowling_average else 0.0,
                    'economy_rate': round(perf_data.economy_rate, 1)
                        if perf_data.economy_rate else 0.0,
                    'total_wickets': perf_data.total_wickets or 0,
                })
            else:
                # Player exists but has no match data
                player_dict.update({
                    'total_matches': 0,
                    'batting_average': 0.0,
                    'bowling_average': 0.0,
                    'strike_rate': 0.0,
                    'economy_rate': 0.0,
                    'total_runs': 0,
                    'total_wickets': 0,
                })

            enriched_players.append(player_dict)

        return jsonify({
            "success": True,
            "players": enriched_players,
            "count": len(enriched_players)
        })

    except Exception as e:
        logger.error(f"Error getting players: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "players": [],
            "count": 0
        }), 500

@app.route('/api/players', methods=['POST'])
def create_player():
    data = request.get_json()
    required = ['name', 'role', 'team_id']
    if not all(k in data for k in required):
        return jsonify({"success": False, "error": "Missing fields"}), 400
    
    # FIX: Allow all four roles
    valid_roles = ['batsman', 'bowler', 'all-rounder', 'wicket-keeper']
    if data['role'] not in valid_roles:
        return jsonify({"success": False, "error": f"Role must be one of: {', '.join(valid_roles)}"}), 400
    
    try:
        player_id = db.create_player(data['name'], data['role'], data['team_id'])
        return jsonify({"success": True, "player_id": player_id})
    except Exception as e:
        logger.error(f"Error creating player: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/matches', methods=['GET'])
def get_matches():
    try:
        team_id = request.args.get('team_id', type=int)
        limit = request.args.get('limit', type=int, default=10)

        # Get matches (handles both old and new schema via db.get_matches())
        matches = db.get_matches(team_id)

        if not matches:
            return jsonify({
                "success": True,
                "matches": [],
                "count": 0
            })

        # Sort by date descending
        matches.sort(key=lambda x: x.date or datetime.now().isoformat(), reverse=True)

        # Limit results
        matches = matches[:limit]

        enriched_matches = []

        for match in matches:
            match_dict = match.to_dict()

            # Resolve team names
            team1_name = "Unknown Team"
            team2_name = "Unknown Team"

            if hasattr(match, 'team1_id') and match.team1_id:
                team1 = db.get_team(match.team1_id)
                team1_name = team1.name if team1 else f"Team {match.team1_id}"
            elif hasattr(match, 'team_id') and match.team_id:
                team = db.get_team(match.team_id)
                team1_name = team.name if team else f"Team {match.team_id}"

            if hasattr(match, 'team2_id') and match.team2_id:
                team2 = db.get_team(match.team2_id)
                team2_name = team2.name if team2 else f"Team {match.team2_id}"

            match_dict.update({
                'team1': team1_name,
                'team2': team2_name,
                'type': match_dict.get('type', 'T20'),
                'score1': match_dict.get('score1', '0/0'),
                'score2': match_dict.get('score2', '0/0'),
                'run_rate1': float(match_dict.get('run_rate1', 0.0)),
                'run_rate2': float(match_dict.get('run_rate2', 0.0)),
                'result': match_dict.get('result', 'No result'),
                'mom': match_dict.get('mom', '')
            })

            # === REAL PERFORMANCE AGGREGATION ===
            # === REAL TEAM RUNS, WICKETS & AUTO RESULT ===
            try:
                conn = db._get_conn()
                cursor = conn.cursor()

                # Team 1 (batting runs + wickets lost via ducks)
                # Team 1 (runs + wickets lost = number of batting performances recorded)
                team1_id_for_query = match.team1_id or match.team_id  # fallback for old schema
                cursor.execute("""
                    SELECT COALESCE(SUM(bp.runs), 0) AS runs,
                           COUNT(*) AS batsmen_out
                    FROM batting_performances bp
                    JOIN players p ON bp.player_id = p.id
                    WHERE bp.match_id = ? AND p.team_id = ?
                """, (match.id, team1_id_for_query))
                team1_data = cursor.fetchone()
                team1_runs = team1_data['runs'] if team1_data else 0
                team1_wkts = team1_data['batsmen_out'] if team1_data else 0  # FIXED: 'batsmen_out'

                # Team 2
                team2_runs = team2_wkts = 0
                if match.team2_id:
                    cursor.execute("""
                        SELECT COALESCE(SUM(bp.runs), 0) AS runs,
                               COUNT(*) AS batsmen_out
                        FROM batting_performances bp
                        JOIN players p ON bp.player_id = p.id
                        WHERE bp.match_id = ? AND p.team_id = ?
                    """, (match.id, match.team2_id))
                    team2_data = cursor.fetchone()
                    team2_runs = team2_data['runs'] if team2_data else 0
                    team2_wkts = team2_data['batsmen_out'] if team2_data else 0  # FIXED: 'batsmen_out'
                else:
                    team2_runs = team2_wkts = 0

                # Auto result
                if team1_runs > team2_runs and team2_runs > 0:
                    result = f"{team1_name} won by {team1_runs - team2_runs} runs"
                elif team2_runs > team1_runs and team1_runs > 0:
                    result = f"{team2_name} won by {team2_runs - team1_runs} runs"
                elif team1_runs == team2_runs and team1_runs > 0:
                    result = "Match tied"
                else:
                    result = "No result"

                conn.close()
            except Exception as perf_error:
                logger.warning(f"Score calc error for match {match.id}: {perf_error}")
                team1_runs = team2_runs = team1_wkts = team2_wkts = 0
                result = "No result"

            # Update scores & result
            match_dict.update({
                'score1': f"{team1_runs}/{team1_wkts}",
                'score2': f"{team2_runs}/{team2_wkts}",
                'result': result,
                'total_runs': team1_runs + team2_runs,
            })
            enriched_matches.append(match_dict)

        return jsonify({
            "success": True,
            "matches": enriched_matches,
            "count": len(enriched_matches)
        })

    except Exception as e:
        logger.error(f"Error in get_matches: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "matches": [],
            "count": 0
        }), 500

@app.route('/api/stats')
def get_stats():
    teams = db.get_teams()
    players = db.get_players()
    matches = db.get_matches()

    total_runs = 0
    match_count = 0

    for match in matches:
        try:
            conn = db._get_conn()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COALESCE(SUM(runs), 0)
                FROM batting_performances
                WHERE match_id = ?
            """, (match.id,))
            runs = cursor.fetchone()[0]
            total_runs += runs
            match_count += 1
            conn.close()
        except:
            pass

    avg_score = round(total_runs / match_count, 1) if match_count else 0

    # Calculate avg rating from players
    total_rating = 0
    rated = 0
    analytics_engine = analytics

    for p in players:
        stats = analytics_engine.calculate_player_stats(p.id)
        if stats and stats.batting_average:
            total_rating += stats.batting_average / 10
            rated += 1

    avg_rating = round(total_rating / rated, 1) if rated else 0

    return jsonify({
        'success': True,
        'teams': len(teams),
        'players': len(players),
        'matches': len(matches),
        'avg_rating': avg_rating,
        'avg_score': avg_score
    })

@app.route('/api/matches', methods=['POST'])
def api_create_match():
    """API endpoint to create a new match"""
    try:
        data = request.get_json()
        
        name = data.get('name', '').strip()
        date = data.get('date')
        team1_id = data.get('team1_id')
        team2_id = data.get('team2_id')

        # Validation
        if not name:
            return jsonify({'success': False, 'error': 'Match name is required'}), 400
        if not date:
            return jsonify({'success': False, 'error': 'Date is required'}), 400
        if not team1_id or not team2_id:
            return jsonify({'success': False, 'error': 'Both teams must be selected'}), 400
        if int(team1_id) == int(team2_id):
            return jsonify({'success': False, 'error': 'Teams must be different'}), 400

        # Call your DB function - this likely returns the new match ID (int)
        new_match_id = db.create_match(
            name=name,
            date=date,
            team1_id=int(team1_id),
            team2_id=int(team2_id)
        )

        # Handle both cases: if it returns int or Match object
        if isinstance(new_match_id, int):
            match_id = new_match_id
        elif hasattr(new_match_id, 'id'):
            match_id = new_match_id.id
        else:
            return jsonify({'success': False, 'error': 'Invalid response from database'}), 500

        logger.info(f"Match created: {name} ({team1_id} vs {team2_id}) - ID: {match_id}")

        return jsonify({
            'success': True,
            'match_id': match_id,
            'message': 'Match created successfully'
        })

    except Exception as e:
        logger.error(f"Error creating match: {e}")
        return jsonify({'success': False, 'error': 'Failed to create match'}), 500

@app.route('/api/performances/batting', methods=['POST'])
def add_batting():
    data = request.get_json()
    required = ['match_id', 'player_id', 'runs', 'balls_faced']
    if not all(k in data for k in required):
        return jsonify({"success": False, "error": "Missing fields"}), 400
    try:
        db.add_batting_performance(data['match_id'], data['player_id'], data['runs'], data['balls_faced'])
        return jsonify({"success": True, "message": "Batting performance added"})
    except Exception as e:
        logger.error(f"Error adding batting: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/performances/bowling', methods=['POST'])
def add_bowling():
    data = request.get_json()
    required = ['match_id', 'player_id', 'overs', 'wickets', 'runs_conceded']
    if not all(k in data for k in required):
        return jsonify({"success": False, "error": "Missing fields"}), 400
    try:
        db.add_bowling_performance(data['match_id'], data['player_id'], data['overs'], data['wickets'], data['runs_conceded'])
        return jsonify({"success": True, "message": "Bowling performance added"})
    except Exception as e:
        logger.error(f"Error adding bowling: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/analytics/player/<int:player_id>')
def player_analytics(player_id):
    try:
        stats = analytics.calculate_player_stats(player_id)
        if not stats:
            return jsonify({"success": False, "error": "Player not found"}), 404
        
        return jsonify({
            "success": True,
            "player": {
                "id": player_id,
                "name": stats.player_name,
                "role": stats.role
            },
            "stats": {
                "total_matches": stats.total_matches or 0,
                "batting_average": round(stats.batting_average, 1) if stats.batting_average else 0.0,
                "strike_rate": round(stats.strike_rate, 1) if stats.strike_rate else 0.0,
                "bowling_average": round(stats.bowling_average, 1) if stats.bowling_average else 0.0,
                "economy_rate": round(stats.economy_rate, 1) if stats.economy_rate else 0.0,
                "total_runs": stats.total_runs or 0,
                "total_wickets": stats.total_wickets or 0,
                "recent_runs": stats.recent_runs or [],
                "recent_wickets": stats.recent_wickets or []
            }
        })
    except Exception as e:
        logger.error(f"Error getting player analytics: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/predict/player/<int:player_id>')
def predict_player(player_id):
    try:
        prediction = analytics.predict_player_performance(player_id)
        if not prediction:
            return jsonify({"success": False, "error": "Player not found"}), 404
        return jsonify({"success": True, "prediction": prediction.to_dict()})
    except Exception as e:
        logger.error(f"Error predicting player: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/recommend/team/<int:team_id>')
def team_recommendation(team_id):
    try:
        rec = analytics.recommend_team_selection(team_id)
        return jsonify({"success": True, "recommendation": rec.to_dict()})
    except Exception as e:
        logger.error(f"Error generating recommendation: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Cricket Coach Pro...")
    print("📊 Dashboard: http://127.0.0.1:5000/")
    print("👥 Teams: http://127.0.0.1:5000/teams")
    print("⚡ API Base: http://127.0.0.1:5000/api/")
    app.run(debug=True, port=5000)