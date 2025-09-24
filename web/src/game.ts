import type { Grid, Dir } from './types';
import { Renderer } from './renderer';
import { Actor, Ghost, stepToward, canMove } from './entities';
import { config } from './config';

export class Game {
  grid: Grid; player: Actor; ghosts: Ghost[] = [];
  pellets = 0; powers = 0; paused=false; over=false; won=false; statusEl: HTMLElement; inputDir: Dir='none';
  r: Renderer; last = 0; gameStarted = false;
  targetFPS = config.targetFPS; frameInterval = 1000 / config.targetFPS;
  score = 0; lives = config.livesStart; playerPower = 0.0; shield = 0.0;
  currentLevel = '000'; waitingForNext = false;
  playerSpawn: {x: number, y: number};
  clearInput?: () => void;
  input?: any;

  constructor(grid:Grid, spawn:{x:number,y:number}, ghosts:{x:number,y:number}[], canvas:HTMLCanvasElement, statusEl:HTMLElement, level = '000'){
    this.grid = grid; this.player = new Actor(spawn.x, spawn.y);
    this.playerSpawn = {x: spawn.x, y: spawn.y};
    this.ghosts = ghosts.map(g => new Ghost(g.x,g.y));
    this.statusEl = statusEl;
    this.r = new Renderer(canvas);
    this.r.resizeToGrid(grid);
    this.currentLevel = level;
    // count pellets and powers
    for (const row of grid) {
      for (const c of row) {
        if (c==='pellet') this.pellets++;
        if (c==='power') this.powers++;
      }
    }
  }

  setDesiredDirection(d:Dir){ 
    if (this.waitingForNext) return; // ignore movement when waiting for next level
    this.inputDir = d; 
  }
  togglePause(){ 
    if (this.waitingForNext) return; // don't allow pause when waiting for next level
    this.paused = !this.paused;
    this.input?.updatePauseButton(this.paused, this.waitingForNext);
  }
  
  handleEnter() {
    if (this.waitingForNext) {
      this.loadNextLevel();
    }
  }
  
  async loadNextLevel() {
    const currentNum = parseInt(this.currentLevel);
    const nextLevel = String(currentNum + 1).padStart(3, '0');
    
    try {
      const response = await fetch(`/levels/${nextLevel}.txt`);
      if (response.ok) {
        const text = await response.text();
        const { parseAsciiLevel } = await import('./level');
        const { grid, player, ghosts } = parseAsciiLevel(text);
        
        // Reset game state for new level
        this.grid = grid;
        this.player = new Actor(player.x, player.y);
        this.player.dir = 'none';
        this.playerSpawn = {x: player.x, y: player.y};
        this.ghosts = ghosts.map(g => new Ghost(g.x, g.y));
        this.currentLevel = nextLevel;
        this.won = false;
        this.waitingForNext = false;
        this.gameStarted = false;
        this.inputDir = 'none';
        this.clearInput?.(); // clear input system
        this.r.resizeToGrid(grid);
        this.input?.updatePauseButton(this.paused, this.waitingForNext);
        
        // Count pellets and powers
        this.pellets = 0; this.powers = 0;
        for (const row of grid) {
          for (const c of row) {
            if (c==='pellet') this.pellets++;
            if (c==='power') this.powers++;
          }
        }
        
        console.log(`Loaded level ${nextLevel}`);
      } else {
        // No more levels, show completion message
        this.statusEl.textContent = 'All levels complete! Congratulations!';
      }
    } catch (e) {
      console.error('Failed to load next level:', e);
      this.statusEl.textContent = 'All levels complete! Congratulations!';
    }
  }

