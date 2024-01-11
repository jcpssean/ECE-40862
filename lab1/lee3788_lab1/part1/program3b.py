import random

n = random.randint(0, 10)
i = 0
win = 0

while (i<3 and win == 0):
    guess = int(input("Enter your guess: "))
    if guess == n: win = 1
    i += 1
if win: print("You win!")
else: print("You lose!")