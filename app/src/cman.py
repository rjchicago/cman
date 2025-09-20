#!/usr/bin/env python3
# cman with external level files (plain text in ./levels).
# - Prompts for a level name; loads levels/<name>.txt
# - Enter with no input -> first available level
# - Invalid name -> list available levels, re-prompt
# Controls: arrows/WASD. Quit: q

import curses, time, random, locale, os, sys

locale.setlocale(locale.LC_ALL, "")

# ---------------- Tunables ----------------
FPS         = 30
PAC_SPEED   = 7
GHOST_SPEED = 6
POWER_TIME  = 8.0
LIVES_START = 3
COLLISION_THRESHOLD = 0.9
VERTICAL_SPEED_MULT = 0.7
HOME_TIME   = 2.0
PAC_CHARS   = {(1,0): ">", (-1,0): "<", (0,-1): "^", (0,1): "v"}
PAC_CHAR_IDLE = "C"
GHOST_CHAR  = "M"

# Unicode walls we treat as solid
WALL = set("─│┌┐└┘├┤┬┴┼")

LEVEL_DIR = os.path.join(os.path.dirname(__file__), "..", "levels")

# ---------------- Level I/O ----------------
def list_level_files():
    if not os.path.isdir(LEVEL_DIR):
        return []
    files = [f for f in os.listdir(LEVEL_DIR) if f.lower().endswith(".txt")]
    files.sort()
    return files

def load_level_file(filename):
    path = os.path.join(LEVEL_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f]
    # Validate rectangular
    if not lines:
        raise ValueError("Level file is empty.")
    width = len(lines[0])
    for i, line in enumerate(lines):
        if len(line) != width:
            raise ValueError(f"Row {i} length {len(line)} != {width} (level must be rectangular)")
    return lines  # list[str]

def get_initial_level():
    """Get initial level from LEVEL env var or return None for default behavior"""
    level_env = os.environ.get('LEVEL')
    if level_env:
        files = list_level_files()
        cand = level_env + ".txt"
        if cand in files:
            return level_env
        else:
            print(f"Warning: Level '{level_env}' not found. Available levels:")
            for f in files:
                print(f"  - {os.path.splitext(f)[0]}")
            print("Falling back to default level selection.")
    return None

def choose_level_interactive():
    files = list_level_files()
    if not files:
        print("No level files found in ./levels.\n"
              "Create at least one .txt file with your map. "
              "Example filenames: classic_28x31.txt, demo_64x64.txt")
        sys.exit(1)

    while True:
        print("\nAvailable levels:")
        for f in files:
            print("  -", os.path.splitext(f)[0])
        inp = input("\nEnter level name (without .txt). Press ENTER to load first: ").strip()
        if inp == "":
            chosen = files[0]
            print(f"Loading: {chosen}")
            return load_level_file(chosen), os.path.splitext(chosen)[0]
        cand = inp + ".txt"
        if cand in files:
            print(f"Loading: {cand}")
            return load_level_file(cand), inp
        else:
            print(f"'{inp}' not found.")
            # loop again to prompt

# ---------------- Helpers (game-agnostic) ----------------
def make_pellet_map(LEVEL):
    pellets, powers = set(), set()
    for y, row in enumerate(LEVEL):
        for x, ch in enumerate(row):
            if ch == '.': pellets.add((x, y))
            elif ch == 'o': powers.add((x, y))
    return pellets, powers

def in_bounds(x, y, W, H): return 0 <= x < W and 0 <= y < H
def is_wall(LEVEL, x, y, W, H):
    if not in_bounds(x, y, W, H): return True
    return LEVEL[y][x] in WALL

def wrap_xy(x, y, W, H):
    # Horizontal wrap: always wrap; to make a tunnel, leave spaces on edges.
    if x < 0: x = W - 1
    if x >= W: x = 0
    # (Keep vertical clamp — classic doesn’t wrap vertically)
    return x, y

def neighbors(LEVEL, x, y, W, H):
    for dx, dy in ((1,0), (-1,0), (0,1), (0,-1)):
        nx, ny = wrap_xy(x + dx, y + dy, W, H)
        if not is_wall(LEVEL, nx, ny, W, H):
            yield nx, ny, (dx, dy)

