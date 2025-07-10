import pygame
import sys
import time
from gpiozero import Button

# === GPIO Setup ===
start_lap_button = Button(2)

# === Pygame Setup ===
pygame.init()
screen = pygame.display.set_mode((600, 450))
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
total_laps = 0
lap_length_m = 0

# Input states
input_stage = "laps"  # 'laps' -> 'length' -> 'done'
lap_input_text = ""
length_input_text = ""

# === UI Buttons ===
start_button_rect = pygame.Rect(50, 330, 200, 60)
lap_button_rect = pygame.Rect(350, 330, 200, 60)
quit_button_rect = pygame.Rect(500, 10, 80, 40)
reset_button_rect = pygame.Rect(10, 10, 100, 40)

def draw_display(elapsed_time, laps_left, finished):
    screen.fill((0, 0, 0))

    # Always draw Reset and Quit buttons
    pygame.draw.rect(screen, (100, 100, 255), reset_button_rect)
    screen.blit(font_small.render("Reset", True, (255, 255, 255)), (reset_button_rect.x + 10, reset_button_rect.y + 8))

    pygame.draw.rect(screen, (200, 50, 50), quit_button_rect)
    screen.blit(font_small.render("Quit", True, (255, 255, 255)), (quit_button_rect.x + 10, quit_button_rect.y + 8))

    if input_stage != "done":
        if input_stage == "laps":
            prompt_surface = font_small.render("Enter number of laps: " + lap_input_text, True, (255, 255, 255))
        elif input_stage == "length":
            prompt_surface = font_small.render("Enter lap length (m): " + length_input_text, True, (255, 255, 255))
        screen.blit(prompt_surface, (50, 100))
    else:
        # Time format
        hours = int(elapsed_time) // 3600
        minutes = (int(elapsed_time) % 3600) // 60
        seconds = int(elapsed_time) % 60
        time_str = f"{hours:02}:{minutes:02}:{seconds:02}"

        time_surface = font_large.render(f"Time: {time_str}", True, (255, 255, 255))
        screen.blit(time_surface, (50, 40))

        if finished:
            laps_surface = font_large.render(f"Laps: {total_laps}", True, (255, 200, 200))
            congrats_surface = font_large.render("Congratulations!!!", True, (100, 255, 100))
            distance = total_laps * lap_length_m * 2
            distance_surface = font_small.render(f"Distance: {distance} m", True, (200, 255, 200))
            screen.blit(laps_surface, (50, 110))
            screen.blit(congrats_surface, (50, 180))
            screen.blit(distance_surface, (50, 250))
        else:
            laps_surface = font_large.render(f"Laps Remaining: {laps_left}", True, (255, 200, 200))
            screen.blit(laps_surface, (50, 120))

        # Draw Start and +Lap buttons
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

def handle_reset():
    global started, done, start_time, elapsed_time, remaining_laps
    started = False
    done = False
    start_time = None
    elapsed_time = 0
    remaining_laps = total_laps

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

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if quit_button_rect.collidepoint(event.pos):
                pygame.quit()
                sys.exit()
            elif reset_button_rect.collidepoint(event.pos):
                handle_reset()
            elif input_stage == "done":
                if start_button_rect.collidepoint(event.pos):
                    handle_start()
                elif lap_button_rect.collidepoint(event.pos):
                    handle_lap()

        elif input_stage != "done":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if input_stage == "laps":
                        try:
                            remaining_laps = int(lap_input_text)
                            total_laps = remaining_laps
                            input_stage = "length"
                        except ValueError:
                            lap_input_text = ""
                    elif input_stage == "length":
                        try:
                            lap_length_m = int(length_input_text)
                            input_stage = "done"
                        except ValueError:
                            length_input_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    if input_stage == "laps":
                        lap_input_text = lap_input_text[:-1]
                    elif input_stage == "length":
                        length_input_text = length_input_text[:-1]
                else:
                    if event.unicode.isdigit():
                        if input_stage == "laps":
                            lap_input_text += event.unicode
                        elif input_stage == "length":
                            length_input_text += event.unicode

    if started and not done:
        elapsed_time = time.time() - start_time

    draw_display(elapsed_time, remaining_laps, done)
    clock.tick(30)
