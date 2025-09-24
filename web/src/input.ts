import type { Dir } from './types';

export class Input {
  current: Dir = 'none';
  next: Dir = 'none';
  isMobile = false;
  pauseBtn?: HTMLElement;
  game?: any;

  constructor() {
    this.isMobile = this.detectMobile();
    
    window.addEventListener('keydown', (e) => {
      const d = this.mapKey(e.key);
      if (d) this.next = d;
      if (e.key.toLowerCase() === 'p') this.togglePause?.();
      if (e.key === 'Enter') this.handleEnter?.();
    });
    
    if (this.isMobile) {
      this.setupTouchControls();
    }
  }
  togglePause?: () => void;
  handleEnter?: () => void;
  
  detectMobile(): boolean {
    const params = new URLSearchParams(location.search);
    if (params.get('mobile') === 'true') return true;
    
    return /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
           ('ontouchstart' in window) ||
           (window.innerWidth <= 768);
  }
  
  setupTouchControls() {
    const controls = document.createElement('div');
    controls.id = 'touch-controls';
    controls.innerHTML = `
      <div id="dpad">
        <div class="dpad-btn" data-dir="up">↑</div>
        <div class="dpad-btn" data-dir="left">←</div>
        <div class="dpad-btn" data-dir="right">→</div>
        <div class="dpad-btn" data-dir="down">↓</div>
      </div>
      <button id="pause-btn">⏸</button>
    `;
    document.body.appendChild(controls);
    
    // Touch and mouse events for directional pad
    controls.querySelectorAll('.dpad-btn').forEach(btn => {
      const dir = btn.getAttribute('data-dir') as Dir;
      
      const start = (e: Event) => {
        e.preventDefault();
        this.next = dir;
        btn.classList.add('active');
      };
      const end = (e: Event) => {
        e.preventDefault();
        btn.classList.remove('active');
      };
      
      btn.addEventListener('touchstart', start);
      btn.addEventListener('touchend', end);
      btn.addEventListener('mousedown', start);
      btn.addEventListener('mouseup', end);
    });
    
    // Pause button
    const pauseBtn = controls.querySelector('#pause-btn') as HTMLElement;
    
    this.pauseBtn = pauseBtn;
    
    const pauseStart = (e: Event) => {
      e.preventDefault();
      pauseBtn.classList.add('active');
    };
    
    const pauseClick = (e: Event) => {
      e.preventDefault();
      if (this.game?.waitingForNext) {
        this.handleEnter?.();
      } else {
        this.togglePause?.();
      }
    };
    const pauseEnd = (e: Event) => {
      e.preventDefault();
      pauseBtn.classList.remove('active');
    };
    
    pauseBtn.addEventListener('touchstart', pauseStart);
    pauseBtn.addEventListener('touchend', (e) => {
      pauseEnd(e);
      pauseClick(e);
    });
    pauseBtn.addEventListener('mousedown', pauseStart);
    pauseBtn.addEventListener('mouseup', (e) => {
      pauseEnd(e);
      pauseClick(e);
    });
  }
  
  updatePauseButton(paused: boolean, waitingForNext: boolean) {
    if (this.pauseBtn) {
      this.pauseBtn.textContent = (paused || waitingForNext) ? '▶' : '⏸';
    }
  }
  
  clearInput() {
    this.next = 'none';
    this.current = 'none';
  }

  mapKey(k: string): Dir | null {
    switch (k) {
      case 'ArrowUp': case 'w': case 'W': return 'up';
      case 'ArrowDown': case 's': case 'S': return 'down';
      case 'ArrowLeft': case 'a': case 'A': return 'left';
      case 'ArrowRight': case 'd': case 'D': return 'right';
      default: return null;
    }
  }
}
