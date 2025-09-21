"""High score management."""
import json
import os
from datetime import datetime

SCORES_FILE = "/data/high_scores.json"

def load_high_scores():
    """Load high scores from file."""
    try:
        with open(SCORES_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_high_scores(scores):
    """Save high scores to file."""
    os.makedirs(os.path.dirname(SCORES_FILE), exist_ok=True)
    with open(SCORES_FILE, 'w') as f:
        json.dump(scores, f, indent=2)

def add_high_score(score, initials="???"):
    """Add a new high score and return if it made the top 10."""
    scores = load_high_scores()
    entry = {"score": score, "initials": initials, "date": datetime.now().isoformat()[:19]}
    scores.append(entry)
    scores.sort(key=lambda x: x["score"], reverse=True)
    scores = scores[:10]  # Keep top 10
    save_high_scores(scores)
    return entry in scores

def is_high_score(score):
    """Check if score qualifies for high score list."""
    scores = load_high_scores()
    return len(scores) < 10 or score > min(s["score"] for s in scores)

def get_top_scores(limit=10):
    """Get top scores."""
    scores = load_high_scores()
    return scores[:limit]