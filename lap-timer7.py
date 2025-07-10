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
screen_width, screen_height = screen.get_size()
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
input_stage = "laps"  # 'laps' -> 'length' -> 'done'
length_input_text = ""
length_input_mode = "buttons"  # 'buttons' or 'text'

# === UI Buttons ===
button_width = 130
button_height = 50
button_y = screen_height - 200
spacing = 10

start_button_rect = pygame.Rect(30, button_y, button_width, button_height)
pause_button_rect = pygame.Rect(start_button_rect.right + spacing, button_y, button_width, button_height)
lap_button_rect = pygame.Rect(pause_button_rect.right + spacing, button_y, button_width, button_height)
minus_lap_button_rect = pygame.Rect(lap_button_rect.right + spacing, button_y, button_width, button_height)

quit_button_rect = pygame.Rect(screen_width - 100, 10, 90, 40)
reset_button_rect = pygame.Rect(10, 10, 100, 40)

# Lap selection buttons
lap_button_width = 120
lap_button_height = 60
lap_buttons_y = 200
lap_buttons_spacing = 20

lap_values = [20, 40, 50, 100, 200]
lap_selection_buttons = []

# Calculate button positions to center them
total_width = len(lap_values) * lap_button_width + (len(lap_values) - 1) * lap_buttons_spacing
start_x = (screen_width - total_width) // 2

for i, value in enumerate(lap_values):
    x = start_x + i * (lap_button_width + lap_buttons_spacing)
    rect = pygame.Rect(x, lap_buttons_y, lap_button_width, lap_button_height)
    lap_selection_buttons.append((rect, value))

# Length selection buttons
length_button_width = 150
length_button_height = 60
length_buttons_y = 200
length_buttons_spacing = 30

length_values = [(8.5344, "28 ft"), (9.7536, "32 ft"), (None, "Other")]
length_selection_buttons = []

# Calculate button positions to center them
total_length_width = len(length_values) * length_button_width + (len(length_values) - 1) * length_buttons_spacing
start_length_x = (screen_width - total_length_width) // 2

for i, (value, label) in enumerate(length_values):
    x = start_length_x + i * (length_button_width + length_buttons_spacing)
    rect = pygame.Rect(x, length_buttons_y, length_button_width, length_button_height)
    length_selection_buttons.append((rect, value, label))

