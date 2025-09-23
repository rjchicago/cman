import type { Grid } from './types';
import { config } from './config';

const ENTITY = new Set(['C','M','.','o',' ','=']);

async function getFirstLevel(): Promise<string> {
  // Try common level names in order
  const commonLevels = ['000', '001', '002', '003', '004', '005', '006'];
  
  for (const level of commonLevels) {
    try {
      const response = await fetch(`/levels/${level}.txt`);
      if (response.ok) {
        console.log(`Found first level: ${level}`);
        return level;
      }
    } catch (e) {
      // Continue to next level
    }
  }
  
  console.log(`Using default level: ${config.defaultLevel}`);
  return config.defaultLevel;
}

export async function loadLevelFromParam(): Promise<{grid:Grid, player:{x:number,y:number}, ghosts:{x:number,y:number}[]}> {
  const p = new URLSearchParams(location.search);
  const level = p.get('level') ?? await getFirstLevel();
  const res = await fetch(`/levels/${level}.txt`);
  if (!res.ok) throw new Error(`Failed to load level ${level}`);
  const text = await res.text();
  return parseAsciiLevel(text);
}

export function parseAsciiLevel(text: string) {
  const lines = text.replace(/\r/g,'').split('\n').filter(l => l.length>0);
  const w = Math.max(...lines.map(l => l.length));
  const grid: Grid = [];
  let player = {x:0,y:0};
  const ghosts: {x:number,y:number}[] = [];

  for (let y=0; y<lines.length; y++) {
    const row: any[] = [];
    for (let x=0; x<w; x++) {
      const ch = lines[y][x] ?? ' ';
      if (ch === 'C') { player = {x,y}; row.push('spawn'); }
      else if (ch === 'M') { ghosts.push({x,y}); row.push('ghost'); }
      else if (ch === '.') row.push('pellet');
      else if (ch === 'o') row.push('power');
      else if (ch === '=') row.push('ghost_exit');
      else if (ch === ' ' ) row.push('empty');
      else row.push(ENTITY.has(ch) ? 'empty' : 'wall'); // any other glyph => wall
    }
    grid.push(row);
  }
  return { grid, player, ghosts };
}
