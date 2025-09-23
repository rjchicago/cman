import type { Dir } from './types';

export class Input {
  current: Dir = 'none';
  next: Dir = 'none';

  constructor() {
    window.addEventListener('keydown', (e) => {
      const d = this.mapKey(e.key);
      if (d) this.next = d;
      if (e.key.toLowerCase() === 'p') this.togglePause?.();
      if (e.key === 'Enter') this.handleEnter?.();
    });
  }
  togglePause?: () => void;
  handleEnter?: () => void;
  
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
