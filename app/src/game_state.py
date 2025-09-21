"""Game state persistence."""
import json
import os
from config import LIVES_START

STATE_FILE = "/tmp/cman_state.json"

def load_game_state():
    """Load score and lives from state file."""
    try:
        with open(STATE_FILE, 'r') as f:
            state = json.load(f)
            return state.get('score', 0), state.get('lives', LIVES_START)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0, LIVES_START

def save_game_state(score, lives):
    """Save score and lives to state file."""
    state = {'score': score, 'lives': lives}
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def clear_game_state():
    """Remove state file (game over)."""
    try:
        os.remove(STATE_FILE)
    except FileNotFoundError:
        pass