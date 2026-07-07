from turtle import *
import random

BASE_SPEED = 1.05
SPEED_STEP = 1.08
MAX_SPEED = 2.6
HITS_PER_STEP = 4


class Ball(Turtle):
    def __init__(self):
        super().__init__()
        self.shape("circle")
        self.color("white")
        self.penup()
        self.goto(0, 0)
        self.dx = BASE_SPEED
        self.dy = BASE_SPEED
        self.paddle_hits = 0

    def move(self):
        self.goto(self.xcor() + self.dx, self.ycor() + self.dy)

    def bounce_x(self):
        self.dx *= -1

    def bounce_y(self):
        self.dy *= -1

    def reset_x(self, sign):
        if sign == '+':
            self.setx(390)
        else:
            self.setx(-390)

    def reset_y(self, sign):
        if sign == '+':
            self.sety(290)
        else:
            self.sety(-290)

    def check_collision_wall(self):
        # Border Checking
        if self.xcor() > 390:
            self.reset_x(sign='+')
            self.bounce_x()

        if self.xcor() < -390:
            self.reset_x(sign='-')
            self.bounce_x()

        if self.ycor() > 290:
            self.reset_y(sign='+')
            self.bounce_y()

        if self.ycor() < -290:
            self.reset_y(sign='-')
            self.bounce_y()

    def check_collision_paddle(self, paddle):
        if (self.ycor() < -240) and (paddle.xcor() + 80 > self.xcor() > paddle.xcor() - 80):
            self.sety(-240)
            self.dy *= -1
            self.paddle_hits += 1
            if self.paddle_hits % HITS_PER_STEP == 0:
                self.speed_up()

    def speed_up(self):
        """Difficulty ramp: every HITS_PER_STEP paddle returns, nudge the
        ball's speed up (preserving direction), capped at MAX_SPEED so it
        never becomes unplayable."""
        new_dx = self.dx * SPEED_STEP
        new_dy = self.dy * SPEED_STEP
        if abs(new_dx) <= MAX_SPEED:
            self.dx = new_dx
        if abs(new_dy) <= MAX_SPEED:
            self.dy = new_dy

    def check_game_over(self):
        if self.ycor() < -280:
            return True
        else:
            return False

    def reset_after_miss(self):
        """Ball dropped past the paddle but the player still has lives
        left: put it back in the middle of the board and send it off in
        a fresh (randomized) direction, keeping the current speed/difficulty."""
        self.goto(0, 0)
        speed_x = abs(self.dx)
        speed_y = abs(self.dy)
        self.dx = speed_x if random.random() < 0.5 else -speed_x
        self.dy = speed_y

    def full_reset(self):
        """Used when starting a brand new game (after game over/win):
        reset position, speed, and the paddle-hit counter that drives
        the difficulty ramp."""
        self.goto(0, 0)
        self.dx = BASE_SPEED
        self.dy = BASE_SPEED
        self.paddle_hits = 0
