import pygame
import random
import sys
import json
import os
import ctypes

try:
    ctypes.windll.user32.SetProcessDPIAware()
except:
    pass
# --- 1. CONFIGURATION & CONSTANTS ---
pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.mixer.init()

info = pygame.display.Info()
WINDOW_WIDTH  = info.current_w
WINDOW_HEIGHT = info.current_h
FIGHT_USED = False
current_run_score = 0
current_run_coins = 0


SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("CrashOut Racer")

scroll_speed = 7.0    
MAX_SPEED = 30.0      

# --- 2. ASSET LOADING ---

def get_font(size):
    try:
        return pygame.font.Font("assets/font.ttf", size)
    except:
        return pygame.font.SysFont("Arial", size, bold=True)

def load_sound(filename_base):
    path_wav = f"assets/{filename_base}.wav"
    path_mp3 = f"assets/{filename_base}.mp3"
    sound_obj = None
   
    if os.path.exists(path_wav):
        try: sound_obj = pygame.mixer.Sound(path_wav)
        except: pass
    elif os.path.exists(path_mp3):
        try: sound_obj = pygame.mixer.Sound(path_mp3)
        except: pass
        
    return sound_obj

COIN_SFX = load_sound("coin")
if COIN_SFX: COIN_SFX.set_volume(0.6)

POWERUP_SFX = load_sound("powerup")
if POWERUP_SFX: POWERUP_SFX.set_volume(0.8)

SHIELD_BREAK_SFX = load_sound("shield_down") # Make sure you have shield_break.wav or .mp3 in assets
if SHIELD_BREAK_SFX: SHIELD_BREAK_SFX.set_volume(0.8)

EXPLOSION_SFX = load_sound("explosion") 
if EXPLOSION_SFX: EXPLOSION_SFX.set_volume(0.9)

START_SFX = load_sound("start")
if START_SFX: START_SFX.set_volume(1.0)

# --- MAP LOADING ---

def load_and_scale(path):
    try:
        img = pygame.image.load(path).convert()
        return pygame.transform.scale(img, (WINDOW_WIDTH, WINDOW_HEIGHT))
    except:
        # Fallback als plaatje niet bestaat
        surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        surf.fill((50, 50, 50))
        return surf
def re_sync_display():
    global SCREEN, WINDOW_WIDTH, WINDOW_HEIGHT, BG, AREAS
    global ROAD_BG, ROAD_CITY, ROAD_FOREST, ROAD_SNOW, ROAD_DESERT
    
    # Get actual monitor resolution again
    info = pygame.display.Info()
    WINDOW_WIDTH = info.current_w
    WINDOW_HEIGHT = info.current_h
    
    # Re-establish Fullscreen
    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
    
    # Re-scale ALL background images to the new width/height
    ROAD_BG = load_and_scale("assets/road_bg.png")
    ROAD_CITY = load_and_scale("assets/road_city.png")
    ROAD_FOREST = load_and_scale("assets/road_forest.png")
    ROAD_SNOW = load_and_scale("assets/road_snow.png")
    ROAD_DESERT = load_and_scale("assets/road_desert.png")
    
    AREAS = [ROAD_BG, ROAD_CITY, ROAD_FOREST, ROAD_SNOW, ROAD_DESERT]
    BG = AREAS[current_area]

    global ROAD_WIDTH, ROAD_X, LANE_COORDS
    ROAD_WIDTH = int(WINDOW_WIDTH * 0.75)
    ROAD_X = (WINDOW_WIDTH - ROAD_WIDTH) // 2
    LANE_PADDING = int(ROAD_WIDTH * 0.04)
    REAL_ROAD_WIDTH = ROAD_WIDTH - (LANE_PADDING * 2)
    LANE_WIDTH = REAL_ROAD_WIDTH // 4
    
    LANE_COORDS = [
        ROAD_X + LANE_PADDING + (LANE_WIDTH * 0.5),
        ROAD_X + LANE_PADDING + (LANE_WIDTH * 1.5),
        ROAD_X + LANE_PADDING + (LANE_WIDTH * 2.5),
        ROAD_X + LANE_PADDING + (LANE_WIDTH * 3.5)  
    ]

# pas de paden aan naar jouw bestanden
ROAD_BG = load_and_scale("assets/road_bg.png")
ROAD_CITY   = load_and_scale("assets/road_city.png")
ROAD_FOREST = load_and_scale("assets/road_forest.png")
ROAD_SNOW   = load_and_scale("assets/road_snow.png")
ROAD_DESERT = load_and_scale("assets/road_desert.png")


AREAS = [ROAD_BG, ROAD_CITY, ROAD_FOREST, ROAD_SNOW,ROAD_DESERT]
current_area = 0
next_area = 0
transitioning = False
transition_alpha = 0
TRANSITION_SPEED = 5

BG = AREAS[current_area]  # wordt gebruikt in menu/shop


# --- 3. SAVE SYSTEM & DATA ---

CAR_SHOP = [
    {"id": 0, "name": "Classic", "price": 0,    "image": "assets/car.png"},
    {"id": 1, "name": "Blue",    "price": 500,  "image": "assets/car_blue.png"},
    {"id": 2, "name": "Taxi",    "price": 1000, "image": "assets/car_taxi.png"},
    {"id": 3, "name": "X-Mas Sled", "price": 0, "image": "assets/sled.png"},
]

