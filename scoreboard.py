from turtle import Turtle

try:
    score = int(open('highestScore.txt', 'r').read())
except FileNotFoundError:
    score = open('highestScore.txt', 'w').write(str(0))
except ValueError:
    score = 0
FONT = ("Courier", 20, "normal")
STARTING_LIVES = 3


class Scoreboard(Turtle):
    def __init__(self):
        super().__init__()
        self.color('white')
        self.penup()
        self.hideturtle()
        self.highScore = score
        self.goto(x=-380, y=260)
        self.score = 0
        self.lives = STARTING_LIVES
        self.update_score()

    def update_score(self):
        self.clear()
        self.write(
            f"Score: {self.score} | Lives: {self.lives} | Highest Score: {self.highScore}",
            align='left', font=FONT)

    def increase_score(self):
        self.score += 1
        if self.score > self.highScore:
            self.highScore += 1
        self.update_score()

    def lose_life(self):
        """Decrement lives after a miss. Returns True when that was the
        last life (game over), False if the player can keep going."""
        self.lives -= 1
        self.update_score()
        return self.lives <= 0

    def save_high_score(self):
        """Persist the high score to disk. Called when a game ends
        (game over or win), independent of resetting the on-screen state."""
        open('highestScore.txt', 'w').write(str(self.highScore))

    def new_round(self):
        """Reset score and lives for a fresh game, keeping the persisted
        high score intact."""
        self.score = 0
        self.lives = STARTING_LIVES
        self.update_score()

    def reset(self):
        self.save_high_score()
        self.new_round()
