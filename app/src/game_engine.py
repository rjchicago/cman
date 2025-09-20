"""Main game engine and simulation loop."""
import curses
import time
import random
from config import *
from entities import Cman, Ghost
from game_utils import *

def simulate(stdscr, LEVEL, title):
    H = len(LEVEL)
    W = len(LEVEL[0])

    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(0)

    # Colors
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_YELLOW, -1)  # Cman
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
        pac.power = max(0.0, pac.power - dt)

        # Input handling
        running, paused, game_started = handle_input(stdscr, pac, paused, last, H, W, LEVEL, game_started)
        if not running or paused:
            if paused:
                last = time.perf_counter()  # Reset timer
            continue

        # Move cman
        move_cman(pac, dt, LEVEL, W, H)
        if (pac.dx != 0 or pac.dy != 0) and not game_started:
            game_started = True

        # Eat pellets/powers
        pac_grid = (int(pac.x), int(pac.y))
        if pac_grid in pellets:
            pellets.remove(pac_grid)
        if pac_grid in powers:
            powers.remove(pac_grid)
            pac.power = POWER_TIME
            for g in ghosts: 
                g.frightened = POWER_TIME

        # Collisions
        running, game_started = handle_collisions(pac, ghosts, pac_start, game_started)
        if not running:
            msg = "GAME OVER"
            break

        # Move ghosts
        if game_started:
            move_ghosts(ghosts, pac, LEVEL, W, H, dt, game_started)

        # Update frightened timers
        for g in ghosts:
            g.frightened = max(0.0, g.frightened - dt)

        # Win condition
        if not pellets and not powers:
            msg = "YOU WIN!"
            running = False

        # Render
        render_game(stdscr, LEVEL, pac, ghosts, pellets, powers, title, 
                   PAC_COLOR, GHOST_COLOR, FRIGHT_COL, MAZE_COLOR)

    # Game over screen
    return show_game_over(stdscr, msg, H, W)