default_data = {
    "username": "",
    "leaderboard": [],
    "coins": 0,
    "inventory": [0],
    "equipped": 0,
    "sound": True
}

def load_data():
    try:
        with open("save_data.json", "r") as f:
            data = json.load(f)
            for key, value in default_data.items():
                if key not in data:
                    data[key] = value
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return default_data.copy()

def save_data(data):
    with open("save_data.json", "w") as f:
        json.dump(data, f)

def reset_progress():
    global GAME_DATA
    current_name = GAME_DATA["username"]
    GAME_DATA = default_data.copy()
    GAME_DATA["username"] = current_name
    save_data(GAME_DATA)
    pygame.mixer.music.unpause()
    if not pygame.mixer.music.get_busy():
        try: pygame.mixer.music.play(-1)
        except: pass

GAME_DATA = load_data()

# --- 4. MUSIC SETUP ---
try:
    pygame.mixer.music.load("assets/theme.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
    if not GAME_DATA["sound"]:
        pygame.mixer.music.pause()
except:
    print("Music file not found.")

# --- 5. CLASSES & MATH ---

ROAD_WIDTH      = int(WINDOW_WIDTH * 0.75)
LANE_PADDING    = int(ROAD_WIDTH * 0.04)
REAL_ROAD_WIDTH = ROAD_WIDTH - (LANE_PADDING * 2)
LANE_WIDTH      = REAL_ROAD_WIDTH // 4  
ROAD_X          = (WINDOW_WIDTH - ROAD_WIDTH) // 2
FPS             = 60

LANE_COORDS = [
    ROAD_X + LANE_PADDING + (LANE_WIDTH * 0.5),
    ROAD_X + LANE_PADDING + (LANE_WIDTH * 1.5),
    ROAD_X + LANE_PADDING + (LANE_WIDTH * 2.5),
    ROAD_X + LANE_PADDING + (LANE_WIDTH * 3.5)  
]

class Button():
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            return True
        return False

    def changeColor(self, position):
        if self.checkForInput(position):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)

class SmokeParticle(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)
        size = random.randint(6, 12)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        alpha = random.randint(100, 180)
        pygame.draw.rect(self.image, (100, 100, 100, alpha), (0,0,size,size))
        self.rect = self.image.get_rect(center=pos)
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(2, 4)
        self.timer = 30

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.timer -= 1
        if self.timer <= 0:
            self.kill()

class SnowParticle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        size = random.randint(2, 4)
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        shade = random.randint(220, 255)
        self.image.fill((shade, shade, shade))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WINDOW_WIDTH)
        self.rect.y = random.randint(-WINDOW_HEIGHT, 0)
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(1.5, 3)

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        if self.rect.top > WINDOW_HEIGHT:
            self.rect.x = random.randint(0, WINDOW_WIDTH)
            self.rect.y = random.randint(-50, 0)

class TireMark(pygame.sprite.Sprite):
    def __init__(self, pos, speed):
        super().__init__()
        w, h = 6, 12
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        self.image.fill((30, 30, 30, 120))
        self.rect = self.image.get_rect(center=pos)
        self.lifetime = 100
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
        elif self.lifetime < 20:
            alpha = int(120 * (self.lifetime / 20))
            self.image.set_alpha(alpha)

class PlayerCar(pygame.sprite.Sprite):
    def __init__(self, image_path, tire_group):
        super().__init__()
        try:
            raw_image = pygame.image.load(image_path).convert_alpha()
            target_width = int(LANE_WIDTH * 1.2)
            scale = target_width / raw_image.get_width()
            new_h = int(raw_image.get_height() * scale)
            self.original_image = pygame.transform.scale(raw_image, (target_width, new_h))
        except:
            self.original_image = pygame.Surface((int(LANE_WIDTH*0.55), 80))
            self.original_image.fill((255, 0, 0))

        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.centerx = LANE_COORDS[1]
        self.rect.bottom  = WINDOW_HEIGHT - 20
        self.mask = pygame.mask.from_surface(self.image)

        self.x = float(self.rect.centerx)
        self.vx = 0.0
        self.accel = 1.8
        self.friction = 0.85
        self.max_side_speed = 25.0

        self.has_shield = False

        self.tire_group = tire_group
        self.trail_timer = 0

    def _spawn_tire_marks(self, road_speed):
        offset = self.rect.width * 0.25
        back_y = self.rect.bottom - 15
        left_pos  = (self.rect.centerx - offset, back_y)
        right_pos = (self.rect.centerx + offset, back_y)
        self.tire_group.add(TireMark(left_pos, road_speed))
        self.tire_group.add(TireMark(right_pos, road_speed))

    def update(self, scroll_speed=7.0):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.vx -= self.accel
        if keys[pygame.K_RIGHT]:
            self.vx += self.accel

        if self.vx > self.max_side_speed:
            self.vx = self.max_side_speed
        if self.vx < -self.max_side_speed:
            self.vx = -self.max_side_speed

        self.vx *= self.friction

        self.x += self.vx
        self.rect.centerx = int(self.x)

        self.trail_timer += 1
        if self.trail_timer >= 3:
            self.trail_timer = 0
            self._spawn_tire_marks(scroll_speed)

        angle = -self.vx * 0.8
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

        if self.rect.left < ROAD_X + LANE_PADDING:
            self.rect.left = ROAD_X + LANE_PADDING
            self.x = self.rect.centerx
            self.vx = 0
        if self.rect.right > ROAD_X + ROAD_WIDTH - LANE_PADDING:
            self.rect.right = ROAD_X + ROAD_WIDTH - LANE_PADDING
            self.x = self.rect.centerx
            self.vx = 0

