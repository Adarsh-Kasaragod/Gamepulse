# src/analytics.py
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from .models import PlayerStats, Prediction, Recommendation
from .database import CricketDatabase
import logging

logger = logging.getLogger(__name__)

class CricketAnalytics:
    def __init__(self, db: CricketDatabase):
        self.db = db
    
    def calculate_player_stats(self, player_id: int) -> Optional[PlayerStats]:
        try:
            perf_data = self.db.get_player_performances(player_id)
            if not perf_data:
                return None
            
            player_info = perf_data["player"]
            batting_history = perf_data["batting_history"]
            bowling_history = perf_data["bowling_history"]
            
            # Calculate batting stats
            total_runs = sum([b["runs"] for b in batting_history])
            total_balls_faced = sum([b["balls_faced"] for b in batting_history])
            total_matches = len(batting_history) if batting_history else len(bowling_history)
            
            batting_average = 0.0
            if batting_history and len([b for b in batting_history if b["runs"] > 0]) > 0:
                batting_average = total_runs / len([b for b in batting_history if b["runs"] > 0])
            
            strike_rate = 0.0
            if total_balls_faced > 0:
                strike_rate = (total_runs / total_balls_faced) * 100
            
            # Calculate bowling stats
            total_wickets = sum([b["wickets"] for b in bowling_history])
            total_overs = sum([b["overs"] for b in bowling_history])
            total_runs_conceded = sum([b["runs_conceded"] for b in bowling_history])
            
            bowling_average = 0.0
            if total_wickets > 0:
                bowling_average = total_runs_conceded / total_wickets
            
            economy_rate = 0.0
            if total_overs > 0:
                economy_rate = total_runs_conceded / total_overs
            
            # Get recent performance (last 5 matches)
            recent_runs = [b["runs"] for b in batting_history[:5]]
            recent_wickets = [b["wickets"] for b in bowling_history[:5]]
            
            return PlayerStats(
                player_id=player_id,
                player_name=player_info["name"],
                role=player_info["role"],
                total_matches=total_matches,
                total_runs=total_runs,
                total_balls_faced=total_balls_faced,
                batting_average=batting_average,
                strike_rate=strike_rate,
                total_wickets=total_wickets,
                total_overs=total_overs,
                total_runs_conceded=total_runs_conceded,
                bowling_average=bowling_average,
                economy_rate=economy_rate,
                recent_runs=recent_runs,
                recent_wickets=recent_wickets
            )
        except Exception as e:
            logger.error(f"Error calculating player stats: {e}")
            return None
    
    def predict_player_performance(self, player_id: int) -> Optional[Prediction]:
        try:
            stats = self.calculate_player_stats(player_id)
            if not stats:
                return None
            
            # Enhanced prediction algorithm
            predicted_runs = self._predict_runs(stats)
            predicted_wickets = self._predict_wickets(stats)
            confidence_score = self._calculate_confidence(stats)
            explanation = self._generate_explanation(stats, predicted_runs, predicted_wickets)
            
            return Prediction(
                player_id=player_id,
                player_name=stats.player_name,
                role=stats.role,
                predicted_runs=predicted_runs,
                predicted_wickets=predicted_wickets,
                confidence_score=confidence_score,
                explanation=explanation
            )
        except Exception as e:
            logger.error(f"Error predicting player performance: {e}")
            # Return a basic prediction
            return Prediction(
                player_id=player_id,
                player_name="Unknown",
                role="player",
                predicted_runs=25.0,
                predicted_wickets=1.5,
                confidence_score=70.0,
                explanation="Basic prediction based on average performance"
            )
    
    def _predict_runs(self, stats: PlayerStats) -> float:
        """Predict runs based on historical performance and recent form"""
        if stats.total_matches == 0:
            return 20.0  # Default prediction for new players
        
        base_prediction = stats.batting_average
        
        # Adjust based on recent form
        if stats.recent_runs:
            recent_avg = np.mean(stats.recent_runs)
            # Weight recent form higher (60% recent, 40% overall)
            base_prediction = (recent_avg * 0.6) + (base_prediction * 0.4)
        
        # Add randomness (±25%)
        variation = 0.75 + (np.random.random() * 0.5)
        predicted = base_prediction * variation
        
        # Cap predictions
        if stats.role == 'batsman':
            return min(predicted, 150)  # Cap for batsmen
        elif stats.role == 'bowler':
            return min(predicted, 50)   # Lower cap for bowlers
        else:
            return min(predicted, 80)   # Cap for all-rounders
    
    def _predict_wickets(self, stats: PlayerStats) -> float:
        """Predict wickets based on bowling performance"""
        if stats.total_matches == 0 or stats.bowling_average == 0:
            return 1.0  # Default prediction
        
        # Convert bowling average to expected wickets
        # Lower average = more wickets
        base_prediction = 30 / stats.bowling_average
        
        # Adjust based on recent form
        if stats.recent_wickets:
            recent_avg = np.mean(stats.recent_wickets)
            base_prediction = (recent_avg * 0.7) + (base_prediction * 0.3)
        
        # Add randomness (±30%)
        variation = 0.7 + (np.random.random() * 0.6)
        predicted = base_prediction * variation
        
        # Cap predictions
        return min(predicted, 6.0)  # Maximum 6 wickets in T20
    
    def _calculate_confidence(self, stats: PlayerStats) -> float:
        """Calculate prediction confidence score"""
        confidence = 70.0  # Base confidence
        
        # More matches = higher confidence
        if stats.total_matches >= 20:
            confidence += 15
        elif stats.total_matches >= 10:
            confidence += 10
        elif stats.total_matches >= 5:
            confidence += 5
        
        # Consistent performance = higher confidence
        if stats.recent_runs and len(stats.recent_runs) >= 3:
            std_dev = np.std(stats.recent_runs)
            if std_dev < 15:
                confidence += 5
        
        # Cap confidence
        return min(confidence, 95.0)
    
    def _generate_explanation(self, stats: PlayerStats, predicted_runs: float, predicted_wickets: float) -> str:
        """Generate human-readable explanation for prediction"""
        explanations = []
        
        if stats.role == 'batsman':
            if predicted_runs > 40:
                explanations.append("Excellent batting form detected.")
            elif predicted_runs > 25:
                explanations.append("Good batting performance expected.")
            else:
                explanations.append("May find scoring difficult.")
        
        if stats.role == 'bowler':
            if predicted_wickets > 2.5:
                explanations.append("Strong wicket-taking threat.")
            elif predicted_wickets > 1.5:
                explanations.append("Can be effective in the middle overs.")
            else:
                explanations.append("May need support from other bowlers.")
        
        # Add form insights
        if stats.recent_runs:
            last_3_avg = np.mean(stats.recent_runs[:3]) if len(stats.recent_runs) >= 3 else 0
            if last_3_avg > stats.batting_average * 1.2:
                explanations.append("Currently in excellent form.")
            elif last_3_avg < stats.batting_average * 0.8:
                explanations.append("Recent form has dipped.")
        
        # Add consistency note
        if stats.total_matches > 10:
            explanations.append(f"Based on {stats.total_matches} matches of data.")
        
        return " ".join(explanations) if explanations else "Prediction based on historical performance."
    
    def recommend_team_selection(self, team_id: int) -> Recommendation:
        """Generate team selection recommendations"""
        players = self.db.get_players(team_id)
        
        # Sort players by performance
        player_stats = []
        for player in players:
            stats = self.calculate_player_stats(player.id)
            if stats:
                player_stats.append((player, stats))
        
        # Get top batsmen and bowlers
        top_batsmen = sorted(
            [(p, s) for p, s in player_stats if s.batting_average > 0],
            key=lambda x: x[1].batting_average,
            reverse=True
        )[:3]
        
        top_bowlers = sorted(
            [(p, s) for p, s in player_stats if s.bowling_average > 0],
            key=lambda x: 1/x[1].bowling_average if x[1].bowling_average > 0 else 0,
            reverse=True
        )[:3]
        
        return Recommendation(
            team_id=team_id,
            match_date=datetime.now().strftime("%Y-%m-%d"),
            top_batsmen=[{
                'player_id': p.id,
                'name': p.name,
                'role': p.role,
                'batting_average': round(s.batting_average, 1),
                'strike_rate': round(s.strike_rate, 1)
            } for p, s in top_batsmen],
            top_bowlers=[{
                'player_id': p.id,
                'name': p.name,
                'role': p.role,
                'bowling_average': round(s.bowling_average, 1),
                'economy_rate': round(s.economy_rate, 1)
            } for p, s in top_bowlers]
        )
    
    def calculate_trend_analysis(self, player_id: int) -> Dict:
        """Calculate performance trends over time"""
        stats = self.calculate_player_stats(player_id)
        if not stats:
            return {}
        
        trend_data = {
            'batting_trend': 'stable',
            'bowling_trend': 'stable',
            'form_indicator': 'neutral',
            'improvement_areas': []
        }
        
        # Analyze batting trend
        if stats.recent_runs and len(stats.recent_runs) >= 3:
            recent_avg = np.mean(stats.recent_runs[:3])
            overall_avg = stats.batting_average
            
            if recent_avg > overall_avg * 1.15:
                trend_data['batting_trend'] = 'improving'
            elif recent_avg < overall_avg * 0.85:
                trend_data['batting_trend'] = 'declining'
        
        # Analyze bowling trend
        if stats.recent_wickets and len(stats.recent_wickets) >= 3:
            recent_avg = np.mean(stats.recent_wickets[:3])
            # Estimate overall wickets per match
            overall_wpm = 30 / stats.bowling_average if stats.bowling_average > 0 else 0
            
            if recent_avg > overall_wpm * 1.2:
                trend_data['bowling_trend'] = 'improving'
            elif recent_avg < overall_wpm * 0.8:
                trend_data['bowling_trend'] = 'declining'
        
        # Determine form indicator
        improving_count = sum([1 for trend in [trend_data['batting_trend'], trend_data['bowling_trend']] if trend == 'improving'])
        declining_count = sum([1 for trend in [trend_data['batting_trend'], trend_data['bowling_trend']] if trend == 'declining'])
        
        if improving_count > declining_count:
            trend_data['form_indicator'] = 'positive'
        elif declining_count > improving_count:
            trend_data['form_indicator'] = 'negative'
        
        # Identify improvement areas
        if stats.strike_rate < 120 and stats.role in ['batsman', 'all-rounder']:
            trend_data['improvement_areas'].append('Strike rate needs improvement')
        if stats.economy_rate > 8 and stats.role in ['bowler', 'all-rounder']:
            trend_data['improvement_areas'].append('Economy rate is high')
        if stats.batting_average < 25 and stats.role in ['batsman', 'all-rounder']:
            trend_data['improvement_areas'].append('Batting average is low')
        
        return trend_data