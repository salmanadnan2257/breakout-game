# Breakout Game

A classic Breakout clone built with Python's `turtle` module: a paddle,
a bouncing ball, a wall of blocks colored by row, a lives system, a start
and end screen, an increasing difficulty ramp, and a persistent high score.

## Why it exists

A game-loop exercise: object motion, collision detection against multiple
kinds of surfaces (walls, paddle, blocks), a small state machine for
start/playing/game-over/win, and score state that survives between runs,
all without a game engine, just `turtle` and a manual `while True` loop.

## Features

- Paddle moves left/right with the arrow keys and is clamped to stay on
  screen.
- Ball bounces off all four walls and the paddle, and reverses direction
  when it hits a block.
- A wall of blocks is generated procedurally: random widths, packed row by
  row until there's no more vertical room. Each row gets its own color
  from a fixed palette, so the wall reads as bands of color instead of a
  random speckle.
- Breaking a block flashes it white for a few frames and fires a small
  outward burst of particle turtles at the block's position before both
  disappear, instead of the block just vanishing instantly.
- Three lives. Missing the ball costs a life and resets the ball to the
  center of the board with a new direction (current difficulty is kept);
  the game only ends once all lives are gone.
- The ball speeds up slightly every 4 paddle returns, capped at a maximum
  speed, so later rallies are faster than the opening ones.
- A start screen ("Press SPACE to start") gates the game until the player
  is ready, and a game-over or you-win screen shows the final score with
  a "Press R to restart" prompt that rebuilds the block wall, resets the
  ball and lives, and returns to the start screen.
- Score increases per block destroyed; the high score persists across runs
  in `highestScore.txt`, read on startup and saved whenever a game ends
  (game over or win).

## Architecture

Five small files, one responsibility each:

- `main.py`: builds the `Screen`, wires the other objects together, runs a
  small state machine (`start` -> `playing` -> `game_over`/`won`), and
  drives the main loop (`wn.update()` each frame; physics and collision
  checks only run while `playing`). Binds `space` to start and `r` to
  restart, and owns the start/game-over/win message turtle.
- `paddle.py`: `Paddle(Turtle)`, its position, key bindings, and wall
  clamping.
- `ball.py`: `Ball(Turtle)`, its velocity (`dx`, `dy`), movement, all its
  collision checks (wall, paddle, game-over condition), the difficulty
  ramp (`speed_up()`, triggered from paddle collisions), and the two reset
  paths: `reset_after_miss()` (keep difficulty, re-center after a life is
  lost) and `full_reset()` (used on a full restart).
- `blocks.py`: `Block`, which generates and lays out the entire wall of
  blocks, assigns each row a color from a fixed palette, checks
  ball-to-block collisions by distance, and drives the block-break visual
  feedback (`spawn_burst()`, `update_effects()`) plus a full `reset()` for
  restarting.
- `scoreboard.py`: `Scoreboard(Turtle)`, which renders score/lives text,
  tracks lives (`lose_life()`), and reads/writes `highestScore.txt` for
  persistence (`save_high_score()`, `new_round()`).

Splitting it this way keeps each collision rule readable on its own (ball
vs. wall is a different shape of problem than ball vs. paddle or ball vs.
block) instead of one file with every `if` statement tangled together.

## Setup

Stdlib only: `turtle` (built on `tkinter`) and `time`. No third-party
packages, no environment variables, no `.env` file. On Debian/Ubuntu, if
`import tkinter` fails, install the system package with
`sudo apt-get install python3-tk`.

```bash
cd breakout-game
python3 main.py
```

## Usage

Press `SPACE` at the start screen to begin. Arrow keys (Left/Right) move
the paddle; the ball launches automatically and bounces around. Every
block it hits flashes, bursts into a few particles, and adds to the
score. Missing the ball costs one of 3 lives and re-centers the ball; the
ball also speeds up slightly every 4 successful paddle returns. Losing the
last life shows "GAME OVER" with the final score, and clearing every
block shows "YOU WIN!" instead. Either end screen accepts `R` to restart:
the block wall regenerates, the ball and lives reset, and the start
screen reappears. The high score is saved to `highestScore.txt` whenever
a game ends.