class EnemyCar(pygame.sprite.Sprite):
    def __init__(self, speed):
        pygame.sprite.Sprite.__init__(self)
       
        if random.random() < 0.10:
            selected_car = "assets/sport_green.png"
        else:
            options = ["assets/sport_red.png", "assets/sport_yellow.png", "assets/sport_blue.png"]
            selected_car = random.choice(options)
           
        try:
            raw_image = pygame.image.load(selected_car).convert_alpha()
            target_width = int(LANE_WIDTH * 0.55)
            scale = target_width / raw_image.get_width()
            new_h = int(raw_image.get_height() * scale)
            scaled_image = pygame.transform.scale(raw_image, (target_width, new_h))
            self.image = pygame.transform.rotate(scaled_image, 180)
        except:
            w = int(LANE_WIDTH * 0.55)
            h = int(w * 1.5)
            self.image = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (200, 0, 0), (0, 0, w, h), border_radius=8)
       
        self.rect = self.image.get_rect()
        lane = random.choice(LANE_COORDS)
        self.rect.centerx = lane
        self.rect.bottom = -20
        self.mask = pygame.mask.from_surface(self.image)
        self.speed_y = speed

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

class WarningSign(pygame.sprite.Sprite):
    def __init__(self, lane_x, car_speed, enemy_group, sprite_group):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, (255, 255, 0), [(25, 0), (0, 50), (50, 50)])
        pygame.draw.rect(self.image, (0,0,0), (22, 10, 6, 25))
        pygame.draw.circle(self.image, (0,0,0), (25, 42), 4)

        self.rect = self.image.get_rect()
        self.rect.centerx = lane_x
        self.rect.y = 100
       
        self.timer = 60
        self.blink_speed = 10
        self.blink_timer = 0
       
        self.lane_x = lane_x
        self.car_speed = car_speed
        self.enemy_group = enemy_group
        self.sprite_group = sprite_group

    def update(self):
        self.timer -= 1
        self.blink_timer += 1
        if self.blink_timer >= self.blink_speed:
            self.blink_timer = 0
            if self.image.get_alpha() == 255: self.image.set_alpha(50)
            else: self.image.set_alpha(255)

        if self.timer <= 0:
            enemy = EnemyCar(self.car_speed)
            enemy.rect.centerx = self.lane_x
            enemy.rect.bottom = -20
            pygame.sprite.spritecollide(enemy, self.enemy_group, True)
            self.enemy_group.add(enemy)
            self.sprite_group.add(enemy)
            self.kill()

class ShieldItem(pygame.sprite.Sprite):
    def __init__(self, speed):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 100, 255, 100), (25, 25), 25)
        pygame.draw.circle(self.image, (0, 255, 255), (25, 25), 15)
       
        self.rect = self.image.get_rect()
        lane = random.choice(LANE_COORDS)
        self.rect.centerx = lane
        self.rect.bottom = -20
        self.mask = pygame.mask.from_surface(self.image)
        self.speed_y = speed

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

class Coin(pygame.sprite.Sprite):
    def __init__(self, speed):
        pygame.sprite.Sprite.__init__(self)
        try:
            raw_image = pygame.image.load("assets/coin.png").convert_alpha()
            self.image = pygame.transform.scale(raw_image, (50, 50))
        except:
            self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 215, 0), (25, 25), 25)

        self.rect = self.image.get_rect()
        lane = random.choice(LANE_COORDS)
        self.rect.centerx = lane
        self.rect.bottom = -20
        self.mask = pygame.mask.from_surface(self.image)
        self.speed_y = speed

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > WINDOW_HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, style="fire"):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((300, 300), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)
        self.lifetime = 40
        self.particles = []
        if style == "blue":
            colors = [(0, 255, 255), (0, 150, 255), (0, 50, 255), (200, 200, 255), (255, 255, 255)]
        else:
            colors = [(255, 255, 0), (255, 100, 0), (255, 0, 0), (80, 80, 80), (255, 255, 255)]
        for _ in range(40):
            x, y = 150, 150
            vx = random.randint(-8, 8)
            vy = random.randint(-8, 8)
            color = random.choice(colors)
            size = random.randint(4, 10)
            self.particles.append([x, y, vx, vy, color, size])

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
            return
        self.image.fill((0, 0, 0, 0))
        for p in self.particles:
            p[0] += p[2]
            p[1] += p[3]
            pygame.draw.rect(self.image, p[4], (p[0], p[1], p[5], p[5]))

