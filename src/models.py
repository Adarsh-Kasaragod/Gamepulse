# src/models.py
from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict, Any
from datetime import datetime

@dataclass
class Team:
    id: int
    name: str
    created_at: Optional[str] = None
    status: Optional[str] = 'active'
    description: Optional[str] = None
    rating: Optional[float] = 5.0
    player_count: Optional[int] = 0
    match_count: Optional[int] = 0
    specialization: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "description": self.description,
            "rating": self.rating,
            "player_count": self.player_count,
            "match_count": self.match_count,
            "specialization": self.specialization,
            "created_at": self.created_at
        }

@dataclass
class Player:
    id: int
    name: str
    role: str  # 'batsman', 'bowler', 'all-rounder', or 'wicket-keeper'
    team_id: int
    created_at: Optional[str] = None
    specialization: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "team_id": self.team_id,
            "specialization": self.specialization,
            "created_at": self.created_at
        }

@dataclass
class Match:
    id: int
    name: str
    date: str
    # Keeping team_id for backward compatibility
    team_id: Optional[int] = None
    team1_id: Optional[int] = None
    team2_id: Optional[int] = None
    type: Optional[str] = 'T20'
    score1: Optional[str] = '0/0'
    score2: Optional[str] = '0/0'
    run_rate1: Optional[float] = 0.0
    run_rate2: Optional[float] = 0.0
    result: Optional[str] = None
    mom: Optional[str] = None
    created_at: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "date": self.date,
            "team_id": self.team_id,
            "team1_id": self.team1_id,
            "team2_id": self.team2_id,
            "type": self.type,
            "score1": self.score1,
            "score2": self.score2,
            "run_rate1": self.run_rate1,
            "run_rate2": self.run_rate2,
            "result": self.result,
            "mom": self.mom,
            "created_at": self.created_at
        }

@dataclass
class PlayerStats:
    player_id: int
    player_name: str
    role: str
    total_matches: int
    total_runs: int = 0
    total_balls_faced: int = 0
    batting_average: float = 0.0
    strike_rate: float = 0.0
    total_wickets: int = 0
    total_overs: float = 0.0
    total_runs_conceded: int = 0
    bowling_average: float = 0.0
    economy_rate: float = 0.0
    recent_runs: List[int] = field(default_factory=list)
    recent_wickets: List[int] = field(default_factory=list)

@dataclass
class Prediction:
    player_id: int
    player_name: str
    role: str
    predicted_runs: Optional[float] = None
    predicted_wickets: Optional[float] = None
    confidence_score: float = 75.0
    explanation: str = ""

    def to_dict(self) -> Dict:
        return {
            'player_id': self.player_id,
            'player_name': self.player_name,
            'role': self.role,
            'predicted_runs': round(self.predicted_runs, 1) if self.predicted_runs else None,
            'predicted_wickets': round(self.predicted_wickets, 1) if self.predicted_wickets else None,
            'confidence_score': round(self.confidence_score, 1),
            'explanation': self.explanation
        }

@dataclass
class Recommendation:
    team_id: int
    match_date: str
    top_batsmen: List[Dict[str, Any]] = field(default_factory=list)
    top_bowlers: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return asdict(self)