def manhattan(a,b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

def astar_dir(LEVEL, src, dst, forbid, W, H):
    from heapq import heappush, heappop
    
    start = src
    goal = dst
    
    # Quick fallback for same position
    if start == goal:
        return (0, 0)
    
    open_set = [(0, start, None)]  # (f_score, pos, came_from_dir)
    g_score = {start: 0}
    
    while open_set:
        _, current, from_dir = heappop(open_set)
        
        if current == goal:
            return from_dir if from_dir else (0, 0)
        
        for nx, ny, (dx, dy) in neighbors(LEVEL, current[0], current[1], W, H):
            if forbid and (dx, dy) == forbid:
                continue
                
            neighbor = (nx, ny)
            tentative_g = g_score[current] + 1
            
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                f_score = tentative_g + manhattan(neighbor, goal)
                first_dir = from_dir if from_dir else (dx, dy)
                heappush(open_set, (f_score, neighbor, first_dir))
    
    # Fallback to greedy if A* fails
    x, y = src
    opts = []
    for nx, ny, (dx, dy) in neighbors(LEVEL, x, y, W, H):
        if forbid and (dx, dy) == forbid:
            continue
        d = manhattan((nx, ny), dst)
        opts.append(((dx, dy), d))
    opts.sort(key=lambda t: t[1])
    return opts[0][0] if opts else (0, 0)

def random_dir(LEVEL, src, forbid, W, H):
    x, y = src
    opts = []
    for nx, ny, (dx, dy) in neighbors(LEVEL, x, y, W, H):
        if forbid and (dx, dy) == forbid:
            continue
        opts.append((dx, dy))
    if not opts:
        for nx, ny, (dx, dy) in neighbors(LEVEL, x, y, W, H):
            opts.append((dx, dy))
    return random.choice(opts) if opts else (0, 0)

def step_entity_on_grid(LEVEL, x, y, dx, dy, step, W, H):
    nx, ny = wrap_xy(x + dx * step, y + dy * step, W, H)
    if not is_wall(LEVEL, nx, ny, W, H):
        return nx, ny, dx, dy
    return x, y, 0, 0

# ---------------- Entities ----------------
class Cman:
    def __init__(self, start_pos):
        sx, sy = start_pos
        self.x = float(sx); self.y = float(sy)
        self.dx = 0; self.dy = 0
        self.want = (0, 0)
        self.lives = LIVES_START
        self.power = 0.0
        self.shield = 1.0
    def reset(self, start_pos):
        sx, sy = start_pos
        self.x = float(sx); self.y = float(sy)
        self.dx = 0; self.dy = 0
        self.want = (0, 0)
        self.power = 0.0
        self.shield = 1.0

class Ghost:
    def __init__(self, home_pos, scatter):
        hx, hy = home_pos
        self.home = (hx, hy)
        self.x = float(hx); self.y = float(hy)
        self.dx = 0; self.dy = 0
        self.scatter = scatter
        self.frightened = 0.0
        self.home_timer = 0.0
    def reset(self):
        self.x, self.y = float(self.home[0]), float(self.home[1])
        self.dx = self.dy = 0
        self.frightened = 0.0
        self.home_timer = HOME_TIME

# ---------------- Spawn helpers ----------------
def find_default_spawns(LEVEL):
    """Find spawn points marked with C (cman) and M (ghosts), replace with spaces"""
    H = len(LEVEL); W = len(LEVEL[0])
    
    # Convert LEVEL to mutable list of lists
    level_grid = [list(row) for row in LEVEL]
    
    # Find C marker for cman
    pac = None
    for y in range(H):
        for x in range(W):
            if level_grid[y][x] == 'C':
                pac = (x, y)
                level_grid[y][x] = ' '  # Replace C with space
                break
        if pac: break
    
    # Find M markers for ghosts
    ghost_candidates = []
    for y in range(H):
        for x in range(W):
            if level_grid[y][x] == 'M':
                ghost_candidates.append((x, y))
                level_grid[y][x] = ' '  # Replace M with space
    
    # Update LEVEL back to list of strings
    for y in range(H):
        LEVEL[y] = ''.join(level_grid[y])
    
    # Fallbacks if markers not found
    if pac is None:
        for y in range(H//2, H):
            for x in range(W):
                if LEVEL[y][x] in ('.','o',' '):
                    pac = (x, y); break
            if pac: break
        if pac is None: pac = (1, 1)
    

    
    # Use only the ghosts found (don't force 4)
    ghosts = ghost_candidates
    
    # Use ghost starting positions as scatter targets
    scatters = ghost_candidates
    return pac, ghosts, scatters

# ---------------- Game Loop ----------------
def simulate(stdscr, LEVEL, title):
    H = len(LEVEL); W = len(LEVEL[0])

    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(0)

    # Colors
    if curses.has_colors():
        curses.start_color(); curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_YELLOW, -1)  # Pac
        curses.init_pair(2, curses.COLOR_RED, -1)     # Ghost
        curses.init_pair(3, curses.COLOR_CYAN, -1)    # Frightened
        curses.init_pair(4, curses.COLOR_WHITE, -1)   # Maze/pellets
        PAC_COLOR = curses.color_pair(1)
        GHOST_COLOR = curses.color_pair(2)
        FRIGHT_COL = curses.color_pair(3)
        MAZE_COLOR = curses.color_pair(4)
    else:
        PAC_COLOR = GHOST_COLOR = FRIGHT_COL = MAZE_COLOR = 0

    # Spawns
    pac_start, ghost_starts, scatter_targets = find_default_spawns(LEVEL)
    pac = Cman(pac_start)
    ghosts = [Ghost(ghost_starts[i], scatter_targets[i]) for i in range(len(ghost_starts))]

    pellets, powers = make_pellet_map(LEVEL)

    last = time.perf_counter()
    running = True
    paused = False
    game_started = False
    msg = ""

    while running:
        now = time.perf_counter()
        dt = now - last
        if dt < 1.0 / FPS:
            time.sleep(1.0 / FPS - dt)
            now = time.perf_counter()
            dt = now - last
        last = now

        pac.shield = max(0.0, pac.shield - dt)
        pac.power  = max(0.0, pac.power  - dt)

        # Input
        try:
            ch = stdscr.getch()
        except curses.error:
            ch = -1
        if ch in (ord('q'), ord('Q')):
            break
        elif ch in (ord('p'), ord('P')):
            paused = True
            msg_text = "PAUSED"
            stdscr.addstr(max(1, H//2), max(0, (W - len(msg_text)) // 2), msg_text)
            stdscr.refresh()
            stdscr.nodelay(False)
            stdscr.getch()
            stdscr.nodelay(True)
            paused = False
            last = time.perf_counter()  # Reset timer to avoid big dt jump
            continue

        
        if paused:
            continue
            
        want = pac.want
        if ch in (curses.KEY_UP, ord('w'), ord('W')):    want = (0, -1)
        elif ch in (curses.KEY_DOWN, ord('s'), ord('S')): want = (0, 1)
        elif ch in (curses.KEY_LEFT, ord('a'), ord('A')): want = (-1, 0)
        elif ch in (curses.KEY_RIGHT, ord('d'), ord('D')):want = (1, 0)
        pac.want = want
        if want != (0, 0):
            nx, ny = wrap_xy(pac.x + want[0], pac.y + want[1], W, H)
            if not is_wall(LEVEL, int(nx), int(ny), W, H):
                pac.dx, pac.dy = want
                game_started = True  # Start game when cman first moves

        # Move cman
        if pac.dx != 0 or pac.dy != 0:
            # Half speed for vertical movement (terminal cells are rectangular)
            speed_x = PAC_SPEED * dt
            speed_y = PAC_SPEED * dt * VERTICAL_SPEED_MULT
            new_x = pac.x + pac.dx * speed_x
            new_y = pac.y + pac.dy * speed_y
            new_x, new_y = wrap_xy(new_x, new_y, W, H)
            if not is_wall(LEVEL, int(new_x), int(new_y), W, H):
                pac.x, pac.y = new_x, new_y

        # Eat pellets/powers
        pac_grid = (int(pac.x), int(pac.y))
        if pac_grid in pellets:
            pellets.remove(pac_grid)
        if pac_grid in powers:
            powers.remove(pac_grid)
            pac.power = POWER_TIME
            for g in ghosts: g.frightened = POWER_TIME

        # Collisions (check immediately after power pellet to allow instant capture)
        for g in ghosts:
            # Use distance-based collision detection for better capture
            distance = abs(g.x - pac.x) + abs(g.y - pac.y)
            if distance < COLLISION_THRESHOLD:
                if g.frightened > 0:
                    g.reset()
                else:
                    # Only check shield for dangerous ghost collisions
                    if pac.shield > 0:
                        continue
                    pac.lives -= 1
                    if pac.lives < 0:
                        msg = "GAME OVER"
                        running = False
                        break
                    pac.reset(pac_start)
                    for gg in ghosts: gg.reset()
                    time.sleep(0.5)
                    break

        if not running:
            break

        # Ghosts (only move after game starts)
        if game_started:
            for g in ghosts:
                # Update home timer
                if g.home_timer > 0:
                    g.home_timer = max(0.0, g.home_timer - dt)
                    # Move left/right in home while waiting
                    at_intersection = abs(g.x - round(g.x)) < 0.1 and abs(g.y - round(g.y)) < 0.1
                    if at_intersection or (g.dx == 0 and g.dy == 0):
                        # Only move horizontally in home
                        if g.dx == 0:  # Start moving
                            g.dx = 1 if random.random() > 0.5 else -1
                            g.dy = 0
                        else:  # Reverse direction if hit wall or edge
                            new_x = g.x + g.dx
                            if is_wall(LEVEL, int(new_x), int(g.y), W, H) or new_x < 0 or new_x >= W:
                                g.dx = -g.dx
                    # Move the ghost
                    if g.dx != 0 or g.dy != 0:
                        speed_x = GHOST_SPEED * dt
                        speed_y = GHOST_SPEED * dt * VERTICAL_SPEED_MULT
                        new_x = g.x + g.dx * speed_x
                        new_y = g.y + g.dy * speed_y
                        new_x, new_y = wrap_xy(new_x, new_y, W, H)
                        if not is_wall(LEVEL, int(new_x), int(new_y), W, H):
                            g.x, g.y = new_x, new_y
                    continue
                
                # Only change direction at grid intersections or when stuck
                at_intersection = abs(g.x - round(g.x)) < 0.1 and abs(g.y - round(g.y)) < 0.1
                
                if at_intersection or (g.dx == 0 and g.dy == 0):
                    forbid = (-g.dx, -g.dy) if (g.dx, g.dy) != (0, 0) else None
                    if g.frightened > 0:
                        ddx, ddy = random_dir(LEVEL, (int(g.x), int(g.y)), forbid, W, H)
                    else:
                        # Check if ghost is in home area (near center)
                        in_home = abs(g.x - W//2) < 3 and abs(g.y - H//2) < 3
                        if in_home:
                            # Exit home by moving toward top of map first
                            exit_target = (int(g.x), max(0, H//2 - 4))
                            ddx, ddy = astar_dir(LEVEL, (int(g.x), int(g.y)), exit_target, forbid, W, H)
                        else:
                            # Always chase cman with A* pathfinding
                            target = (int(pac.x), int(pac.y))
                            ddx, ddy = astar_dir(LEVEL, (int(g.x), int(g.y)), target, forbid, W, H)
                    # If ghost is stuck, force a random direction
                    if ddx == 0 and ddy == 0:
                        ddx, ddy = random_dir(LEVEL, (int(g.x), int(g.y)), None, W, H)
                    g.dx, g.dy = ddx, ddy
                
                if g.dx != 0 or g.dy != 0:
                    # Half speed for vertical movement (terminal cells are rectangular)
                    speed_x = GHOST_SPEED * dt
                    speed_y = GHOST_SPEED * dt * VERTICAL_SPEED_MULT
                    new_x = g.x + g.dx * speed_x
                    new_y = g.y + g.dy * speed_y
                    new_x, new_y = wrap_xy(new_x, new_y, W, H)
                    if not is_wall(LEVEL, int(new_x), int(new_y), W, H):
                        g.x, g.y = new_x, new_y
                    else:
                        g.dx = g.dy = 0  # Stop if hit wall


        
        # Update frightened timers after collision detection
        for g in ghosts:
            g.frightened = max(0.0, g.frightened - dt)

        if not running:
            break

        if not pellets and not powers:
            msg = "YOU WIN!"
            running = False

        # Render
        stdscr.erase()

        # Title/HUD row (above the map if room)
        try:
            stdscr.addstr(0, 0, f"Level: {title}  (q quits)  Power:{pac.power:4.1f}  Lives:{max(0,pac.lives)}")
        except curses.error:
            pass

        # Maze & pickups
        for y, row in enumerate(LEVEL):
            for x, ch in enumerate(row):
                if ch in WALL:
                    try: stdscr.addstr(y+1, x, ch, MAZE_COLOR)
                    except curses.error: pass
                else:
                    if (x, y) in pellets:
                        try: stdscr.addstr(y+1, x, ".", MAZE_COLOR)
                        except curses.error: pass
                    elif (x, y) in powers:
                        try: stdscr.addstr(y+1, x, "o", MAZE_COLOR)
                        except curses.error: pass
                    else:
                        try: stdscr.addstr(y+1, x, " ")
                        except curses.error: pass

        # Ghosts
        for g in ghosts:
            if g.frightened > 0:
                # Blink red/blue when frightened time < 2 seconds
                if g.frightened < 2.0 and int(g.frightened * 8) % 2:
                    col = GHOST_COLOR  # Red blink
                else:
                    col = FRIGHT_COL   # Blue
            else:
                col = GHOST_COLOR
            try: stdscr.addstr(int(g.y)+1, int(g.x), "M", col)
            except curses.error: pass

        # cman
        pc = PAC_CHARS.get((pac.dx, pac.dy), PAC_CHAR_IDLE)
        try: stdscr.addstr(int(pac.y)+1, int(pac.x), pc, PAC_COLOR)
        except curses.error: pass

        stdscr.refresh()

    # Game over screen
    stdscr.nodelay(False); stdscr.timeout(-1)
    if msg:
        final_msg = msg
        msg_y = H + 2
        msg_x = max(0, (W - len(final_msg)) // 2)
        try:
            stdscr.addstr(msg_y, msg_x, final_msg)
        except curses.error:
            pass
        try:
            stdscr.addstr(msg_y + 2, 0, "q to quit, ENTER for next level")
        except curses.error:
            pass
        stdscr.refresh()
        
        while True:
            ch = stdscr.getch()
            if ch in (ord('q'), ord('Q')):
                return None  # Quit
            elif ch in (10, 13):  # Enter key
                return "NEXT"  # Continue to next level
    else:
        try:
            stdscr.addstr(H + 2, 0, "Bye! Press any key…")
        except curses.error:
            pass
        stdscr.refresh(); stdscr.getch()
        return None

# ---------------- Main ----------------
def main():
    files = list_level_files()
    
    # Check for LEVEL environment variable
    initial_level = get_initial_level()
    if initial_level:
        # Find the index of the specified level
        target_file = initial_level + ".txt"
        try:
            current_level = files.index(target_file)
        except ValueError:
            current_level = 0  # Fallback to first level
    else:
        current_level = 0
    
    while True:
        if current_level >= len(files):
            print("All levels completed!")
            break
            
        filename = files[current_level]
        title = os.path.splitext(filename)[0]
        print(f"Loading: {filename}")
        LEVEL = load_level_file(filename)
        
        result = curses.wrapper(simulate, LEVEL, title)
        
        if result == "NEXT":
            current_level += 1
        else:
            break  # Quit

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