def area_for_score(score):
    if score < 2500:
        return 0
    elif score < 4000:
        return 1
    elif score < 5800:
        return 2
    elif score < 10000:
        return 3
    else:
        return 3

def start_area_transition(new_area):
    global transitioning, next_area, transition_alpha, current_area
    if new_area == current_area:
        return
    next_area = new_area
    transitioning = True
    transition_alpha = 0

def update_area_for_score(score):
    global current_area, transitioning
    new_area = area_for_score(score)
    if new_area != current_area and not transitioning:
        start_area_transition(new_area)


def draw_background(surface, scroll_y, score):
    global current_area, transitioning, transition_alpha
    update_area_for_score(score)

    base_img = AREAS[current_area]
    h = WINDOW_HEIGHT
    rel = scroll_y % h

    # basisbiome
    surface.blit(base_img, (0, int(rel - h)))
    surface.blit(base_img, (0, int(rel)))

    # overgang naar volgende biome
    if transitioning:
        top_img = AREAS[next_area].copy()
        top_img.set_alpha(transition_alpha)
        surface.blit(top_img, (0, int(rel - h)))
        surface.blit(top_img, (0, int(rel)))
        transition_alpha += TRANSITION_SPEED

        transition_alpha += TRANSITION_SPEED
        if transition_alpha >= 255:
            transition_alpha = 255
            transition_alpha = 0 # reset for next time
            transitioning = False
            current_area = next_area


# --- FIGHT & TRANSITION KOPPELING ---

def start_fight():
    global current_area
    import fight
    pygame.mixer.music.stop() 
    
    area_names = ["suburbs", "city", "forest", "snow", "desert"]
    current_biome = area_names[current_area]
    print(f"CAR SCRIPT SENDING: {current_biome}")
    # 2. Run the fight
    victory = fight.main(current_biome)

    re_sync_display()
    if victory:
        try:
            pygame.mixer.music.load("assets/theme.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
            if not GAME_DATA["sound"]:
                pygame.mixer.music.pause()
        except:
            print("Could not reload car theme.")
            
        display_win_message()
        return True 
    else:
        # If defeat, keep music stopped or play a game-over sound
        print("Defeat! Game Over.")
        return False   

def crash_transition():
    global SCREEN
    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
    """Transition na crash, daarna fight starten en resultaat teruggeven."""
    clock = pygame.time.Clock()
    duration = 180  # ~2 seconden

    t = 0
    while t < duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        alpha = int(255 * (t / duration))
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill((80, 0, 0))
        overlay.set_alpha(alpha)
        SCREEN.blit(overlay, (0, 0))

        scale = 0.25 + (t / duration)
        # 1. Render "CRASH!" (Bigger font)
        crash_font_size = int(100 * scale)
        crash_txt = get_font(crash_font_size).render("CRASH!", True, (255, 255, 255))
        crash_rect = crash_txt.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40))
        
        # 2. Render instructions (Smaller font)
        sub_font_size = int(40 * scale)
        sub_txt = get_font(sub_font_size).render("FIGHT HIM TO CONTINUE!", True, (255, 255, 255))
        sub_rect = sub_txt.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))

        # Draw both
        SCREEN.blit(crash_txt, crash_rect)
        SCREEN.blit(sub_txt, sub_rect)

        pygame.display.flip()
        clock.tick(FPS)
        t += 1

    # heel belangrijk: geef hier het resultaat terug
    return start_fight()

