from turtle import *
from turtle import Terminator
from blocks import Block
from ball import Ball
from paddle import Paddle
from scoreboard import Scoreboard

# Breakout Game

# Screen
wn = Screen()
wn.title("Breakout Game")
wn.bgcolor("black")
wn.setup(width=800, height=600)
wn.tracer(0)

# Blocks
block = Block()
block.make_all_blocks()

# Paddle
paddle = Paddle()

# Ball
ball = Ball()

# Scoreboard
scoreboard = Scoreboard()
scoreboard.update_score()

# Keyboard Binding
paddle.key_bindings(wn)

# Center-screen message turtle: start screen, game over, and win screen
# all reuse this instead of each spawning their own Turtle.
message = Turtle()
message.color("white")
message.penup()
message.hideturtle()

# Simple state machine: "start" -> "playing" -> "game_over" / "won".
# Physics only runs in "playing"; the other states just wait on a key press.
game_state = "start"


def show_start_screen():
    message.clear()
    message.goto(0, 20)
    message.write("BREAKOUT", align="center", font=("Courier", 32, "bold"))
    message.goto(0, -20)
    message.write("Press SPACE to start  -  Arrow keys move the paddle",
                  align="center", font=("Courier", 16, "normal"))


def show_end_screen(won):
    message.clear()
    message.goto(0, 20)
    title = "YOU WIN!" if won else "GAME OVER"
    message.write(title, align="center", font=("Courier", 32, "bold"))
    message.goto(0, -20)
    message.write(f"Final Score: {scoreboard.score}  -  Press R to restart",
                  align="center", font=("Courier", 16, "normal"))


def start_game():
    global game_state
    if game_state == "start":
        message.clear()
        game_state = "playing"


def restart_game():
    global game_state
    if game_state in ("game_over", "won"):
        block.reset()
        ball.full_reset()
        scoreboard.new_round()
        show_start_screen()
        game_state = "start"


wn.onkey(start_game, "space")
wn.onkey(restart_game, "r")
wn.listen()

show_start_screen()

# Main Game Loop. Runs until the player closes the window, at which point
# turtle raises Terminator - caught here so the process exits cleanly
# instead of printing a traceback.
try:
    while True:
        wn.update()

        if game_state == "playing":
            # Check collision with the blocks
            block.check_collision_ball(ball, scoreboard)

            # Move the ball
            ball.move()

            # Check collision with the wall
            ball.check_collision_wall()

            # Paddle and Ball Collisions (also drives the difficulty ramp)
            ball.check_collision_paddle(paddle)

            # Paddle and Wall Collisions
            paddle.check_collision_wall()

            # Check collision with the blocks
            block.check_collision_ball(ball, scoreboard)

            # Advance block-break flash/particle effects by one frame
            block.update_effects()

            if len(block.all_blocks) == 0:
                scoreboard.save_high_score()
                show_end_screen(won=True)
                game_state = "won"
            elif ball.check_game_over():
                is_game_over = scoreboard.lose_life()
                if is_game_over:
                    scoreboard.save_high_score()
                    show_end_screen(won=False)
                    game_state = "game_over"
                else:
                    ball.reset_after_miss()
        else:
            # Let any in-flight particle bursts keep animating even after
            # the round ends, instead of freezing mid-burst.
            block.update_effects()
except Terminator:
    pass
