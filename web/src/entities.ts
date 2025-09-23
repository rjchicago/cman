import type { Dir, Grid } from './types';
import { config } from './config';

export class Actor {
  x: number; y: number; px=0; py=0; speed=config.playerSpeed; dir: Dir='none';
  constructor(x:number,y:number){ this.x=x; this.y=y; this.px=x; this.py=y; }
  setDir(d:Dir){ this.dir=d; }
}

export class Ghost extends Actor {
  homeTimer = config.homeTimeStart; // initial home time
  frightened = 0.0; // frightened timer
  spawnX: number; spawnY: number; // original spawn position
  hasExited = false; // flag to track if ghost has fully exited home
  exiting = false; // flag to track if ghost is currently crossing exit
  
  constructor(x:number,y:number){ 
    super(x,y); 
    this.speed = config.ghostSpeed;
    this.spawnX = x;
    this.spawnY = y;
  }
  
  reset(captureReset = false) {
    this.x = this.spawnX;
    this.y = this.spawnY;
    this.px = this.spawnX;
    this.py = this.spawnY;
    this.homeTimer = captureReset ? config.homeTimeCapture : config.homeTimeStart;
    this.frightened = 0.0;
    this.dir = 'none';
    this.hasExited = false;
    this.exiting = false;
  }
}

export function canMove(grid:Grid, x:number, y:number, isGhost = false, fromX?: number, fromY?: number, hasExited = false) {
  // Allow horizontal warping - if x is out of bounds, check if it's a valid warp
  if (x < 0 || x >= (grid[0]?.length || 0)) {
    return y >= 0 && y < grid.length; // can warp if y is valid
  }
  
  const cell = grid[y]?.[x];
  if (!cell || cell === 'wall') return false;
  if (cell === 'ghost_exit') {
    return isGhost && !hasExited; // only non-exited ghosts can use exits
  }
  if (cell === 'ghost') {
    return isGhost && !hasExited; // only non-exited ghosts can enter spawn areas
  }
  return true;
}

export function stepToward(a:Actor, grid:Grid, desired:Dir, dt:number) {
  const isGhost = a instanceof Ghost;
  const hasExited = isGhost ? (a as Ghost).hasExited : false;
  // Commit pending turn if possible at cell center
  const atCellCenter = Math.abs(a.px - a.x) < 0.001 && Math.abs(a.py - a.y) < 0.001;
  if (atCellCenter && desired!=='none') {
    const [nx, ny] = neighbor(a.x,a.y,desired);
    if (canMove(grid,nx,ny,isGhost,a.x,a.y,hasExited)) a.dir = desired;
  }
  // Move along current dir
  if (a.dir!=='none') {
    const [nx, ny] = neighbor(a.x,a.y,a.dir);
    if (atCellCenter && !canMove(grid,nx,ny,isGhost,a.x,a.y,hasExited)) { a.dir='none'; return; }
    const baseSpeed = a.speed * dt;
    const vx = baseSpeed;
    const vy = baseSpeed * config.verticalSpeedMult;
    if (a.dir==='left')  a.px = Math.max(a.x - 1, a.px - vx);
    if (a.dir==='right') a.px = Math.min(a.x + 1, a.px + vx);
    if (a.dir==='up')    a.py = Math.max(a.y - 1, a.py - vy);
    if (a.dir==='down')  a.py = Math.min(a.y + 1, a.py + vy);
    // Snap if reached target
    if (Math.abs(a.px - a.x) >= 1 || Math.abs(a.py - a.y) >= 1) {
      a.x = Math.round(a.px);
      a.y = Math.round(a.py);
      a.px = a.x; a.py = a.y;
      
      // Handle horizontal warping
      const gridWidth = grid[0]?.length || 0;
      if (a.x < 0) {
        a.x = a.px = gridWidth - 1;
      } else if (a.x >= gridWidth) {
        a.x = a.px = 0;
      }
    }
  }
}

function neighbor(x:number,y:number,dir:Dir):[number,number]{
  if (dir==='left') return [x-1,y];
  if (dir==='right') return [x+1,y];
  if (dir==='up') return [x,y-1];
  if (dir==='down') return [x,y+1];
  return [x,y];
}
