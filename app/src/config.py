"""Game configuration constants."""

# Game timing
FPS = 30
PAC_SPEED = 7
GHOST_SPEED = 6
POWER_TIME = 8.0
HOME_TIME = 2.0

# Game mechanics
LIVES_START = 3
COLLISION_THRESHOLD = 0.9
VERTICAL_SPEED_MULT = 0.7

# Display characters
PAC_CHARS = {(1,0): ">", (-1,0): "<", (0,-1): "^", (0,1): "v"}
PAC_CHAR_IDLE = "C"
GHOST_CHAR = "M"

# Unicode walls
WALL = set("─│┌┐└┘├┤┬┴┼")