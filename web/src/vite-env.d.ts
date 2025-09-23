/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_TARGET_FPS: string
  readonly VITE_PLAYER_SPEED: string
  readonly VITE_GHOST_SPEED: string
  readonly VITE_POWER_TIME: string
  readonly VITE_HOME_TIME: string
  readonly VITE_LIVES_START: string
  readonly VITE_COLLISION_THRESHOLD: string
  readonly VITE_VERTICAL_SPEED_MULT: string
  readonly VITE_PELLET_POINTS: string
  readonly VITE_GHOST_POINTS: string
  readonly VITE_LEVEL_BONUS: string
  readonly VITE_CANVAS_WIDTH: string
  readonly VITE_CANVAS_HEIGHT: string
  readonly VITE_DEFAULT_LEVEL: string
  readonly VITE_PLAYER_COLOR: string
  readonly VITE_GHOST_COLOR: string
  readonly VITE_FRIGHTENED_COLOR: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}