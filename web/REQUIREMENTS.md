# Cman Web Requirements

Based on the Python implementation, this document defines the requirements for the web version to achieve feature parity.

## Core Game Mechanics

### Player (Cman)
- **Movement**: Arrow keys or WASD
- **Speed**: 7 units/second (configurable via `VITE_PLAYER_SPEED`)
- **Vertical Speed**: 70% of horizontal speed (0.7 multiplier)
- **Lives**: Start with 3 lives
- **Shield**: 1 second invincibility after respawn
- **Power Mode**: 8 seconds after eating power pellet
- **Collision**: Manhattan distance < 0.9 units

### Ghosts
- **Speed**: 6 units/second (configurable via `VITE_GHOST_SPEED`)
- **Vertical Speed**: 70% of horizontal speed (0.7 multiplier)
- **Home Timer**: 2 seconds in home before exiting
- **AI States**:
  - **In Home**: Use A* pathfinding to exit home area
  - **Chase Mode**: Use A* pathfinding to reach player
  - **Frightened Mode**: Random movement for 8 seconds
- **Collision**: Same as player
- **Respawn**: Return to home with 2-second timer when eaten

### Level Elements
- **Pellets (.)**: Worth 1 point each
- **Power Pellets (o)**: Activate power mode, make ghosts frightened
- **Walls**: Unicode box drawing characters `─│┌┐└┘├┤┬┴┼`
- **Spawn Points**: 
  - `C` for Cman (replaced with space)
  - `M` for ghosts (replaced with space)

### Game Flow
- **Start Condition**: Game begins when player first moves
- **Win Condition**: All pellets and power pellets collected
- **Lose Condition**: All lives lost
- **Level Progression**: Automatic advance to next level
- **Scoring**:
  - Pellet: 1 point
  - Ghost (when frightened): 10 points
  - Level completion bonus: 50 points

## Technical Requirements

### Performance
- **Frame Rate**: 30 FPS (configurable via `VITE_TARGET_FPS`)
- **Input Handling**: Non-blocking, responsive controls
- **Collision Detection**: Efficient distance calculations
- **Pathfinding**: A* algorithm for ghost AI

### Display
- **Canvas Size**: 800x640 pixels (configurable)
- **Colors**:
  - Player: `#6cf` (cyan)
  - Ghosts: `#f66` (red)
  - Frightened Ghosts: Flashing between red and cyan
- **Character Display**:
  - Player: Directional arrows `>`, `<`, `^`, `v` or `C` when idle
  - Ghosts: `M`
  - Pellets: `.`
  - Power Pellets: `o`

### Controls
- **Movement**: Arrow keys, WASD
- **Pause**: P key
- **Quit**: Q key

### Level System
- **Format**: Text files with ASCII art
- **Loading**: Support for multiple levels (001.txt, 002.txt, etc.)
- **Default Level**: Configurable via `VITE_DEFAULT_LEVEL`
- **Horizontal Wrapping**: Support tunnel effects at screen edges
- **No Vertical Wrapping**: Maintain classic behavior

## Missing Features (To Implement)

### High Priority
1. **Ghost Home Timer**: 2-second delay before ghosts exit home
2. **A* Pathfinding**: Replace simple chase with proper pathfinding
3. **Frightened State**: Ghosts turn blue and move randomly when player has power
4. **Power Mode Timer**: Visual countdown and ghost state management
5. **Lives System**: Track and display remaining lives
6. **Scoring System**: Implement point system and display
7. **Shield/Invincibility**: Brief protection after respawn
8. **Vertical Speed Reduction**: 70% speed for vertical movement

### Medium Priority
1. **Level Progression**: Automatic advance to next level
2. **Game Over Screen**: Show final score and restart options
3. **Pause Functionality**: Proper pause/resume with visual indicator
4. **High Scores**: Local storage of top scores
5. **Sound Effects**: Basic audio feedback (optional)

### Low Priority
1. **Multiple Ghost Types**: Different AI behaviors per ghost
2. **Scatter Mode**: Ghosts retreat to corners periodically
3. **Bonus Items**: Fruit and other collectibles
4. **Animations**: Smooth sprite animations
5. **Particle Effects**: Visual feedback for eating pellets

## Configuration Variables

All values should be configurable via environment variables:

```bash
# Game mechanics
VITE_TARGET_FPS=30
VITE_PLAYER_SPEED=7
VITE_GHOST_SPEED=6
VITE_POWER_TIME=8.0
VITE_HOME_TIME=2.0
VITE_LIVES_START=3
VITE_COLLISION_THRESHOLD=0.9
VITE_VERTICAL_SPEED_MULT=0.7

# Scoring
VITE_PELLET_POINTS=1
VITE_GHOST_POINTS=10
VITE_LEVEL_BONUS=50

# Display
VITE_CANVAS_WIDTH=800
VITE_CANVAS_HEIGHT=640
VITE_PLAYER_COLOR=#6cf
VITE_GHOST_COLOR=#f66
VITE_FRIGHTENED_COLOR=#00f

# Level
VITE_DEFAULT_LEVEL=001
```

## Testing Checklist

- [ ] Player moves in all directions at correct speed
- [ ] Ghosts exit home after timer expires
- [ ] Ghosts chase player using pathfinding
- [ ] Power pellets make ghosts frightened
- [ ] Collision detection works accurately
- [ ] Lives decrease on ghost collision
- [ ] Score increases for pellets and ghosts
- [ ] Level completes when all pellets eaten
- [ ] Horizontal wrapping works at screen edges
- [ ] Pause/resume functionality
- [ ] All configuration variables work
- [ ] Performance maintains 30 FPS