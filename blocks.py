from turtle import *
import math
import random

UPPER_XCOR = 400
LOWER_XCOR = -400
UPPER_YCOR = 240
LOWER_YCOR = 140

# One color per row, cycled if there are more rows than colors, instead of a
# single flat color or a fully random per-block palette.
ROW_COLORS = [
    'tomato', 'orange', 'gold', 'yellow green',
    'medium sea green', 'steel blue', 'medium purple',
]

BURST_PARTICLES = 5
BURST_LIFETIME = 8
FADE_FRAMES = 3


class Block:
    def __init__(self):
        self.random_ylength = [3, 4, 5]
        self.all_blocks = []
        self.x_y_position = []
        self.random_stretch_len = []
        self.can_make_more = True
        # Blocks that were just hit: briefly flash white before disappearing.
        self.fading = []
        # Small particle bursts spawned on block break.
        self.particles = []

    def make_block(self):
        block = Turtle()
        random_strechlen = random.choice(self.random_ylength)
        self.random_stretch_len.append(random_strechlen)
        block.shapesize(stretch_wid=1, stretch_len=random_strechlen)
        block.shape("square")
        block.penup()
        self.place_block(block)
        # Color is assigned by row (based on final y position) rather than
        # picked independently per block, so each row reads as one band.
        row = int(round((UPPER_YCOR - block.ycor()) / 20))
        row_color = ROW_COLORS[row % len(ROW_COLORS)]
        block.color(row_color)
        block.break_color = row_color
        self.all_blocks.append(block)

    def place_block(self, block):
        if len(self.all_blocks) == 0:
            x = UPPER_XCOR - ((self.random_stretch_len[-1] * 20) // 2)
            y = UPPER_YCOR
            self.x_y_position.append((x, y))
            block.goto(x=x, y=y)
        else:
            x = ((self.x_y_position[-1][0] - ((self.random_stretch_len[-2] * 20) // 2)) - (
                    (self.random_stretch_len[-1] * 20) // 2))
            lim = (UPPER_XCOR - ((self.random_stretch_len[-1] * 20) // 2)) * -1
            if x < lim:
                x = UPPER_XCOR - ((self.random_stretch_len[-1] * 20) // 2)
                y = (self.x_y_position[-1][1] - 20)
                if y > LOWER_YCOR:
                    self.x_y_position.append((x, y))
                    block.goto(x=x, y=y)
                else:
                    self.can_make_more = False
                    return
            else:
                y = self.x_y_position[-1][1]
                self.x_y_position.append((x, y))
                block.goto(x=x, y=y)

    def make_all_blocks(self):
        while self.can_make_more:
            self.make_block()
            if not self.can_make_more:
                self.all_blocks[-1].hideturtle()

    def spawn_burst(self, x, y, color):
        """Cheap "particle" feedback: a few tiny turtles flying outward
        for a handful of frames, then removed. No physics engine, just
        a fixed velocity per particle and a frame countdown."""
        for _ in range(BURST_PARTICLES):
            particle = Turtle()
            particle.penup()
            particle.shape("circle")
            particle.shapesize(0.3)
            particle.color(color)
            particle.goto(x, y)
            angle = random.uniform(0, 360)
            dx = math.cos(math.radians(angle)) * 5
            dy = math.sin(math.radians(angle)) * 5
            self.particles.append([particle, dx, dy, BURST_LIFETIME])

    def update_effects(self):
        """Advance the block-break flash and particle burst by one frame.
        Must be called once per main-loop iteration."""
        for entry in self.fading[:]:
            blk, frames_left = entry
            frames_left -= 1
            if frames_left <= 0:
                blk.hideturtle()
                self.fading.remove(entry)
            else:
                entry[1] = frames_left

        for entry in self.particles[:]:
            particle, dx, dy, frames_left = entry
            particle.goto(particle.xcor() + dx, particle.ycor() + dy)
            frames_left -= 1
            if frames_left <= 0:
                particle.hideturtle()
                self.particles.remove(entry)
            else:
                entry[3] = frames_left

    def check_collision_ball(self, ball, scoreboard):
        for block in self.all_blocks:
            if block.distance(ball) < 35:
                scoreboard.increase_score()
                self.all_blocks.remove(block)
                x, y, color = block.xcor(), block.ycor(), block.break_color
                block.color("white")
                self.fading.append([block, FADE_FRAMES])
                self.spawn_burst(x, y, color)
                ball.dy *= -1
                return True
        return False

    def reset(self):
        """Clear every block and in-flight effect, then rebuild a fresh
        wall. Used when a finished game is restarted."""
        for block in self.all_blocks:
            block.hideturtle()
        for entry in self.fading:
            entry[0].hideturtle()
        for entry in self.particles:
            entry[0].hideturtle()

        self.all_blocks = []
        self.x_y_position = []
        self.random_stretch_len = []
        self.fading = []
        self.particles = []
        self.can_make_more = True
        self.make_all_blocks()