  update(dt:number){
    if (this.paused || this.over || this.won) return;

    // Update timers
    this.shield = Math.max(0, this.shield - dt);
    this.playerPower = Math.max(0, this.playerPower - dt);

    // Only move player if game has started
    if (this.gameStarted) {
      stepToward(this.player, this.grid, this.inputDir, dt);
    }
    
    // Start game when player first moves (only if not paused/waiting)
    if (!this.gameStarted && this.inputDir !== 'none' && !this.paused && !this.over && !this.won) {
      this.gameStarted = true;
      // Set shorter timer for game start
      for (const g of this.ghosts) {
        if (g.homeTimer > 0) {
          g.homeTimer = config.homeTimeStart;
        }
      }
    }

    // Move ghosts after game started
    if (this.gameStarted) {
      for (const g of this.ghosts) {
        // Update ghost timers only when game is active
        g.homeTimer = Math.max(0, g.homeTimer - dt);
        g.frightened = Math.max(0, g.frightened - dt);
        
        // Skip movement if in home
        if (g.homeTimer > 0) {
          console.log(`Ghost at (${g.x},${g.y}) waiting in home: ${g.homeTimer.toFixed(1)}s`);
          continue;
        }
        
        const currentCell = this.grid[g.y]?.[g.x];
        
        // Track exiting state
        if (!g.exiting && currentCell === 'ghost_exit') {
          g.exiting = true;
        }
        
        // Set hasExited only when ghost fully enters a playable area after exiting
        if (g.exiting && !g.hasExited && (currentCell === 'empty' || currentCell === 'pellet' || currentCell === 'power' || currentCell === 'spawn')) {
          g.hasExited = true;
          g.exiting = false;
          console.log(`Ghost at (${g.x},${g.y}) fully exited home, now on '${currentCell}'`);
        }
        
        let d: Dir = 'none';
        if (g.frightened > 0) {
          // Flee from player when frightened
          const validDirs: Dir[] = [];
          for (const dir of ['up', 'down', 'left', 'right'] as Dir[]) {
            const [nx, ny] = this.getNeighbor(g.x, g.y, dir);
            if (canMove(this.grid, nx, ny, true, g.x, g.y, g.hasExited)) {
              validDirs.push(dir);
            }
          }
          
          if (validDirs.length > 0) {
            const dx = this.player.x - g.x, dy = this.player.y - g.y;
            const distance = Math.abs(dx) + Math.abs(dy);
            const awayDir = Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? 'left' : 'right') : (dy > 0 ? 'up' : 'down');
            
            // Fear decreases with distance - close = 90% flee, far = 30% flee
            const fearLevel = Math.max(0.3, 0.9 - (distance * 0.05));
            
            if (validDirs.includes(awayDir) && Math.random() < fearLevel) {
              d = awayDir;
            } else {
              d = validDirs[Math.floor(Math.random() * validDirs.length)];
            }
          }
        } else if (g.exiting) {
          // Keep current direction while exiting
          d = g.dir;
          console.log(`Ghost at (${g.x},${g.y}) exiting, maintaining direction: ${d}`);
        } else if (!g.hasExited) {
          // Find exit when still in home area
          console.log(`Ghost at (${g.x},${g.y}) hasExited=false, cell='${currentCell}', finding exit`);
          d = this.findGhostExit(g.x, g.y);
          console.log(`Ghost exit direction: ${d}`);
        } else {
          // Chase player when fully exited
          console.log(`Ghost at (${g.x},${g.y}) hasExited=true, chasing player`);
          
          // Get all valid directions
          const validDirs: Dir[] = [];
          for (const dir of ['up', 'down', 'left', 'right'] as Dir[]) {
            const [nx, ny] = this.getNeighbor(g.x, g.y, dir);
            if (canMove(this.grid, nx, ny, true, g.x, g.y, g.hasExited)) {
              validDirs.push(dir);
            }
          }
          
          // Check if at intersection (3+ valid directions) or blocked
          const atIntersection = validDirs.length >= 3;
          const canContinue = g.dir !== 'none' && validDirs.includes(g.dir);
          
          if (canContinue && !atIntersection) {
            d = g.dir; // keep going in corridors
          } else {
            // Make decision at intersections or when blocked
            const dx = this.player.x - g.x, dy = this.player.y - g.y;
            const preferred = Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? 'right' : 'left') : (dy > 0 ? 'down' : 'up');
            
            // Prefer chase direction, but add some randomness
            if (validDirs.includes(preferred) && Math.random() < 0.7) {
              d = preferred;
            } else if (validDirs.length > 0) {
              d = validDirs[Math.floor(Math.random() * validDirs.length)];
            }
          }
        }
        
        stepToward(g, this.grid, d, dt);
      }
    }

    // Eat pellets/powers
    const c = this.grid[this.player.y][this.player.x];
    if (c==='pellet'){ 
      this.grid[this.player.y][this.player.x]='empty'; 
      this.pellets--; 
      this.score += config.pelletPoints;
    }
    if (c==='power'){ 
      this.grid[this.player.y][this.player.x]='empty'; 
      this.powers--;
      this.playerPower = config.powerTime;
      for (const g of this.ghosts) g.frightened = config.powerTime;
    }

    // Collisions - use actual positions for better detection
    if (this.shield <= 0) {
      for (const g of this.ghosts) {
        const dx = g.px - this.player.px;
        const dy = g.py - this.player.py;
        const dist = Math.sqrt(dx * dx + dy * dy);
        
        if (dist < config.collisionThreshold) {
          if (g.frightened > 0) {
            // Player eats frightened ghost
            this.score += config.ghostPoints;
            this.shield = 0.5; // brief invincibility after eating ghost
            g.reset(true); // use capture timer
            console.log(`Player ate ghost at (${g.px.toFixed(1)},${g.py.toFixed(1)})`);
          } else {
            // Ghost catches player
            this.lives--;
            console.log(`Ghost caught player! Lives remaining: ${this.lives}`);
            if (this.lives < 0) {
              this.over = true;
            } else {
              // Reset all entities to spawn positions and stop game
              this.player.x = this.player.px = this.playerSpawn.x;
              this.player.y = this.player.py = this.playerSpawn.y;
              this.player.dir = 'none';
              this.inputDir = 'none';
              this.gameStarted = false; // stop game until player moves
              this.shield = 2.0; // longer invincibility after death
              this.clearInput?.(); // clear input system
              
              // Reset all ghosts to spawn positions
              for (const ghost of this.ghosts) {
                ghost.x = ghost.px = ghost.spawnX;
                ghost.y = ghost.py = ghost.spawnY;
                ghost.dir = 'none';
                ghost.homeTimer = config.homeTimeStart; // reset home timer
                ghost.frightened = 0.0;
                ghost.hasExited = false;
                ghost.exiting = false;
              }
            }
          }
        }
      }
    }

    // Win condition
    if (this.pellets === 0 && this.powers === 0 && !this.won) {
      this.score += config.levelBonus;
      this.won = true;
      this.waitingForNext = true;
      this.input?.updatePauseButton(this.paused, this.waitingForNext);
      console.log(`Level ${this.currentLevel} complete!`);
    }
  }

  findGhostExit(x: number, y: number): Dir {
    // First check adjacent cells for direct exit
    const dirs: [Dir, number, number][] = [['up',0,-1],['down',0,1],['left',-1,0],['right',1,0]];
    
    for (const [dir, dx, dy] of dirs) {
      const nx = x + dx, ny = y + dy;
      if (this.grid[ny]?.[nx] === 'ghost_exit') {
        return dir;
      }
    }
    
    // Find all ghost exits in the level
    const exits: {x: number, y: number}[] = [];
    for (let row = 0; row < this.grid.length; row++) {
      for (let col = 0; col < this.grid[row].length; col++) {
        if (this.grid[row][col] === 'ghost_exit') {
          exits.push({x: col, y: row});
        }
      }
    }
    
    // Find closest exit
    let closestExit = exits[0];
    let minDist = Infinity;
    for (const exit of exits) {
      const dist = Math.abs(exit.x - x) + Math.abs(exit.y - y);
      if (dist < minDist) {
        minDist = dist;
        closestExit = exit;
      }
    }
    
    // Move toward closest exit, but check if path is clear
    if (closestExit) {
      const dx = closestExit.x - x;
      const dy = closestExit.y - y;
      
      // Try horizontal movement first if needed
      if (dx !== 0) {
        const horizontalDir = dx > 0 ? 'right' : 'left';
        const [nx, ny] = this.getNeighbor(x, y, horizontalDir);
        if (this.grid[ny]?.[nx] && this.grid[ny][nx] !== 'wall') {
          return horizontalDir;
        }
      }
      
      // Try vertical movement if horizontal blocked or not needed
      if (dy !== 0) {
        const verticalDir = dy > 0 ? 'down' : 'up';
        const [nx, ny] = this.getNeighbor(x, y, verticalDir);
        if (this.grid[ny]?.[nx] && this.grid[ny][nx] !== 'wall') {
          return verticalDir;
        }
      }
    }
    
    return 'up'; // fallback
  }
  
  getNeighbor(x: number, y: number, dir: Dir): [number, number] {
    if (dir === 'left') return [x-1, y];
    if (dir === 'right') return [x+1, y];
    if (dir === 'up') return [x, y-1];
    if (dir === 'down') return [x, y+1];
    return [x, y];
  }



  render(time:number){
    this.r.drawGrid(this.grid);
    this.ghosts.forEach(g => {
      let color = config.ghostColor;
      if (g.frightened > 0) {
        // Check if ghost should blink (warning that frightened mode is ending)
        const shouldBlink = g.frightened <= config.ghostBlinkTime;
        if (shouldBlink) {
          // Blink every 200ms
          const blinkOn = Math.floor(time / 200) % 2 === 0;
          color = blinkOn ? config.frightenedColor : config.ghostColor;
        } else {
          color = config.frightenedColor;
        }
      }
      this.r.drawActor(g.px,g.py,color);
    });
    this.r.drawActor(this.player.px,this.player.py,config.playerColor);
    const txt = this.over ? 'Game Over' : this.won ? 'Level Complete! Press Enter to continue' : this.paused ? 'Paused' : `Score: ${this.score} Lives: ${this.lives} Pellets: ${this.pellets}`;
    this.r.text(txt);
    this.statusEl.textContent = txt;
  }

  frame = (t:number) => {
    const elapsed = t - this.last;
    
    if (elapsed >= this.frameInterval) {
      const dt = Math.min(0.05, elapsed / 1000);
      this.last = t;
      this.update(dt);
      this.render(t);
    }
    
    requestAnimationFrame(this.frame);
  }
}
