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
    game.input = input;
    input.game = game;
    
    // Hide side panel for all users
    const panel = document.querySelector('.panel') as HTMLElement;
    if (panel) {
      panel.style.display = 'none';
    }
    
    // Hide touch controls on desktop
    if (!input.isMobile) {
      const touchControls = document.getElementById('touch-controls');
      if (touchControls) {
        touchControls.style.display = 'none';
      }
    }
    
    // Dynamic canvas scaling
    const scaleCanvas = () => {
      const controlsHeight = input.isMobile ? 140 : 0;
      const availableWidth = window.innerWidth;
      const availableHeight = window.innerHeight - controlsHeight;
      
      // Get actual canvas dimensions
      const canvasWidth = canvas.offsetWidth || canvas.width;
      const canvasHeight = canvas.offsetHeight || canvas.height;
      
      const scaleX = availableWidth / canvasWidth;
      const scaleY = availableHeight / canvasHeight;
      const scale = Math.min(scaleX, scaleY, 1);
      
      canvas.style.transform = `translate(-50%, -50%) scale(${scale})`;
    };
    
    scaleCanvas();
    window.addEventListener('resize', scaleCanvas);
    // propagate “next desired” every frame to allow snappy turns
    const syncDesired = () => { game.setDesiredDirection(input.next); requestAnimationFrame(syncDesired); };
    syncDesired();
    requestAnimationFrame(game.frame);
  } catch (e:any) {
    status.textContent = e.message ?? 'Failed to load';
    console.error(e);
  }
})();