Verified by running the module set through a headless-safe frame loop
(same imports, same per-frame collision calls as `main.py`, capped at 200
iterations instead of looping forever, working on private copies of the
modules so the real `highestScore.txt` isn't touched) rather than the
full interactive game, since `main.py` itself never returns until the
window is closed. The test forces specific conditions instead of relying
on chance within 200 frames: it drives the ball onto the paddle 10 times
to trigger the difficulty ramp, then forces a miss to trigger a life
loss, then exercises the restart path. Output:

```
blocks created: 52
frames run: 200
lives remaining: 2
paddle hits recorded: 10
ball speed: initial=(1.05, 1.05) final=(-1.2247, -1.2247)
life loss observed: True
difficulty increase observed: True
restart flow ok: lives=3, score=0, blocks rebuilt=46, ball speed reset=(1.05, 1.05)
SMOKE TEST OK - ran 200 frames without exception, observed life loss, difficulty increase, and a working restart
```

## Challenges

- **Block layout without an engine.** `blocks.py` has to pack rows of
  randomly-sized blocks left to right and wrap to the next row when a block
  would run past the left edge, then stop entirely when it runs out of
  vertical space. `place_block()` does this by tracking the previous
  block's position and width and computing whether the next one fits; when
  it doesn't, `can_make_more` is set to `False` and the loop in
  `make_all_blocks()` stops and hides the block that didn't fit.
- **Ball vs. block collision without hitboxes.** Turtle doesn't give you
  rectangle collision out of the box, so `check_collision_ball()` uses
  `block.distance(ball) < 35`, a fixed radius check. It's an approximation
  (a wide block and a narrow block are treated as the same size for
  collision purposes), but it's cheap and visually good enough at this
  block size.
- **Ball vs. paddle collision is direction-sensitive.** The check in
  `check_collision_paddle()` only fires when the ball is below y = -240 and
  within the paddle's x-range, otherwise the ball would bounce off the
  paddle's own vertical space even when approaching from above or the
  side.
- **Double collision checks per frame.** `main.py` calls
  `block.check_collision_ball()` twice in the same loop iteration (once
  before moving the ball, once after). This looks like it was done to catch
  a fast-moving ball that would otherwise tunnel past a block between
  checks; it works, but it means the collision logic runs twice as often
  as it needs to for most frames.
- **Score persistence across runs.** `scoreboard.py` reads
  `highestScore.txt` at import time and wraps the read in `try/except` for
  both a missing file and a non-numeric contents, so a first run or a
  corrupted file doesn't crash the game, it just starts the high score at
  0.
- **A TikZ node name collided with a built-in key while building the
  explainer PDFs.** The main-loop diagram in `docs/explainers/deep-dive.pdf`
  originally named its flowchart node style `step`, which silently collides
  with TikZ's own `/tikz/step` key (used for grid spacing); `pdflatex` failed
  with a wall of `pgfkeys Error: The key '/tikz/step' requires a value`
  errors instead of drawing the diagram. Renaming the style to `flowstep`
  fixed it, a reminder that TikZ's style namespace overlaps with its option
  namespace, so short, generic style names aren't actually safe to reuse.

## What I learned

- `turtle`'s `Screen.tracer(0)` plus a manual `wn.update()` per loop
  iteration is what turns turtle from "draws immediately and slowly" into
  something closer to a real frame-based game loop; without it the ball
  would flicker and lag badly.
- Distance-based collision (`turtle.distance()`) is a reasonable substitute
  for real hitbox math when every colliding object is roughly circular or
  small relative to the play field, but it stops being accurate the moment
  object sizes vary a lot, which is visible in how the block collision
  radius is a single constant regardless of block width.
- Reading persisted state (the high score file) at class-definition time
  in `scoreboard.py`, rather than inside `__init__` or a loader function,
  works here because the module is only imported once, but it is a design
  choice that would not survive being imported twice or tested in
  isolation.

## What I'd do differently

- Move the high-score file read out of module level and into an explicit
  `load_high_score()` function; as written, importing `scoreboard.py`
  has a side effect (reading, and potentially writing, a file), which
  makes it harder to test or reuse.
- Replace the fixed-radius distance check in `blocks.py` with an actual
  bounding-box collision test, since block widths vary from 3 to 5 units
  but the collision radius is constant at 35, so wider blocks are
  slightly harder to hit at their edges than the constant assumes.
- Drop the duplicate `block.check_collision_ball()` call in `main.py`'s
  loop, or replace both calls with a single collision check that also
  accounts for the ball's speed, since calling the same check twice per
  frame is a workaround, not a fix, for potential tunneling.
- No automated tests. For a 279-line turtle game that's proportionate, but
  the pure-logic pieces (block placement math, collision distance
  thresholds) could be unit tested without needing a display at all.
