# Cman Level Creator

## Creating Levels

Create `.txt` files in the `levels/` directory. Level files must be rectangular (all rows same width).

### Characters

- `C` - Cman spawn point (required, only one)
- `M` - Ghost spawn points (optional, multiple allowed)
- `.` - Pellets (dots to collect)
- `o` - Power pellets (makes ghosts vulnerable)
- `─│┌┐└┘├┤┬┴┼` - Walls (Unicode box drawing)
- ` ` - Empty space (walkable)

### Design Notes

- Ghost spawn areas should have openings for ghosts to exit

### Warping

- Horizontal warping supported - gaps in left/right walls allow wrapping
- Vertical warping not supported

### Example

``` txt
┌───────────┐
│. . . . . o│
│.┌───┐.┌─┐.│
│.└───┘.└─┘.│
│. . . . . .│
└─┐.┌─ ─┐.┌─┘
  │.│M M│.│  
┌─┘.└───┘.└─┐
│. . .C. . .│
│.┌───┐.┌─┐.│
│.└───┘.└─┘.│
│o . . . . .│
└───────────┘
```

### Controls

- Arrow keys or WASD - Move
- P - Pause
- Q - Quit

### Running

#### Docker

``` bash
docker run --rm -it rjchicago/cman
```

#### Local
- `python3 cman.py` - Interactive level selection
- `LEVEL=003 python3 cman.py` - Load specific level

#### Docker Compose
- `docker compose build` - Build with Docker
- `docker compose run --rm --it cman` - Run interactively
- `docker compose run --rm --it -e LEVEL=003 cman` - Load specific level

#### Alias
Create a shell alias for easier usage:
```bash
cman () {
	docker run --rm -it -e LEVEL="$LEVEL" rjchicago/cman "$@"
}
```

```bash
# Usage
cman

# Load a specific level
LEVEL=003 cman
```