def draw_display(elapsed_time, laps_left, finished):
    screen.fill((0, 0, 0))

    # Reset and Quit buttons
    pygame.draw.rect(screen, (100, 100, 255), reset_button_rect)
    screen.blit(font_small.render("Reset", True, (255, 255, 255)), (reset_button_rect.x + 10, reset_button_rect.y + 8))

    pygame.draw.rect(screen, (200, 50, 50), quit_button_rect)
    screen.blit(font_small.render("Quit", True, (255, 255, 255)), (quit_button_rect.x + 10, quit_button_rect.y + 8))

    if input_stage == "laps":
        # Display lap selection buttons
        prompt_surface = font_medium.render("Select number of laps:", True, (255, 255, 255))
        prompt_rect = prompt_surface.get_rect(center=(screen_width // 2, 120))
        screen.blit(prompt_surface, prompt_rect)
        
        for rect, value in lap_selection_buttons:
            pygame.draw.rect(screen, (0, 150, 200), rect)
            pygame.draw.rect(screen, (255, 255, 255), rect, 2)
            
            text_surface = font_medium.render(str(value), True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)
            
    elif input_stage == "length":
        if length_input_mode == "buttons":
            # Display length selection buttons
            prompt_surface = font_medium.render("Select lap length:", True, (255, 255, 255))
            prompt_rect = prompt_surface.get_rect(center=(screen_width // 2, 120))
            screen.blit(prompt_surface, prompt_rect)
            
            for rect, value, label in length_selection_buttons:
                pygame.draw.rect(screen, (0, 150, 200), rect)
                pygame.draw.rect(screen, (255, 255, 255), rect, 2)
                
                text_surface = font_small.render(label, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=rect.center)
                screen.blit(text_surface, text_rect)
        else:
            # Display text input for custom length
            prompt_surface = font_medium.render("Enter lap length (m): " + length_input_text, True, (255, 255, 255))
            prompt_rect = prompt_surface.get_rect(center=(screen_width // 2, 120))
            screen.blit(prompt_surface, prompt_rect)
            
            instruction_surface = font_small.render("Press Enter to confirm", True, (200, 200, 200))
            instruction_rect = instruction_surface.get_rect(center=(screen_width // 2, 180))
            screen.blit(instruction_surface, instruction_rect)
        
    else:
        # Time display
        hours = int(elapsed_time) // 3600
        minutes = (int(elapsed_time) % 3600) // 60
        seconds = int(elapsed_time) % 60
        time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
        
        time_surface = font_large.render(f"Time: {time_str}", True, (255, 255, 255))
        screen.blit(time_surface, (50, 80))

        if finished:
            laps_surface = font_medium.render(f"Laps: {total_laps}", True, (255, 200, 200))
            screen.blit(laps_surface, (50, 160))
            
            congrats_surface = font_medium.render("Congratulations!!!", True, (100, 255, 100))
            screen.blit(congrats_surface, (50, 280))
            
            distance = total_laps * lap_length_m * 2
            distance_surface = font_small.render(f"Distance: {distance:.2f} m", True, (200, 255, 200))
            screen.blit(distance_surface, (50, 220))
        else:
            laps_remaining_surface = font_medium.render(f"Laps Remaining: {laps_left}", True, (255, 200, 200))
            screen.blit(laps_remaining_surface, (50, 160))
            
            completed_laps = total_laps - remaining_laps
            completed_surface = font_medium.render(f"Completed Laps: {completed_laps}", True, (200, 255, 255))
            screen.blit(completed_surface, (50, 210))

            # Control buttons
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
        # Resume from pause
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
    global started, done, start_time, elapsed_time, remaining_laps, paused, input_stage, length_input_text, length_input_mode
    started = False
    paused = False
    done = False
    start_time = None
    elapsed_time = 0
    remaining_laps = total_laps
    input_stage = "laps"
    length_input_text = ""
    length_input_mode = "buttons"

def select_laps(num_laps):
    global remaining_laps, total_laps, input_stage
    remaining_laps = num_laps
    total_laps = num_laps
    input_stage = "length"

def select_length(length_value):
    global lap_length_m, input_stage, length_input_mode
    if length_value is None:
        # User selected "Other" - switch to text input mode
        length_input_mode = "text"
    else:
        # User selected a preset length
        lap_length_m = length_value
        input_stage = "done"

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

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if quit_button_rect.collidepoint(event.pos):
                pygame.quit()
                sys.exit()
            elif reset_button_rect.collidepoint(event.pos):
                handle_reset()
            elif input_stage == "laps":
                # Check lap selection buttons
                for rect, value in lap_selection_buttons:
                    if rect.collidepoint(event.pos):
                        select_laps(value)
                        break
            elif input_stage == "length" and length_input_mode == "buttons":
                # Check length selection buttons
                for rect, value, label in length_selection_buttons:
                    if rect.collidepoint(event.pos):
                        select_length(value)
                        break
            elif input_stage == "done":
                if start_button_rect.collidepoint(event.pos):
                    handle_start()
                elif pause_button_rect.collidepoint(event.pos):
                    handle_pause()
                elif lap_button_rect.collidepoint(event.pos):
                    handle_lap()
                elif minus_lap_button_rect.collidepoint(event.pos):
                    handle_minus_lap()

        # Handle keyboard input for lap length
        if input_stage == "length" and length_input_mode == "text":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    try:
                        lap_length_m = float(length_input_text)
                        input_stage = "done"
                    except ValueError:
                        length_input_text = ""
                elif event.key == pygame.K_BACKSPACE:
                    length_input_text = length_input_text[:-1]
                else:
                    if (event.unicode.isdigit() or event.unicode == '.'):
                        length_input_text += event.unicode

    if started and not paused and not done:
        elapsed_time = time.time() - start_time

    draw_display(elapsed_time, remaining_laps, done)
    clock.tick(30)
