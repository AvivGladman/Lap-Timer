import pygame
import sys
import time
from gpiozero import Button

# === User Input ===
try:
    remaining_laps = int(input("Enter the number of laps: "))
except ValueError:
    print("Invalid input. Please enter an integer.")
    sys.exit(1)

# === GPIO Setup ===
start_lap_button = Button(2)

# === Pygame Setup ===
pygame.init()
screen = pygame.display.set_mode((600, 300))
pygame.display.set_caption("Lap Timer")
font_large = pygame.font.SysFont(None, 60)
font_small = pygame.font.SysFont(None, 40)
clock = pygame.time.Clock()

# === State ===
started = False
start_time = None
elapsed_time = 0
done = False

def draw_display(elapsed_time, laps_left, finished):
    screen.fill((0, 0, 0))

    # Time format
    hours = int(elapsed_time) // 3600
    minutes = (int(elapsed_time) % 3600) // 60
    seconds = int(elapsed_time) % 60
    time_str = f"{hours:02}:{minutes:02}:{seconds:02}"

    time_surface = font_large.render(f"Time: {time_str}", True, (255, 255, 255))
    screen.blit(time_surface, (50, 50))

    if finished:
        laps_surface = font_large.render(f"Laps: {laps_left}", True, (255, 200, 200))
        congrats_surface = font_large.render("Congratulations!!!", True, (100, 255, 100))
        screen.blit(laps_surface, (50, 120))
        screen.blit(congrats_surface, (50, 190))
    else:
        laps_surface = font_large.render(f"Laps Remaining: {laps_left}", True, (255, 200, 200))
        screen.blit(laps_surface, (50, 130))

    pygame.display.flip()

def handle_button_press():
    global started, start_time, remaining_laps, done
    if not started:
        started = True
        start_time = time.time()
    elif not done:
        if remaining_laps > 0:
            remaining_laps -= 1
        if remaining_laps == 0:
            done = True

# Attach button handler
start_lap_button.when_pressed = handle_button_press

# === Main Loop ===
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    if started and not done:
        elapsed_time = time.time() - start_time

    draw_display(elapsed_time, remaining_laps, done)
    clock.tick(30)
