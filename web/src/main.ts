import { Input } from './input';
import { loadLevelFromParam } from './level';
import { Game } from './game';

(async function(){
  const canvas = document.getElementById('game') as HTMLCanvasElement;
  const status = document.getElementById('status')!;
  try {
    const p = new URLSearchParams(location.search);
    const currentLevel = p.get('level') ?? '000';
    const {grid, player, ghosts} = await loadLevelFromParam();
    const game = new Game(grid, player, ghosts, canvas, status, currentLevel);
    const input = new Input();
    input.togglePause = () => game.togglePause();
    input.handleEnter = () => game.handleEnter();
    game.clearInput = () => input.clearInput();
    // propagate “next desired” every frame to allow snappy turns
    const syncDesired = () => { game.setDesiredDirection(input.next); requestAnimationFrame(syncDesired); };
    syncDesired();
    requestAnimationFrame(game.frame);
  } catch (e:any) {
    status.textContent = e.message ?? 'Failed to load';
    console.error(e);
  }
})();