def display_win_message():
    """Laat zien dat je gewonnen hebt voordat de race doorgaat"""
    clock = pygame.time.Clock()
    duration = 60 # 2.5 seconden
    
    t = 0
    while t < duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
        # Groene overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill((0, 100, 0))
        overlay.set_alpha(150)
        SCREEN.blit(overlay, (0, 0))
        
        # Tekst
        win_txt = get_font(50).render("YOU WON!", True, (255, 255, 255))
        cont_txt = get_font(30).render("CONTINUING RACING...", True, (200, 255, 200))
        
        SCREEN.blit(win_txt, (WINDOW_WIDTH//2 - win_txt.get_width()//2, WINDOW_HEIGHT//2 - 50))
        SCREEN.blit(cont_txt, (WINDOW_WIDTH//2 - cont_txt.get_width()//2, WINDOW_HEIGHT//2 + 20))
        
        pygame.display.flip()
        clock.tick(FPS)
        t += 1

# --- 6. USERNAME & LEADERBOARD SCREENS ---

def get_username():
    if GAME_DATA["username"]:
        return
   
    input_box = pygame.Rect(WINDOW_WIDTH//2 - 150, WINDOW_HEIGHT//2, 300, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_active
    text = ''
    done = False
   
    while not done:
        SCREEN.fill((30, 30, 30))
        title = get_font(50).render("ENTER USERNAME", True, (255, 255, 255))
        SCREEN.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, WINDOW_HEIGHT//2 - 100))
       
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if len(text) > 0:
                        GAME_DATA["username"] = text
                        save_data(GAME_DATA)
                        if START_SFX and GAME_DATA["sound"]:
                            START_SFX.play()
                        done = True
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    if len(text) < 10:
                        text += event.unicode
       
        txt_surface = get_font(40).render(text, True, color)
        SCREEN.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(SCREEN, color, input_box, 2)
        pygame.display.flip()

def leaderboard():
    while True:
        SCREEN.blit(BG, (0, 0))
        MOUSE_POS = pygame.mouse.get_pos()
       
        TITLE = get_font(60).render("LEADERBOARD", True, "#b68f40")
        TITLE_RECT = TITLE.get_rect(center=(WINDOW_WIDTH // 2, 80))
        SCREEN.blit(TITLE, TITLE_RECT)
       
        BACK_BTN = Button(image=None, pos=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 80),
                          text_input="BACK", font=get_font(40), base_color="White", hovering_color="Green")
        BACK_BTN.changeColor(MOUSE_POS)
        BACK_BTN.update(SCREEN)
       
        leader_list = GAME_DATA.get("leaderboard", [])
        start_y = 180
       
        if not leader_list:
            no_score = get_font(30).render("No High Scores Yet!", True, "White")
            SCREEN.blit(no_score, (WINDOW_WIDTH//2 - no_score.get_width()//2, start_y))
        else:
            for i, entry in enumerate(leader_list[:5]):
                name = entry['name']
                score = entry['score']
                score_str = f"{i+1}. {name}: {score}"
               
                txt = get_font(35).render(score_str, True, (255, 215, 0))
                SCREEN.blit(txt, (WINDOW_WIDTH//2 - txt.get_width()//2, start_y))
                start_y += 60

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if BACK_BTN.checkForInput(MOUSE_POS):
                    return

        pygame.display.update()

# --- 7. GAME LOOPS (SHOP & PLAY) ---

def shop():
    pygame.mouse.set_visible(True)
    while True:
        SCREEN.blit(BG, (0, 0))
        MOUSE_POS = pygame.mouse.get_pos()

        TITLE = get_font(50).render("CAR SHOP", True, (255, 255, 255))
        TITLE_RECT = TITLE.get_rect(center=(WINDOW_WIDTH // 2, 60))
        SCREEN.blit(TITLE, TITLE_RECT)
       
        MONEY_TEXT = get_font(30).render(f"Coins: {GAME_DATA['coins']}", True, (255, 215, 0))
        SCREEN.blit(MONEY_TEXT, (20, 20))

        BACK_BTN = Button(image=None, pos=(80, 550),
                          text_input="BACK", font=get_font(30), base_color="White", hovering_color="Green")
        BACK_BTN.changeColor(MOUSE_POS)
        BACK_BTN.update(SCREEN)

        y_pos = 180
        buttons = []
       
        for car in CAR_SHOP:
            if car["id"] == 3 and car["id"] not in GAME_DATA["inventory"]:
                continue

            car_id = car["id"]
            name = car["name"]
            price = car["price"]
            image_path = car["image"]
           
            try:
                car_preview = pygame.image.load(image_path).convert_alpha()
                asp = car_preview.get_height() / car_preview.get_width()
                car_preview = pygame.transform.scale(car_preview, (150, int(150*asp)))
            except:
                car_preview = pygame.Surface((150, 80))
                car_preview.fill((100,100,100))
           
            preview_rect = car_preview.get_rect(center=(WINDOW_WIDTH * 0.25, y_pos))
            SCREEN.blit(car_preview, preview_rect)

            if car_id == GAME_DATA["equipped"]:
                status_text = "EQUIPPED"
                color = (0, 255, 0)
            elif car_id in GAME_DATA["inventory"]:
                status_text = "SELECT"
                color = (255, 255, 255)
            else:
                status_text = f"BUY ({price})"
                color = (200, 0, 0)

            NAME_TXT = get_font(40).render(name, True, (255, 255, 255))
            NAME_RECT = NAME_TXT.get_rect(center=(WINDOW_WIDTH * 0.5, y_pos))
            SCREEN.blit(NAME_TXT, NAME_RECT)

            BTN = Button(image=None, pos=(WINDOW_WIDTH * 0.75, y_pos),
                         text_input=status_text, font=get_font(30), base_color=color, hovering_color="Gray")
            BTN.changeColor(MOUSE_POS)
            BTN.update(SCREEN)
            buttons.append({"btn": BTN, "id": car_id, "price": price})
            y_pos += 150

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_data(GAME_DATA)
                pygame.quit()
                sys.exit()
           
            if event.type == pygame.MOUSEBUTTONDOWN:
                if BACK_BTN.checkForInput(MOUSE_POS):
                    main_menu()
               
                for item in buttons:
                    if item["btn"].checkForInput(MOUSE_POS):
                        c_id = item["id"]
                        c_price = item["price"]
                       
                        if c_id in GAME_DATA["inventory"]:
                            GAME_DATA["equipped"] = c_id
                            save_data(GAME_DATA)
                        else:
                            if GAME_DATA["coins"] >= c_price:
                                GAME_DATA["coins"] -= c_price
                                GAME_DATA["inventory"].append(c_id)
                                GAME_DATA["equipped"] = c_id
                                save_data(GAME_DATA)
        pygame.display.update()

# --- PLAY FUNCTIE MET ARGUMENTEN ---
def play(start_score=0, start_coins=0):
    global SCREEN
    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
    global FIGHT_USED, current_run_score, current_run_coins

    if GAME_DATA["sound"]:
        if not pygame.mixer.music.get_busy(): # If no music is playing
            try:
                pygame.mixer.music.load("assets/theme.mp3")
                pygame.mixer.music.set_volume(0.5)
                pygame.mixer.music.play(-1)
            except:
                print("Theme music file not found.")

    pygame.mouse.set_visible(True)
    clock = pygame.time.Clock()
    
    # Gebruik doorgegeven waardes (voor als je doorgaat na fight)
    score = start_score
    coins_collected = start_coins
   
    equipped_id = GAME_DATA["equipped"]
    car_info = next(item for item in CAR_SHOP if item["id"] == equipped_id)
    image_path = car_info["image"]
   
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    smoke_group = pygame.sprite.Group()
    tire_group  = pygame.sprite.Group()
    snow_group  = pygame.sprite.Group()
   
    for _ in range(200):
        snow_group.add(SnowParticle())
   
    player = PlayerCar(image_path, tire_group)
    all_sprites.add(player)

    game_over = False
    crashed = False
    paused = False
    
    scroll_speed = 7.0    
    MAX_SPEED = 30.0      
   
    scroll_offset = 0
    enemy_timer = 0
    coin_timer = 0
    powerup_timer = 0
    spawn_rate = 60
    smoke_timer = 0
    unlock_message_timer = 0

    countdown = True
    countdown_start_time = pygame.time.get_ticks()
    score_saved = False

    while True:
        MOUSE_POS = pygame.mouse.get_pos()

        if not pygame.display.get_active():
            pygame.mixer.music.pause()
            paused = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GAME_DATA["coins"] += coins_collected
                save_data(GAME_DATA)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not game_over:
                        paused = not paused
                    else:
                        if not score_saved:
                            GAME_DATA["coins"] += coins_collected
                            save_data(GAME_DATA)
                        main_menu()
                if event.key == pygame.K_r and game_over:
                    FIGHT_USED = False
                    play() # Reset volledig bij echte Game Over
           
            if event.type == pygame.MOUSEBUTTONDOWN and paused:
                if RESUME_BTN.checkForInput(MOUSE_POS):
                    paused = False
                if MENU_BTN.checkForInput(MOUSE_POS):
                    GAME_DATA["coins"] += coins_collected
                    save_data(GAME_DATA)
                    main_menu()

        if not game_over and not paused:
            pygame.mouse.set_visible(False)
           
            if countdown:
                now = pygame.time.get_ticks()
                elapsed = now - countdown_start_time
                if elapsed > 3500:
                    countdown = False
           
            elif crashed:
                all_sprites.update()
                explosions = [s for s in all_sprites if isinstance(s, Explosion)]
                if not explosions:
                    game_over = True
            else:
                scroll_offset += scroll_speed
                # Alleen score optellen als we niet crashen
                score += 1
                update_area_for_score(score)

                if score >= 5000 and 3 not in GAME_DATA["inventory"]:
                    GAME_DATA["inventory"].append(3)
                    save_data(GAME_DATA)
                    unlock_message_timer = 180

                target_spawn_rate = 70 - (scroll_speed * 1.8)
                spawn_rate = max(15, int(target_spawn_rate))

                smoke_timer += 1
                if smoke_timer >= 4:
                    smoke_timer = 0
                    exhaust_pos = (player.rect.centerx, player.rect.bottom - 5)
                    puff = SmokeParticle(exhaust_pos)
                    smoke_group.add(puff)

                enemy_timer += 1
                if enemy_timer >= spawn_rate:
                    enemy_timer = 0
                    base_enemy_speed = 8
                    difficulty_factor = int(scroll_speed * 0.25)
                    final_traffic_speed = base_enemy_speed + difficulty_factor

                    blocked_lanes = []
                    for s in all_sprites:
                        if isinstance(s, WarningSign):
                            blocked_lanes.append(s.lane_x)

                    if random.random() < 0.2:
                        lane = random.choice(LANE_COORDS)
                        fast_speed = final_traffic_speed + 5
                        warning = WarningSign(lane, fast_speed, enemies, all_sprites)
                        all_sprites.add(warning)
                    else:
                        speed = final_traffic_speed + random.randint(0, 3)
                        enemy = EnemyCar(speed)
                       
                        if enemy.rect.centerx in blocked_lanes:
                            enemy.kill()
                        elif not pygame.sprite.spritecollideany(enemy, enemies):
                            enemies.add(enemy)
                            all_sprites.add(enemy)
                        else:
                            enemy.kill()

                coin_timer += 1
                if coin_timer >= 40:
                    coin_timer = 0
                    new_coin = Coin(scroll_speed)
                    if not pygame.sprite.spritecollideany(new_coin, enemies):
                        coins.add(new_coin)
                        all_sprites.add(new_coin)
                    else:
                        new_coin.kill()

                powerup_timer += 1
                if powerup_timer >= 400:
                    powerup_timer = 0
                    shield_orb = ShieldItem(scroll_speed)
                    if not pygame.sprite.spritecollideany(shield_orb, enemies):
                        powerups.add(shield_orb)
                        all_sprites.add(shield_orb)
                    else:
                        shield_orb.kill()

                player.update(scroll_speed)
               
                enemies.update()
                coins.update()
                powerups.update()
                smoke_group.update()
                tire_group.update()
                snow_group.update()
                all_sprites.update()

                hits = pygame.sprite.spritecollide(player, coins, True, pygame.sprite.collide_mask)
                for hit in hits:
                    if COIN_SFX and GAME_DATA["sound"]: COIN_SFX.play()
                    coins_collected += 1
                    score += 100
                    if scroll_speed < MAX_SPEED:
                        scroll_speed += 0.2

                shield_hits = pygame.sprite.spritecollide(player, powerups, True, pygame.sprite.collide_mask)
                for hit in shield_hits:
                    if POWERUP_SFX and GAME_DATA["sound"]: POWERUP_SFX.play()
                    player.has_shield = True
               
               

                enemy_hits = pygame.sprite.spritecollide(player, enemies, False, pygame.sprite.collide_mask)
                if enemy_hits:
                    if player.has_shield:
                        player.has_shield = False
                        if SHIELD_BREAK_SFX:
                            SHIELD_BREAK_SFX.play()
                        blue_pop = Explosion(player.rect.center, style="blue")
                        all_sprites.add(blue_pop)
                        for enemy in enemy_hits:
                            boom = Explosion(enemy.rect.center, style="fire")
                            all_sprites.add(boom)
                            enemy.kill()
                    else:
                        # CRASH LOGICA
                        crashed = True

                        if EXPLOSION_SFX and GAME_DATA["sound"]:
                            EXPLOSION_SFX.play()

                        boom = Explosion(player.rect.center, style="fire")
                        all_sprites.add(boom)
                        player.kill()
                        smoke_group.empty()

                        # Als we nog niet gevochten hebben, start fight logic
                        if not FIGHT_USED:
                            # Eerst even de explosie laten zien
                            crash_timer = pygame.time.get_ticks()
                            while pygame.time.get_ticks() - crash_timer < 500:
                                draw_background(SCREEN, scroll_offset, score)
                                snow_group.draw(SCREEN)
                                tire_group.draw(SCREEN)
                                smoke_group.update() # Update smoke voor effect
                                smoke_group.draw(SCREEN)
                                all_sprites.update()
                                all_sprites.draw(SCREEN)
                                pygame.display.flip()
                                clock.tick(FPS)

                            FIGHT_USED = True
                            won = crash_transition()
                            
                            if won:
                                display_win_message() # Laat You Won bericht zien
                                # HERSTART MET HUIDIGE SCORE/COINS
                                SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
                                return play(score, coins_collected)
                            else:
                                # Verloren -> Game Over
                                GAME_DATA["coins"] += coins_collected
                                save_data(GAME_DATA)
                                pygame.mouse.set_visible(True)
                                main_menu() # THIS takes you back to car menu
                                return
                        else:
                            # Al gevochten? Dan gewoon game over animatie afmaken
                            pass


        draw_background(SCREEN, scroll_offset, score)

       
        snow_group.draw(SCREEN)
        tire_group.draw(SCREEN)
        smoke_group.draw(SCREEN)
        all_sprites.draw(SCREEN)

        if not crashed and not game_over and player.has_shield:
            pygame.draw.circle(SCREEN, (0, 200, 255), player.rect.center, 75, 4)
       
        score_text = get_font(30).render(f"SCORE: {score}", True, (255, 255, 255))
        coin_text = get_font(30).render(f"COINS: {coins_collected}", True, (255, 215, 0))
        SCREEN.blit(score_text, (20, 20))
        SCREEN.blit(coin_text, (20, 60))

        if countdown and not paused:
            now = pygame.time.get_ticks()
            elapsed = now - countdown_start_time
            count_text = ""
            count_color = (255, 255, 255)
           
            if elapsed < 1000:
                count_text = "3"
            elif elapsed < 2000:
                count_text = "2"
            elif elapsed < 3000:
                count_text = "1"
            else:
                count_text = "GO!"
                count_color = (255, 0, 0)
           
            if count_text:
                txt_surf = get_font(120).render(count_text, True, count_color)
                outline_surf = get_font(120).render(count_text, True, (0,0,0))
                center_rect = txt_surf.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
                SCREEN.blit(outline_surf, (center_rect.x+4, center_rect.y+4))
                SCREEN.blit(txt_surf, center_rect)

        if paused:
            pygame.mouse.set_visible(True)
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            SCREEN.blit(overlay, (0, 0))
           
            pause_txt = get_font(60).render("PAUSED", True, "White")
            SCREEN.blit(pause_txt, (WINDOW_WIDTH//2 - pause_txt.get_width()//2, WINDOW_HEIGHT//2 - 100))
           
            RESUME_BTN = Button(image=None, pos=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2),
                                text_input="RESUME", font=get_font(40), base_color="White", hovering_color="Green")
            MENU_BTN = Button(image=None, pos=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 70),
                              text_input="MAIN MENU", font=get_font(40), base_color="White", hovering_color="Red")
           
            RESUME_BTN.changeColor(MOUSE_POS)
            RESUME_BTN.update(SCREEN)
            MENU_BTN.changeColor(MOUSE_POS)
            MENU_BTN.update(SCREEN)

        if unlock_message_timer > 0 and not paused:
            unlock_message_timer -= 1
            if (unlock_message_timer // 10) % 2 == 0:
                msg = get_font(40).render("SECRET UNLOCKED: X-MAS SLED!", True, (0, 255, 0))
                rect = msg.get_rect(center=(WINDOW_WIDTH//2, 150))
                pygame.draw.rect(SCREEN, (0,0,0), rect.inflate(20, 10))
                SCREEN.blit(msg, rect)

        if game_over:
            pygame.mouse.set_visible(True)
            if not score_saved:
                GAME_DATA["coins"] += coins_collected
                GAME_DATA["leaderboard"].append({"name": GAME_DATA["username"], "score": score})
                GAME_DATA["leaderboard"].sort(key=lambda x: x["score"], reverse=True)
                GAME_DATA["leaderboard"] = GAME_DATA["leaderboard"][:10]
                save_data(GAME_DATA)
                score_saved = True

            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((50, 0, 0))
            SCREEN.blit(overlay, (0,0))
           

            go_text = get_font(60).render("CRASHED!", True, (255, 255, 255))
            final_coin = get_font(40).render(f"Collected: {coins_collected}", True, (255, 215, 0))
            restart_text = get_font(30).render("Press 'R' to Restart", True, (255, 255, 255))
           
            SCREEN.blit(go_text, (WINDOW_WIDTH//2 - go_text.get_width()//2, WINDOW_HEIGHT//2 - 80))
            SCREEN.blit(final_coin, (WINDOW_WIDTH//2 - final_coin.get_width()//2, WINDOW_HEIGHT//2))
            SCREEN.blit(restart_text, (WINDOW_WIDTH//2 - restart_text.get_width()//2, WINDOW_HEIGHT//2 + 60))

        pygame.display.flip()
        clock.tick(FPS)

# --- 8. MAIN MENU ---

def main_menu():
    get_username()
   
    pygame.mouse.set_visible(True)
    while True:
        SCREEN.blit(BG, (0, 0))
        MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(60).render("CrashOut Racer", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(WINDOW_WIDTH // 2, 80))

        user_txt = get_font(20).render(f"Player: {GAME_DATA['username']}", True, "White")
        SCREEN.blit(user_txt, (10, 10))

        PLAY_BUTTON = Button(image=None, pos=(WINDOW_WIDTH // 2, 200),
                             text_input="PLAY", font=get_font(50), base_color="#d7fcd4", hovering_color="White")
       
        CARS_BUTTON = Button(image=None, pos=(WINDOW_WIDTH // 2, 280),
                             text_input="CARS", font=get_font(50), base_color="#d7fcd4", hovering_color="White")
       
        LEADER_BUTTON = Button(image=None, pos=(WINDOW_WIDTH // 2, 360),
                             text_input="LEADERBOARD", font=get_font(40), base_color="#d7fcd4", hovering_color="White")

        sound_text = "SOUND: ON" if GAME_DATA["sound"] else "SOUND: OFF"
        sound_color = "White" if GAME_DATA["sound"] else "Gray"
        SOUND_BUTTON = Button(image=None, pos=(WINDOW_WIDTH // 2, 440),
                             text_input=sound_text, font=get_font(40), base_color=sound_color, hovering_color="Green")

        QUIT_BUTTON = Button(image=None, pos=(WINDOW_WIDTH // 2, 520),
                             text_input="QUIT", font=get_font(50), base_color="#d7fcd4", hovering_color="White")

        RESET_BUTTON = Button(image=None, pos=(WINDOW_WIDTH // 2, 580),
                             text_input="RESET PROGRESS", font=get_font(30), base_color="Red", hovering_color="#ff5555")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, CARS_BUTTON, LEADER_BUTTON, SOUND_BUTTON, QUIT_BUTTON, RESET_BUTTON]:
            button.changeColor(MOUSE_POS)
            button.update(SCREEN)
       
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
           
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_l:
                    GAME_DATA["leaderboard"] = []
                    save_data(GAME_DATA)
                    print("Leaderboard reset!")

            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MOUSE_POS):
                    global FIGHT_USED
                    FIGHT_USED = False
                    play()
                if CARS_BUTTON.checkForInput(MOUSE_POS):
                    shop()
                if LEADER_BUTTON.checkForInput(MOUSE_POS):
                    leaderboard()
                if QUIT_BUTTON.checkForInput(MOUSE_POS):
                    pygame.quit()
                    sys.exit()
               
                if SOUND_BUTTON.checkForInput(MOUSE_POS):
                    if GAME_DATA["sound"]:
                        GAME_DATA["sound"] = False
                        pygame.mixer.music.pause()
                    else:
                        GAME_DATA["sound"] = True
                        pygame.mixer.music.unpause()
                        if not pygame.mixer.music.get_busy():
                             try: pygame.mixer.music.play(-1)
                             except: pass
                    save_data(GAME_DATA)

                if RESET_BUTTON.checkForInput(MOUSE_POS):
                    reset_progress()
                    GAME_DATA["username"] = ""
                    get_username()

        pygame.display.update()

if __name__ == "__main__":
    main_menu()
