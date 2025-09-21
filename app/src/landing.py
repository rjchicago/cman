"""Landing page with leaderboard."""
import curses
from high_scores import get_top_scores

def show_landing(stdscr):
    """Show landing page with leaderboard."""
    curses.curs_set(0)
    stdscr.nodelay(False)
    
    while True:
        stdscr.erase()
        
        try:
            # Title
            stdscr.addstr(1, 0, " ██████ ███    ███  █████  ███    ██ ")
            stdscr.addstr(2, 0, "██      ████  ████ ██   ██ ████   ██ ")
            stdscr.addstr(3, 0, "██      ██ ████ ██ ███████ ██ ██  ██ ")
            stdscr.addstr(4, 0, "██      ██  ██  ██ ██   ██ ██  ██ ██ ")
            stdscr.addstr(5, 0, " ██████ ██      ██ ██   ██ ██   ████ ")
            stdscr.addstr(7, 0, "HIGH SCORES:")
            
            # Leaderboard
            scores = get_top_scores(10)
            if scores:
                for i, entry in enumerate(scores):
                    initials = entry.get('initials', '???')
                    stdscr.addstr(9 + i, 0, f"{i+1:2}. {initials} {entry['score']:>6} ({entry['date'][:10]})")
            else:
                stdscr.addstr(9, 0, "No high scores yet!")
            
            # Instructions
            stdscr.addstr(21, 0, "Press ENTER to start, Q to quit")
            
        except curses.error:
            pass
        
        stdscr.refresh()
        
        ch = stdscr.getch()
        if ch in (10, 13):  # Enter
            return True
        elif ch in (ord('q'), ord('Q')):
            return False