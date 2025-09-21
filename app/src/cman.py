#!/usr/bin/env python3
"""Cman game - main entry point."""
import curses
import locale
import os
from level_loader import list_level_files, load_level_file, get_initial_level
from game_engine import simulate

locale.setlocale(locale.LC_ALL, "")

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
    
    game_state = None
    while True:
        if current_level >= len(files):
            print("All levels completed!")
            break
            
        filename = files[current_level]
        title = os.path.splitext(filename)[0]
        print(f"Loading: {filename}")
        LEVEL = load_level_file(filename)
        
        if game_state:
            result = curses.wrapper(simulate, LEVEL, title, game_state[0], game_state[1])
        else:
            result = curses.wrapper(simulate, LEVEL, title)
        
        if isinstance(result, tuple) and result[0] == "NEXT":
            game_state = result[1]  # (score, lives)
            current_level += 1
        elif result == "NEXT":
            current_level += 1
        elif result == "RESTART":
            current_level = 0
            game_state = None
        else:
            break  # Quit

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass