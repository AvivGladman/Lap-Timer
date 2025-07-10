import pygame
import sys
import time
from gpiozero import Button

# === GPIO Setup ===
start_lap_button = Button(2)

# === Pygame Setup ===
pygame.init()
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Lap Timer")
font_large = pygame.font.SysFont(None, 60)
font_small = pygame.font.SysFont(None, 40)
clock = pygame.time.Clock()

# === State ===
started = False
start_time = None
elapsed_time = 0
done = False
remaining_laps = 0
inputting_laps = True
lap_input_text = ""

# === UI Buttons ===
start_button_rect = pygame.Rect(50, 250, 200, 60)
lap_button_rect = pygame.Rect(350, 250, 200, 60)

def draw_display(elapsed_time, laps_left, finished):
    screen.fill((0, 0, 0))

    if inputting_laps:
        prompt_surface = font_small.render("Enter number of laps: " + lap_input_text, True, (255, 255, 255))
        screen.blit(prompt_surface, (50, 100))
    else:
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

        # Draw buttons
        pygame.draw.rect(screen, (0, 100, 200), start_button_rect)
        pygame.draw.rect(screen, (0, 200, 100), lap_button_rect)
        screen.blit(font_small.render("Start", True, (255, 255, 255)), (start_button_rect.x + 60, start_button_rect.y + 15))
        screen.blit(font_small.render("+ Lap", True, (255, 255, 255)), (lap_button_rect.x + 60, lap_button_rect.y + 15))

    pygame.display.flip()

def handle_start():
    global started, start_time
    if not started:
        started = True
        start_time = time.time()

def handle_lap():
    global remaining_laps, done
    if started and not done:
        if remaining_laps > 0:
            remaining_laps -= 1
        if remaining_laps == 0:
            done = True

# GPIO handler
def gpio_handler():
    if not started:
        handle_start()
    else:
        handle_lap()

start_lap_button.when_pressed = gpio_handler

# === Main Loop ===
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif inputting_laps:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    try:
                        remaining_laps = int(lap_input_text)
                        inputting_laps = False
                    except ValueError:
                        lap_input_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    lap_input_text = lap_input_text[:-1]
                else:
                    if event.unicode.isdigit():
                        lap_input_text += event.unicode

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if start_button_rect.collidepoint(event.pos):
                handle_start()
            elif lap_button_rect.collidepoint(event.pos):
                handle_lap()

    if started and not done:
        elapsed_time = time.time() - start_time

    draw_display(elapsed_time, remaining_laps, done)
    clock.tick(30)
