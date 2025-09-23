// Game configuration with environment variable overrides
export const config = {
  // Game settings
  targetFPS: Number(import.meta.env.VITE_TARGET_FPS) || 30,
  playerSpeed: Number(import.meta.env.VITE_PLAYER_SPEED) || 7,
  ghostSpeed: Number(import.meta.env.VITE_GHOST_SPEED) || 6,
  powerTime: Number(import.meta.env.VITE_POWER_TIME) || 8.0,
  ghostBlinkTime: Number(import.meta.env.VITE_GHOST_BLINK_TIME) || 3.0,
  homeTimeStart: Number(import.meta.env.VITE_HOME_TIME_START) || 0.2,
  homeTimeCapture: Number(import.meta.env.VITE_HOME_TIME_CAPTURE) || 3.0,
  livesStart: Number(import.meta.env.VITE_LIVES_START) || 3,
  collisionThreshold: Number(import.meta.env.VITE_COLLISION_THRESHOLD) || 0.3,
  verticalSpeedMult: Number(import.meta.env.VITE_VERTICAL_SPEED_MULT) || 0.7,
  
  // Scoring
  pelletPoints: Number(import.meta.env.VITE_PELLET_POINTS) || 1,
  ghostPoints: Number(import.meta.env.VITE_GHOST_POINTS) || 10,
  levelBonus: Number(import.meta.env.VITE_LEVEL_BONUS) || 50,
  
  // Display settings
  canvasWidth: Number(import.meta.env.VITE_CANVAS_WIDTH) || 800,
  canvasHeight: Number(import.meta.env.VITE_CANVAS_HEIGHT) || 640,
  
  // Level settings
  defaultLevel: import.meta.env.VITE_DEFAULT_LEVEL || '001',
  
  // Colors
  playerColor: import.meta.env.VITE_PLAYER_COLOR || '#6cf',
  ghostColor: import.meta.env.VITE_GHOST_COLOR || '#f66',
  frightenedColor: import.meta.env.VITE_FRIGHTENED_COLOR || '#00f',
};