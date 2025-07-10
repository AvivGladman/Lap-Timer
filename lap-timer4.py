
import pygame
import sys
import time
from gpiozero import Button

# === GPIO Setup ===
start_lap_button = Button(2)

# === Pygame Setup ===
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Lap Timer")
font_large = pygame.font.SysFont(None, 72)
font_medium = pygame.font.SysFont(None, 48)
font_small = pygame.font.SysFont(None, 36)
clock = pygame.time.Clock()

# === State ===
started = False
paused = False
start_time = None
elapsed_time = 0
pause_time = 0
done = False

remaining_laps = 0
total_laps = 0
lap_length_m = 0.0

# Input states
input_stage = "laps"  # 'laps' -> 'length' -> 'done'
length_input_text = ""

# === UI Buttons ===
button_width = 130
button_height = 50
spacing = 10

# Lap selection buttons
lap_options = [20, 40, 50, 100, 200]
lap_buttons = []
for i, val in enumerate(lap_options):
    rect = pygame.Rect(50 + i * (button_width + spacing), 200, button_width, button_height)
    lap_buttons.append((val, rect))

# Control buttons
start_button_rect = pygame.Rect(30, 350, button_width, button_height)
pause_button_rect = pygame.Rect(start_button_rect.right + spacing, 350, button_width, button_height)
lap_button_rect = pygame.Rect(pause_button_rect.right + spacing, 350, button_width, button_height)
minus_lap_button_rect = pygame.Rect(lap_button_rect.right + spacing, 350, button_width, button_height)

quit_button_rect = pygame.Rect(540, 10, 90, 40)
reset_button_rect = pygame.Rect(10, 10, 100, 40)

def draw_display(elapsed_time, laps_left, finished):
    screen.fill((0, 0, 0))

    # Reset and Quit buttons
    pygame.draw.rect(screen, (100, 100, 255), reset_button_rect)
    screen.blit(font_small.render("Reset", True, (255, 255, 255)), (reset_button_rect.x + 10, reset_button_rect.y + 8))

    pygame.draw.rect(screen, (200, 50, 50), quit_button_rect)
    screen.blit(font_small.render("Quit", True, (255, 255, 255)), (quit_button_rect.x + 10, quit_button_rect.y + 8))

    if input_stage == "laps":
        prompt_surface = font_small.render("Select number of laps:", True, (255, 255, 255))
        screen.blit(prompt_surface, (50, 150))
        for val, rect in lap_buttons:
            pygame.draw.rect(screen, (50, 150, 200), rect)
            label = font_small.render(str(val), True, (255, 255, 255))
            label_rect = label.get_rect(center=rect.center)
            screen.blit(label, label_rect)
    elif input_stage == "length":
        prompt_surface = font_small.render("Enter lap length (m): " + length_input_text, True, (255, 255, 255))
        screen.blit(prompt_surface, (50, 120))
    else:
        hours = int(elapsed_time) // 3600
        minutes = (int(elapsed_time) % 3600) // 60
        seconds = int(elapsed_time) % 60
        time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
        screen.blit(font_large.render(f"Time: {time_str}", True, (255, 255, 255)), (50, 80))

        if finished:
            screen.blit(font_medium.render(f"Laps: {total_laps}", True, (255, 200, 200)), (50, 160))
            screen.blit(font_medium.render("Congratulations!!!", True, (100, 255, 100)), (50, 280))
            distance = total_laps * lap_length_m * 2
            screen.blit(font_small.render(f"Distance: {distance:.2f} m", True, (200, 255, 200)), (50, 220))
        else:
            screen.blit(font_medium.render(f"Laps Remaining: {laps_left}", True, (255, 200, 200)), (50, 160))
            completed_laps = total_laps - remaining_laps
            screen.blit(font_medium.render(f"Completed Laps: {completed_laps}", True, (200, 255, 255)), (50, 210))

        # Buttons
        pygame.draw.rect(screen, (0, 100, 200), start_button_rect)
        screen.blit(font_small.render("Start", True, (255, 255, 255)), (start_button_rect.x + 35, start_button_rect.y + 12))

        pygame.draw.rect(screen, (200, 150, 50), pause_button_rect)
        screen.blit(font_small.render("Pause", True, (255, 255, 255)), (pause_button_rect.x + 30, pause_button_rect.y + 12))

        pygame.draw.rect(screen, (0, 200, 100), lap_button_rect)
        screen.blit(font_small.render("+ Lap", True, (255, 255, 255)), (lap_button_rect.x + 30, lap_button_rect.y + 12))

        pygame.draw.rect(screen, (0, 200, 100), minus_lap_button_rect)
        screen.blit(font_small.render("- Lap", True, (255, 255, 255)), (minus_lap_button_rect.x + 30, minus_lap_button_rect.y + 12))

    pygame.display.flip()

def handle_start():
    global started, start_time, paused, pause_time
    if not started:
        started = True
        start_time = time.time()
    elif paused:
        paused = False
        start_time += time.time() - pause_time

def handle_pause():
    global paused, pause_time
    if started and not paused:
        paused = True
        pause_time = time.time()

def handle_lap():
    global remaining_laps, done
    if started and not done and not paused:
        if remaining_laps > 0:
            remaining_laps -= 1
        if remaining_laps == 0:
            done = True

def handle_minus_lap():
    global remaining_laps
    if started and not done and not paused:
        remaining_laps += 1

def handle_reset():
    global started, done, start_time, elapsed_time, remaining_laps, paused, input_stage, length_input_text
    started = False
    paused = False
    done = False
    start_time = None
    elapsed_time = 0
    remaining_laps = total_laps
    input_stage = "laps"
    length_input_text = ""

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
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if quit_button_rect.collidepoint(event.pos):
                pygame.quit()
                sys.exit()
            elif reset_button_rect.collidepoint(event.pos):
                handle_reset()
            elif input_stage == "laps":
                for val, rect in lap_buttons:
                    if rect.collidepoint(event.pos):
                        total_laps = val
                        remaining_laps = val
                        input_stage = "length"
            elif input_stage == "done":
                if start_button_rect.collidepoint(event.pos):
                    handle_start()
                elif pause_button_rect.collidepoint(event.pos):
                    handle_pause()
                elif lap_button_rect.collidepoint(event.pos):
                    handle_lap()
                elif minus_lap_button_rect.collidepoint(event.pos):
                    handle_minus_lap()
        elif event.type == pygame.KEYDOWN and input_stage == "length":
            if event.key == pygame.K_RETURN:
                try:
                    lap_length_m = float(length_input_text)
                    input_stage = "done"
                except ValueError:
                    length_input_text = ""
            elif event.key == pygame.K_BACKSPACE:
                length_input_text = length_input_text[:-1]
            else:
                if event.unicode.isdigit() or event.unicode == '.':
                    length_input_text += event.unicode

    if started and not paused and not done:
        elapsed_time = time.time() - start_time

    draw_display(elapsed_time, remaining_laps, done)
    clock.tick(30)
