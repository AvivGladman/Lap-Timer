



import pygame
import sys
import time
import random
import math
from gpiozero import Button

# === GPIO Setup ===
start_lap_button = Button(2)

# === Pygame Setup ===
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Lap Timer")
screen_width, screen_height = screen.get_size()
font_huge = pygame.font.SysFont(None, min(screen_width//8, screen_height//8))
font_large = pygame.font.SysFont(None, min(screen_width//12, screen_height//12))
font_medium = pygame.font.SysFont(None, min(screen_width//20, screen_height//20))
font_small = pygame.font.SysFont(None, min(screen_width//30, screen_height//30))
clock = pygame.time.Clock()

# === Fireworks System ===
class Particle:
    def __init__(self, x, y, vx, vy, color, life, trail_length=5, gravity=0.1, size=3):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life
        self.gravity = gravity
        self.size = size
        self.trail = []
        self.trail_length = trail_length
        self.sparkle = random.random() < 0.3  # 30% chance to sparkle
        
    def update(self):
        # Add current position to trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.trail_length:
            self.trail.pop(0)
            
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1
        
        # Add some air resistance
        self.vx *= 0.995
        self.vy *= 0.995
        
    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            size = max(1, int(self.size * (self.life / self.max_life)))
            
            # Draw trail
            for i, (tx, ty) in enumerate(self.trail):
                trail_alpha = int(alpha * (i / len(self.trail)) * 0.5)
                trail_size = max(1, int(size * (i / len(self.trail))))
                trail_color = tuple(max(0, min(255, c - 50)) for c in self.color)
                pygame.draw.circle(screen, trail_color, (int(tx), int(ty)), trail_size)
            
            # Draw main particle
            if self.sparkle and (self.life % 6 < 3):
                # Sparkle effect
                sparkle_color = tuple(min(255, c + 50) for c in self.color)
                pygame.draw.circle(screen, sparkle_color, (int(self.x), int(self.y)), size + 1)
            
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)

class Firework:
    def __init__(self, x, y, firework_type=None):
        self.x = x
        self.y = y
        self.particles = []
        self.exploded = False
        self.vy = random.uniform(-15, -10)
        self.vx = random.uniform(-2, 2)
        self.color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        self.fuse = random.randint(60, 120)
        self.firework_type = firework_type or random.choice(['brocade', 'willow', 'bee', 'palm', 'star', 'classic'])
        
    def update(self):
        if not self.exploded:
            self.x += self.vx
            self.y += self.vy
            self.vy += 0.1
            self.fuse -= 1
            
            if self.fuse <= 0 or self.vy > 0:
                self.explode()
        else:
            for particle in self.particles[:]:
                particle.update()
                if particle.life <= 0:
                    self.particles.remove(particle)
                    
    def explode(self):
        self.exploded = True
        
        if self.firework_type == 'brocade':
            self.create_brocade()
        elif self.firework_type == 'willow':
            self.create_willow()
        elif self.firework_type == 'bee':
            self.create_bee()
        elif self.firework_type == 'palm':
            self.create_palm()
        elif self.firework_type == 'star':
            self.create_star()
        else:
            self.create_classic()
    
    def create_brocade(self):
        # Brocade: Symmetrical burst with long golden trails that droop gracefully
        # Use primarily golden colors with some variation
        colors = [
            (255, 215, 0),   # Gold
            (255, 223, 0),   # Light gold
            (255, 200, 0),   # Deep gold
            (255, 235, 59),  # Bright gold
            (255, 193, 7),   # Amber gold
        ]
        
        # Create main burst pattern - more organized than random
        num_main_rays = 16  # Even number for symmetry
        particles_per_ray = 2  # Multiple particles per ray for thickness
        
        for ray in range(num_main_rays):
            # Calculate angle for each ray
            base_angle = (ray / num_main_rays) * 2 * math.pi
            
            for p in range(particles_per_ray):
                # Add slight angle variation for each particle in the ray
                angle_variation = random.uniform(-0.1, 0.1)
                angle = base_angle + angle_variation
                
                # Vary speed slightly for more natural look
                speed = random.uniform(6, 9) + p * 0.5
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed
                
                # Longer life for characteristic long trails
                life = random.randint(80, 120)
                color = random.choice(colors)
                
                # Create particle with long trail and moderate gravity for drooping effect
                particle = Particle(
                    self.x, self.y, vx, vy, color, life, 
                    trail_length=20,  # Long trails
                    gravity=0.08,     # Moderate gravity for graceful droop
                    size=3
                )
                self.particles.append(particle)
        
        # Add some secondary particles for the crackling effect
        num_secondary = random.randint(12, 20)
        for _ in range(num_secondary):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 6)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.randint(40, 70)
            color = random.choice(colors)
            
            # Smaller particles with shorter trails for crackling effect
            particle = Particle(
                self.x, self.y, vx, vy, color, life,
                trail_length=8,
                gravity=0.12,
                size=2
            )
            # Make some particles sparkle more for crackling effect
            particle.sparkle = random.random() < 0.7  # Higher sparkle chance
            self.particles.append(particle)
    
    def create_willow(self):
        # Willow: Drooping, long-lasting trails
        colors = [(0, 255, 0), (34, 139, 34), (50, 205, 50)]  # Green variations
        num_particles = random.randint(15, 25)
        for _ in range(num_particles):
            angle = random.uniform(-math.pi/3, math.pi/3)  # More upward spread
            speed = random.uniform(5, 12)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 2  # Slight upward bias
            life = random.randint(80, 120)  # Long-lasting
            color = random.choice(colors)
            particle = Particle(self.x, self.y, vx, vy, color, life, trail_length=15, gravity=0.05, size=2)
            self.particles.append(particle)
    
    def create_bee(self):
        # Bee: Chaotic, buzzing motion
        colors = [(255, 255, 0), (255, 165, 0), (255, 140, 0)]  # Yellow/orange
        num_particles = random.randint(8, 15)
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.randint(60, 100)
            color = random.choice(colors)
            # Add random velocity changes for buzzing effect
            particle = BeeParticle(self.x, self.y, vx, vy, color, life)
            self.particles.append(particle)
    
    def create_palm(self):
        # Palm: Upward burst with falling trails
        colors = [(255, 0, 0), (255, 69, 0), (255, 140, 0)]  # Red/orange
        num_particles = random.randint(12, 20)
        for _ in range(num_particles):
            angle = random.uniform(-math.pi/2 - 0.5, -math.pi/2 + 0.5)  # Mostly upward
            speed = random.uniform(8, 15)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.randint(50, 90)
            color = random.choice(colors)
            particle = Particle(self.x, self.y, vx, vy, color, life, trail_length=12, gravity=0.15, size=3)
            self.particles.append(particle)
    
    def create_star(self):
        # Star: Perfect symmetrical burst
        colors = [(255, 255, 255), (255, 0, 255), (0, 255, 255)]  # Bright colors
        num_rays = 8
        particles_per_ray = 3
        for ray in range(num_rays):
            angle = (ray / num_rays) * 2 * math.pi
            for p in range(particles_per_ray):
                speed = 4 + p * 2
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed
                life = random.randint(45, 75)
                color = random.choice(colors)
                particle = Particle(self.x, self.y, vx, vy, color, life, trail_length=6, size=4)
                self.particles.append(particle)
    
    def create_classic(self):
        # Classic: Regular circular burst
        num_particles = random.randint(15, 30)
        for _ in range(num_particles):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            life = random.randint(30, 60)
            particle = Particle(self.x, self.y, vx, vy, self.color, life)
            self.particles.append(particle)
            
    def draw(self, screen):
        if not self.exploded:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 3)
        else:
            for particle in self.particles:
                particle.draw(screen)
                
    def is_finished(self):
        return self.exploded and len(self.particles) == 0

class BeeParticle(Particle):
    def __init__(self, x, y, vx, vy, color, life):
        super().__init__(x, y, vx, vy, color, life, trail_length=3, gravity=0.05, size=2)
        self.buzz_timer = 0
        self.buzz_direction = random.uniform(0, 2 * math.pi)
        
    def update(self):
        # Add buzzing motion
        self.buzz_timer += 1
        if self.buzz_timer % 8 == 0:
            self.buzz_direction = random.uniform(0, 2 * math.pi)
            buzz_strength = 0.5
            self.vx += math.cos(self.buzz_direction) * buzz_strength
            self.vy += math.sin(self.buzz_direction) * buzz_strength
        
        super().update()

# Fireworks manager
fireworks = []
firework_timer = 0

def add_firework(firework_type=None):
    x = random.randint(screen_width // 4, 3 * screen_width // 4)
    y = screen_height - 50
    fireworks.append(Firework(x, y, firework_type))

def update_fireworks():
    global firework_timer
    
    # Add new fireworks occasionally with variety
    firework_timer += 1
    if firework_timer > random.randint(25, 50):
        # Choose firework type with weighted probabilities
        firework_types = ['brocade', 'willow', 'bee', 'palm', 'star', 'classic']
        weights = [0.2, 0.15, 0.1, 0.2, 0.15, 0.2]  # Higher chance for more spectacular types
        firework_type = random.choices(firework_types, weights=weights)[0]
        add_firework(firework_type)
        firework_timer = 0
        
    # Update existing fireworks
    for firework in fireworks[:]:
        firework.update()
        if firework.is_finished():
            fireworks.remove(firework)

def draw_fireworks(screen):
    for firework in fireworks:
        firework.draw(screen)

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
# Top control buttons
button_width = 160
button_height = 50
top_button_y = 20

quit_button_rect = pygame.Rect(screen_width - button_width - 20, top_button_y, button_width, button_height)
reset_button_rect = pygame.Rect(20, top_button_y, button_width, button_height)

# Main control buttons (bottom area)
main_button_width = 160
main_button_height = 50
main_button_y = screen_height - main_button_height - 30
main_button_spacing = 30

start_button_rect = pygame.Rect(50, main_button_y, main_button_width, main_button_height)
pause_button_rect = pygame.Rect(start_button_rect.right + main_button_spacing, main_button_y, main_button_width, main_button_height)
lap_button_rect = pygame.Rect(pause_button_rect.right + main_button_spacing, main_button_y, main_button_width, main_button_height)
minus_lap_button_rect = pygame.Rect(lap_button_rect.right + main_button_spacing, main_button_y, main_button_width, main_button_height)

# Lap selection buttons
lap_button_width = screen_width // 7
lap_button_height = screen_height // 8
lap_buttons_y = screen_height // 3
lap_buttons_spacing = 30

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
length_button_width = screen_width // 4
length_button_height = screen_height // 8
length_buttons_y = screen_height // 3
length_buttons_spacing = 40

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

    # Draw fireworks in background if finished
    if finished:
        update_fireworks()
        draw_fireworks(screen)

    # Reset and Quit buttons
    pygame.draw.rect(screen, (100, 100, 255), reset_button_rect)
    reset_text = font_large.render("Reset", True, (255, 255, 255))
    reset_text_rect = reset_text.get_rect(center=reset_button_rect.center)
    screen.blit(reset_text, reset_text_rect)

    pygame.draw.rect(screen, (200, 50, 50), quit_button_rect)
    quit_text = font_large.render("Quit", True, (255, 255, 255))
    quit_text_rect = quit_text.get_rect(center=quit_button_rect.center)
    screen.blit(quit_text, quit_text_rect)

    if input_stage == "laps":
        # Display lap selection buttons
        prompt_surface = font_large.render("Select number of laps:", True, (255, 255, 255))
        prompt_rect = prompt_surface.get_rect(center=(screen_width // 2, (screen_height // 6)+50))
        screen.blit(prompt_surface, prompt_rect)
        
        for rect, value in lap_selection_buttons:
            pygame.draw.rect(screen, (0, 150, 200), rect)
            pygame.draw.rect(screen, (255, 255, 255), rect, 3)
            
            text_surface = font_large.render(str(value), True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)
            
    elif input_stage == "length":
        if length_input_mode == "buttons":
            # Display length selection buttons
            prompt_surface = font_large.render("Select lap length:", True, (255, 255, 255))
            prompt_rect = prompt_surface.get_rect(center=(screen_width // 2, (screen_height // 6)+50))
            screen.blit(prompt_surface, prompt_rect)
            
            for rect, value, label in length_selection_buttons:
                pygame.draw.rect(screen, (0, 150, 200), rect)
                pygame.draw.rect(screen, (255, 255, 255), rect, 3)
                
                text_surface = font_large.render(label, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=rect.center)
                screen.blit(text_surface, text_rect)
        else:
            # Display text input for custom length
            prompt_surface = font_large.render("Enter lap length (m):", True, (255, 255, 255))
            prompt_rect = prompt_surface.get_rect(center=(screen_width // 2, screen_height // 4))
            screen.blit(prompt_surface, prompt_rect)
            
            input_surface = font_huge.render(length_input_text, True, (255, 255, 100))
            input_rect = input_surface.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(input_surface, input_rect)
            
            instruction_surface = font_medium.render("Press Enter to confirm", True, (200, 200, 200))
            instruction_rect = instruction_surface.get_rect(center=(screen_width // 2, screen_height // 2 + 100))
            screen.blit(instruction_surface, instruction_rect)
        
    else:
        # Timer display area
        timer_y = (screen_height // 8)+75
        
        # Time display
        hours = int(elapsed_time) // 3600
        minutes = (int(elapsed_time) % 3600) // 60
        seconds = int(elapsed_time) % 60
        time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
        
        time_surface = font_huge.render(f"Time: {time_str}", True, (255, 255, 255))
        time_rect = time_surface.get_rect(center=(screen_width // 2, timer_y))
        screen.blit(time_surface, time_rect)

        # Status display area
        status_y = (screen_height // 3)+50
        
        if finished:
            laps_surface = font_huge.render(f"Total Laps: {total_laps}", True, (255, 200, 200))
            laps_rect = laps_surface.get_rect(center=(screen_width // 2, status_y))
            screen.blit(laps_surface, laps_rect)
            
            congrats_surface = font_huge.render("Congratulations!!!", True, (100, 255, 100))
            congrats_rect = congrats_surface.get_rect(center=(screen_width // 2, status_y + 80))
            screen.blit(congrats_surface, congrats_rect)
            
            distance = total_laps * lap_length_m
            distance_surface = font_huge.render(f"Distance: {distance:.2f} m", True, (200, 255, 200))
            distance_rect = distance_surface.get_rect(center=(screen_width // 2, status_y + 140))
            screen.blit(distance_surface, distance_rect)
        else:
            laps_remaining_surface = font_huge.render(f"Laps Remaining: {laps_left}", True, (255, 200, 200))
            laps_remaining_rect = laps_remaining_surface.get_rect(center=(screen_width // 2, status_y))
            screen.blit(laps_remaining_surface, laps_remaining_rect)
            
            completed_laps = total_laps - remaining_laps
            completed_surface = font_huge.render(f"Completed Laps: {completed_laps}", True, (200, 255, 255))
            completed_rect = completed_surface.get_rect(center=(screen_width // 2, status_y + 80))
            screen.blit(completed_surface, completed_rect)

            # Control buttons
            pygame.draw.rect(screen, (0, 100, 200), start_button_rect)
            start_text = font_large.render("Start", True, (255, 255, 255))
            start_text_rect = start_text.get_rect(center=start_button_rect.center)
            screen.blit(start_text, start_text_rect)

            pygame.draw.rect(screen, (200, 150, 50), pause_button_rect)
            pause_text = font_large.render("Pause", True, (255, 255, 255))
            pause_text_rect = pause_text.get_rect(center=pause_button_rect.center)
            screen.blit(pause_text, pause_text_rect)

            pygame.draw.rect(screen, (0, 200, 100), lap_button_rect)
            lap_text = font_large.render("+ Lap", True, (255, 255, 255))
            lap_text_rect = lap_text.get_rect(center=lap_button_rect.center)
            screen.blit(lap_text, lap_text_rect)

            pygame.draw.rect(screen, (200, 100, 0), minus_lap_button_rect)
            minus_lap_text = font_large.render("- Lap", True, (255, 255, 255))
            minus_lap_text_rect = minus_lap_text.get_rect(center=minus_lap_button_rect.center)
            screen.blit(minus_lap_text, minus_lap_text_rect)

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
            remaining_laps -= 2
        if remaining_laps == 0:
            done = True
            # Add spectacular initial fireworks when finishing
            initial_types = ['brocade', 'star', 'palm', 'willow']
            for firework_type in initial_types:
                add_firework(firework_type)

def handle_minus_lap():
    global remaining_laps
    if started and not done and not paused:
        remaining_laps += 2

def handle_reset():
    global started, done, start_time, elapsed_time, remaining_laps, paused, input_stage, length_input_text, length_input_mode, fireworks
    started = False
    paused = False
    done = False
    start_time = None
    elapsed_time = 0
    remaining_laps = total_laps
    input_stage = "laps"
    length_input_text = ""
    length_input_mode = "buttons"
    fireworks.clear()  # Clear any existing fireworks

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
