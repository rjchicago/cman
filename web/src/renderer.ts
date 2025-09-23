import type { Grid } from './types';

export class Renderer {
  ctx: CanvasRenderingContext2D;
  tile = 24;
  constructor(private canvas: HTMLCanvasElement) {
    const ctx = canvas.getContext('2d');
    if(!ctx) throw new Error('no 2D context');
    this.ctx = ctx;
  }
  resizeToGrid(grid:Grid){
    this.canvas.width  = grid[0].length * this.tile;
    this.canvas.height = grid.length    * this.tile + 30; // extra space for text
  }
  drawGrid(grid:Grid){
    const {ctx,tile} = this;
    ctx.fillStyle = '#000'; ctx.fillRect(0,0,ctx.canvas.width,ctx.canvas.height);
    for(let y=0;y<grid.length;y++){
      for(let x=0;x<grid[0].length;x++){
        const c = grid[y][x];
        if(c==='wall'){ ctx.fillStyle = '#243'; ctx.fillRect(x*tile, y*tile, tile, tile); }
        if(c==='ghost_exit'){ 
          ctx.fillStyle = '#666'; ctx.fillRect(x*tile, y*tile, tile, tile);
          ctx.fillStyle = '#fff'; ctx.font = `${tile-4}px monospace`; ctx.textAlign = 'center';
          ctx.fillText('=', x*tile + tile/2, y*tile + tile*0.75);
        }
        if(c==='pellet'){ this.disk(x,y,3,'#eee'); }
        if(c==='power'){ this.disk(x,y,6,'#f5d'); }
      }
    }
  }
  drawActor(px:number,py:number,color:string){
    this.disk(px,py,8,color);
  }
  disk(x:number,y:number,r:number,color:string){
    const {ctx,tile} = this;
    const cx = x*tile + tile/2, cy = y*tile + tile/2;
    ctx.beginPath(); ctx.arc(cx,cy,r,0,Math.PI*2); ctx.fillStyle = color; ctx.fill();
  }
  text(msg:string){
    const {ctx} = this;
    const gridHeight = this.canvas.height - 30;
    ctx.fillStyle='#ddd'; ctx.font='14px system-ui'; ctx.textAlign = 'left';
    ctx.fillText(msg, 8, gridHeight + 16);
  }
}