def handle_input(stdscr, pac, paused, last, H, W, LEVEL, game_started):
    try:
        ch = stdscr.getch()
    except curses.error:
        ch = -1
    
    if ch in (ord('q'), ord('Q')):
        return False, paused, game_started
    elif ch in (ord('p'), ord('P')):
        msg_text = "PAUSED"
        stdscr.addstr(max(1, H//2), max(0, (W - len(msg_text)) // 2), msg_text)
        stdscr.refresh()
        stdscr.nodelay(False)
        stdscr.getch()
        stdscr.nodelay(True)
        return True, True, game_started

    want = pac.want
    if ch in (curses.KEY_UP, ord('w'), ord('W')):    
        want = (0, -1)
    elif ch in (curses.KEY_DOWN, ord('s'), ord('S')): 
        want = (0, 1)
    elif ch in (curses.KEY_LEFT, ord('a'), ord('A')): 
        want = (-1, 0)
    elif ch in (curses.KEY_RIGHT, ord('d'), ord('D')):
        want = (1, 0)
    
    pac.want = want
    if want != (0, 0):
        nx, ny = wrap_xy(pac.x + want[0], pac.y + want[1], W, H)
        if not is_wall(LEVEL, int(nx), int(ny), W, H):
            pac.dx, pac.dy = want
    
    return True, False, game_started

def move_cman(pac, dt, LEVEL, W, H):
    if pac.dx != 0 or pac.dy != 0:
        speed_x = PAC_SPEED * dt
        speed_y = PAC_SPEED * dt * VERTICAL_SPEED_MULT
        new_x = pac.x + pac.dx * speed_x
        new_y = pac.y + pac.dy * speed_y
        new_x, new_y = wrap_xy(new_x, new_y, W, H)
        if not is_wall(LEVEL, int(new_x), int(new_y), W, H):
            pac.x, pac.y = new_x, new_y

def handle_collisions(pac, ghosts, pac_start, game_started):
    for g in ghosts:
        distance = abs(g.x - pac.x) + abs(g.y - pac.y)
        if distance < COLLISION_THRESHOLD:
            if g.frightened > 0:
                g.reset()  # This sets home_timer = HOME_TIME
            else:
                if pac.shield > 0:
                    continue
                pac.lives -= 1
                if pac.lives < 0:
                    return False, False
                pac.reset(pac_start)
                for gg in ghosts: 
                    gg.reset()
                time.sleep(0.5)
                return True, False  # Reset game state on respawn
    return True, game_started

def move_ghosts(ghosts, pac, LEVEL, W, H, dt, game_started):
    for g in ghosts:
        # Update home timer
        if g.home_timer > 0:
            g.home_timer = max(0.0, g.home_timer - dt)
            continue  # Skip movement while in home
        
        move_ghost_active(g, pac, dt, LEVEL, W, H)

def move_ghost_active(g, pac, dt, LEVEL, W, H):
    at_intersection = abs(g.x - round(g.x)) < 0.1 and abs(g.y - round(g.y)) < 0.1
    
    if at_intersection or (g.dx == 0 and g.dy == 0):
        forbid = (-g.dx, -g.dy) if (g.dx, g.dy) != (0, 0) else None
        
        if g.frightened > 0:
            ddx, ddy = random_dir(LEVEL, (int(g.x), int(g.y)), forbid, W, H)
        else:
            in_home = abs(g.x - W//2) < 3 and abs(g.y - H//2) < 3
            if in_home:
                exit_target = (int(g.x), max(0, H//2 - 4))
                ddx, ddy = astar_dir(LEVEL, (int(g.x), int(g.y)), exit_target, forbid, W, H)
            else:
                target = (int(pac.x), int(pac.y))
                ddx, ddy = astar_dir(LEVEL, (int(g.x), int(g.y)), target, forbid, W, H)
        
        if ddx == 0 and ddy == 0:
            ddx, ddy = random_dir(LEVEL, (int(g.x), int(g.y)), None, W, H)
        g.dx, g.dy = ddx, ddy
    
    if g.dx != 0 or g.dy != 0:
        speed_x = GHOST_SPEED * dt
        speed_y = GHOST_SPEED * dt * VERTICAL_SPEED_MULT
        new_x = g.x + g.dx * speed_x
        new_y = g.y + g.dy * speed_y
        new_x, new_y = wrap_xy(new_x, new_y, W, H)
        if not is_wall(LEVEL, int(new_x), int(new_y), W, H):
            g.x, g.y = new_x, new_y
        else:
            g.dx = g.dy = 0

def render_game(stdscr, LEVEL, pac, ghosts, pellets, powers, title, 
                PAC_COLOR, GHOST_COLOR, FRIGHT_COL, MAZE_COLOR):
    stdscr.erase()

    # Title/HUD
    try:
        stdscr.addstr(0, 0, f"Level: {title}  (q quits)  Power:{pac.power:4.1f}  Lives:{max(0,pac.lives)}")
    except curses.error:
        pass

    # Maze & pickups
    for y, row in enumerate(LEVEL):
        for x, ch in enumerate(row):
            if ch in WALL:
                try: 
                    stdscr.addstr(y+1, x, ch, MAZE_COLOR)
                except curses.error: 
                    pass
            else:
                if (x, y) in pellets:
                    try: 
                        stdscr.addstr(y+1, x, ".", MAZE_COLOR)
                    except curses.error: 
                        pass
                elif (x, y) in powers:
                    try: 
                        stdscr.addstr(y+1, x, "o", MAZE_COLOR)
                    except curses.error: 
                        pass
                else:
                    try: 
                        stdscr.addstr(y+1, x, " ")
                    except curses.error: 
                        pass

    # Ghosts
    for g in ghosts:
        if g.frightened > 0:
            if g.frightened < 2.0 and int(g.frightened * 8) % 2:
                col = GHOST_COLOR
            else:
                col = FRIGHT_COL
        else:
            col = GHOST_COLOR
        try: 
            stdscr.addstr(int(g.y)+1, int(g.x), "M", col)
        except curses.error: 
            pass

    # Cman
    pc = PAC_CHARS.get((pac.dx, pac.dy), PAC_CHAR_IDLE)
    try: 
        stdscr.addstr(int(pac.y)+1, int(pac.x), pc, PAC_COLOR)
    except curses.error: 
        pass

    stdscr.refresh()

def show_game_over(stdscr, msg, H, W):
    stdscr.nodelay(False)
    stdscr.timeout(-1)
    
    if msg:
        msg_y = H + 2
        msg_x = max(0, (W - len(msg)) // 2)
        try:
            stdscr.addstr(msg_y, msg_x, msg)
            stdscr.addstr(msg_y + 2, 0, "q to quit, ENTER for next level")
        except curses.error:
            pass
        stdscr.refresh()
        
        while True:
            ch = stdscr.getch()
            if ch in (ord('q'), ord('Q')):
                return None
            elif ch in (10, 13):
                return "NEXT"
    else:
        try:
            stdscr.addstr(H + 2, 0, "Bye! Press any key…")
        except curses.error:
            pass
        stdscr.refresh()
        stdscr.getch()
        return None