export type Vec = { x: number; y: number };
export type Cell = 'empty'|'wall'|'pellet'|'power'|'spawn'|'ghost'|'ghost_exit';
export type Grid = Cell[][];
export type Dir = 'up'|'down'|'left'|'right'|'none';
