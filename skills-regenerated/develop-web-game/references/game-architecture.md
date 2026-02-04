# Game Architecture Patterns

Canvas-based web game architecture patterns for the develop-web-game skill.

## Canvas Setup

Use a single `<canvas>` element centered in the viewport. Draw all backgrounds on the canvas context, not via CSS:

```html
<canvas id="game" width="800" height="600"></canvas>
<style>
  body { margin: 0; display: flex; justify-content: center; align-items: center; min-height: 100vh; background: #111; }
  #game { display: block; }
</style>
```

Resize handling: listen for `resize` events and scale the canvas while maintaining aspect ratio.

## render_game_to_text Implementation

Expose `window.render_game_to_text` returning concise JSON with the current game state. Include enough information to play the game without visuals:

```js
function renderGameToText() {
  return JSON.stringify({
    mode: state.mode,                // "menu" | "playing" | "paused" | "gameover"
    player: {
      x: Math.round(state.player.x),
      y: Math.round(state.player.y),
      vx: Math.round(state.player.vx * 10) / 10,
      vy: Math.round(state.player.vy * 10) / 10,
      hp: state.player.hp
    },
    entities: state.entities.map(e => ({
      type: e.type,                  // "enemy" | "projectile" | "pickup"
      x: Math.round(e.x),
      y: Math.round(e.y),
      hp: e.hp
    })),
    score: state.score,
    level: state.level,
    coordSystem: "origin top-left, +x right, +y down"
  });
}
window.render_game_to_text = renderGameToText;
```

Guidelines for the payload:
- Bias toward current, visible entities over full history
- Include coordinate system note (origin and axis directions)
- Encode player position, velocity, active obstacles/enemies, collectibles, timers/cooldowns, score, and mode flags
- Round floating-point values to reduce noise
- Keep payload under ~2 KB for readability

## advanceTime Hook

Provide deterministic time stepping so the Playwright client can advance frames without wall-clock dependency:

```js
window.advanceTime = (ms) => {
  const steps = Math.max(1, Math.round(ms / (1000 / 60)));
  for (let i = 0; i < steps; i++) {
    update(1 / 60);  // fixed-step game update
  }
  render();           // render after all steps
};
```

The game loop should detect when `advanceTime` is available and defer to it during automated testing. During normal play, use `requestAnimationFrame` as usual.

## Fullscreen Toggle

Use a single key (prefer `f`) to toggle fullscreen. Allow `Esc` to exit. When fullscreen toggles, resize the canvas and recalculate input coordinate mapping:

```js
document.addEventListener("keydown", (e) => {
  if (e.key === "f") {
    if (!document.fullscreenElement) {
      canvas.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
  }
});
canvas.addEventListener("fullscreenchange", () => {
  canvas.width = document.fullscreenElement ? window.innerWidth : 800;
  canvas.height = document.fullscreenElement ? window.innerHeight : 600;
});
```

## Game Loop Pattern

A minimal game loop with fixed time step and `advanceTime` support:

```js
let lastTime = 0;
function gameLoop(timestamp) {
  const dt = Math.min((timestamp - lastTime) / 1000, 1 / 30);
  lastTime = timestamp;
  update(dt);
  render();
  requestAnimationFrame(gameLoop);
}
requestAnimationFrame(gameLoop);
```

The `update(dt)` function handles physics, collisions, and state transitions. The `render()` function draws the current state to the canvas. Keep them separate so `advanceTime` can call `update` without redundant renders.
