"""Game utility functions for pathfinding and level operations."""
import random
from heapq import heappush, heappop
from config import WALL

def make_pellet_map(LEVEL):
    pellets, powers = set(), set()
    for y, row in enumerate(LEVEL):
        for x, ch in enumerate(row):
            if ch == '.': 
                pellets.add((x, y))
            elif ch == 'o': 
                powers.add((x, y))
    return pellets, powers

def in_bounds(x, y, W, H): 
    return 0 <= x < W and 0 <= y < H

def is_wall(LEVEL, x, y, W, H):
    if not in_bounds(x, y, W, H): 
        return True
    return LEVEL[y][x] in WALL

def wrap_xy(x, y, W, H):
    # Horizontal wrap: always wrap; to make a tunnel, leave spaces on edges.
    if x < 0: x = W - 1
    if x >= W: x = 0
    # (Keep vertical clamp — classic doesn't wrap vertically)
    return x, y

def neighbors(LEVEL, x, y, W, H):
    for dx, dy in ((1,0), (-1,0), (0,1), (0,-1)):
        nx, ny = wrap_xy(x + dx, y + dy, W, H)
        if not is_wall(LEVEL, nx, ny, W, H):
            yield nx, ny, (dx, dy)

def manhattan(a, b): 
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def astar_dir(LEVEL, src, dst, forbid, W, H):
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

def find_default_spawns(LEVEL):
    """Find spawn points marked with C (cman) and M (ghosts), replace with spaces"""
    H = len(LEVEL)
    W = len(LEVEL[0])
    
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
                    pac = (x, y)
                    break
            if pac: break
        if pac is None: pac = (1, 1)
    
    # Use only the ghosts found (don't force 4)
    ghosts = ghost_candidates
    
    # Use ghost starting positions as scatter targets
    scatters = ghost_candidates
    return pac, ghosts, scatters