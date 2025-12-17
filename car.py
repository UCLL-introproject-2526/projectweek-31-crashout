import pygame
import random
import sys
import json

# --- 1. CONFIGURATION & CONSTANTS ---
pygame.init()
pygame.mixer.init()

# Detect Screen Size
info = pygame.display.Info()
WINDOW_WIDTH  = info.current_w
WINDOW_HEIGHT = info.current_h

SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("CrashOut Racer")

# --- SPEED SETTINGS ---
scroll_speed = 7.0    
MAX_SPEED = 30.0      

# --- 2. ASSET LOADING ---

def get_font(size): 
    try:
        return pygame.font.Font("assets/font.ttf", size)
    except:
        return pygame.font.SysFont("Arial", size, bold=True)

try:
    BG = pygame.image.load("assets/Background.png").convert()
    BG = pygame.transform.scale(BG, (WINDOW_WIDTH, WINDOW_HEIGHT))
except:
    BG = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    BG.fill((30, 100, 30))

try:
    ROAD_IMG = pygame.image.load("assets/road_bg.png").convert()
    ROAD_IMG = pygame.transform.scale(ROAD_IMG, (WINDOW_WIDTH, WINDOW_HEIGHT))
    USE_CUSTOM_ROAD = True
except:
    USE_CUSTOM_ROAD = False

# --- 3. SAVE SYSTEM & DATA ---

CAR_SHOP = [
    {"id": 0, "name": "Classic", "price": 0,    "image": "assets/car.png"},
    {"id": 1, "name": "Blue",    "price": 500,  "image": "assets/car_blue.png"},
    {"id": 2, "name": "Taxi",    "price": 1000, "image": "assets/car_taxi.png"},
    {"id": 3, "name": "X-Mas Sled", "price": 0, "image": "assets/sled.png"}, 
]

default_data = {
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
    GAME_DATA = default_data.copy()
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

# DYNAMIC ROAD WIDTH
# We assume the road takes up about 75% of the screen width visually.
ROAD_WIDTH      = int(WINDOW_WIDTH * 0.75) 

# Adjust padding relative to screen size (approx 4% of road)
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

class PlayerCar(pygame.sprite.Sprite):
    def __init__(self, image_path):
        pygame.sprite.Sprite.__init__(self)
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
        self.rect.bottom = WINDOW_HEIGHT - 20
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 9 
        self.has_shield = False

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            self.image = pygame.transform.rotate(self.original_image, 5)
            self.mask = pygame.mask.from_surface(self.image) 
        elif keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            self.image = pygame.transform.rotate(self.original_image, -5)
            self.mask = pygame.mask.from_surface(self.image)
        else:
            self.image = self.original_image
            self.mask = pygame.mask.from_surface(self.image)

        if self.rect.left < ROAD_X + LANE_PADDING: 
            self.rect.left = ROAD_X + LANE_PADDING
        if self.rect.right > ROAD_X + ROAD_WIDTH - LANE_PADDING: 
            self.rect.right = ROAD_X + ROAD_WIDTH - LANE_PADDING

class EnemyCar(pygame.sprite.Sprite):
    def __init__(self, speed):
        pygame.sprite.Sprite.__init__(self)
        car_options = ["assets/coupe_green.png", "assets/coupe_red.png", "assets/coupe_midnight.png"]
        selected_car = random.choice(car_options)
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
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((300, 300), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=center)
        self.lifetime = 40 
        self.particles = []
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

def draw_background(surface, scroll_y):
    if USE_CUSTOM_ROAD:
        bg_height = ROAD_IMG.get_height()
        relative_y = scroll_y % bg_height
        surface.blit(ROAD_IMG, (0, relative_y - bg_height))
        if relative_y < WINDOW_HEIGHT:
            surface.blit(ROAD_IMG, (0, relative_y))
    else:
        surface.fill((30, 100, 30))
        pygame.draw.rect(surface, (50, 50, 50), (ROAD_X, 0, ROAD_WIDTH, WINDOW_HEIGHT))
        pygame.draw.line(surface, (255, 255, 255), (ROAD_X, 0), (ROAD_X, WINDOW_HEIGHT), 5)
        pygame.draw.line(surface, (255, 255, 255), (ROAD_X + ROAD_WIDTH, 0), (ROAD_X + ROAD_WIDTH, WINDOW_HEIGHT), 5)

# --- 6. GAME LOOPS (SHOP & PLAY) ---

def shop():
    pygame.mouse.set_visible(True) 
    while True:
        SCREEN.fill((0, 0, 0))
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
            
            if car_id == GAME_DATA["equipped"]:
                status_text = "EQUIPPED"
                color = (0, 255, 0)
            elif car_id in GAME_DATA["inventory"]:
                status_text = "SELECT"
                color = (255, 255, 255)
            else:
                status_text = f"BUY ({price})"
                color = (200, 0, 0)

            NAME_TXT = get_font(30).render(name, True, (255, 255, 255))
            SCREEN.blit(NAME_TXT, (200, y_pos))

            BTN = Button(image=None, pos=(600, y_pos + 15), 
                         text_input=status_text, font=get_font(30), base_color=color, hovering_color="Gray")
            BTN.changeColor(MOUSE_POS)
            BTN.update(SCREEN)
            buttons.append({"btn": BTN, "id": car_id, "price": price})
            y_pos += 100 

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

def play():
    pygame.mouse.set_visible(False) 
    clock = pygame.time.Clock()
    
    equipped_id = GAME_DATA["equipped"]
    car_info = next(item for item in CAR_SHOP if item["id"] == equipped_id)
    image_path = car_info["image"]
    
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    smoke_group = pygame.sprite.Group() 
    
    player = PlayerCar(image_path) 
    all_sprites.add(player)

    game_over = False
    crashed = False
    score = 0
    coins_collected = 0
    
    scroll_speed = 7.0    
    MAX_SPEED = 30.0      
    
    scroll_offset = 0
    enemy_timer = 0
    coin_timer = 0
    powerup_timer = 0 
    spawn_rate = 60
    smoke_timer = 0
    unlock_message_timer = 0

    # --- COUNTDOWN VARIABLES ---
    countdown = True
    countdown_start_time = pygame.time.get_ticks()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GAME_DATA["coins"] += coins_collected
                save_data(GAME_DATA)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    GAME_DATA["coins"] += coins_collected
                    save_data(GAME_DATA)
                    main_menu()
                if event.key == pygame.K_r and game_over:
                    GAME_DATA["coins"] += coins_collected
                    save_data(GAME_DATA)
                    play() 

        if not game_over:
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
                score += 1
                
                if score >= 5000 and 3 not in GAME_DATA["inventory"]:
                    GAME_DATA["inventory"].append(3)
                    save_data(GAME_DATA)
                    unlock_message_timer = 180 

                target_spawn_rate = 70 - (scroll_speed * 1.8)
                spawn_rate = max(15, int(target_spawn_rate))

                # Make steering speed proportional to screen width 
                # (so it feels the same on 4k as on 800x600)
                player.speed = int(WINDOW_WIDTH * 0.01) + int(scroll_speed * 0.4)

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

                    if random.random() < 0.2:
                        lane = random.choice(LANE_COORDS)
                        fast_speed = final_traffic_speed + 5
                        warning = WarningSign(lane, fast_speed, enemies, all_sprites)
                        all_sprites.add(warning)
                    else:
                        speed = final_traffic_speed + random.randint(0, 3)
                        enemy = EnemyCar(speed)
                        if not pygame.sprite.spritecollideany(enemy, enemies):
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
                if powerup_timer >= 1500:
                    powerup_timer = 0
                    shield_orb = ShieldItem(scroll_speed)
                    if not pygame.sprite.spritecollideany(shield_orb, enemies):
                        powerups.add(shield_orb)
                        all_sprites.add(shield_orb)
                    else:
                        shield_orb.kill()

                player.update()
                enemies.update()
                coins.update()
                powerups.update() 
                smoke_group.update()
                all_sprites.update()

                hits = pygame.sprite.spritecollide(player, coins, True, pygame.sprite.collide_mask)
                for hit in hits:
                    coins_collected += 1
                    score += 100 
                    if scroll_speed < MAX_SPEED:
                        scroll_speed += 0.2

                shield_hits = pygame.sprite.spritecollide(player, powerups, True, pygame.sprite.collide_mask)
                for hit in shield_hits:
                    player.has_shield = True 

                enemy_hits = pygame.sprite.spritecollide(player, enemies, False, pygame.sprite.collide_mask)
                if enemy_hits:
                    if player.has_shield:
                        player.has_shield = False 
                        for enemy in enemy_hits:
                            boom = Explosion(enemy.rect.center)
                            all_sprites.add(boom)
                            enemy.kill()
                    else:
                        crashed = True
                        boom = Explosion(player.rect.center)
                        all_sprites.add(boom)
                        player.kill()
                        smoke_group.empty() 

        # --- DRAWING ---
        draw_background(SCREEN, scroll_offset)
        smoke_group.draw(SCREEN)
        all_sprites.draw(SCREEN)

        if not crashed and not game_over and player.has_shield:
            pygame.draw.circle(SCREEN, (0, 200, 255), player.rect.center, 50, 4)
        
        score_text = get_font(30).render(f"SCORE: {score}", True, (255, 255, 255))
        coin_text = get_font(30).render(f"COINS: {coins_collected}", True, (255, 215, 0))
        SCREEN.blit(score_text, (20, 20))
        SCREEN.blit(coin_text, (20, 60))

        if countdown:
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

        if unlock_message_timer > 0:
            unlock_message_timer -= 1
            if (unlock_message_timer // 10) % 2 == 0:
                msg = get_font(40).render("SECRET UNLOCKED: X-MAS SLED!", True, (0, 255, 0))
                rect = msg.get_rect(center=(WINDOW_WIDTH//2, 150))
                pygame.draw.rect(SCREEN, (0,0,0), rect.inflate(20, 10))
                SCREEN.blit(msg, rect)

        if game_over:
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

# --- 7. MAIN MENU ---

def main_menu():
    pygame.mouse.set_visible(True) 
    while True:
        SCREEN.blit(BG, (0, 0))
        MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(60).render("CrashOut Racer", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(WINDOW_WIDTH // 2, 80))

        PLAY_BUTTON = Button(image=None, pos=(WINDOW_WIDTH // 2, 200), 
                            text_input="PLAY", font=get_font(50), base_color="#d7fcd4", hovering_color="White")
        
        CARS_BUTTON = Button(image=None, pos=(WINDOW_WIDTH // 2, 280), 
                            text_input="CARS", font=get_font(50), base_color="#d7fcd4", hovering_color="White")
        
        sound_text = "SOUND: ON" if GAME_DATA["sound"] else "SOUND: OFF"
        sound_color = "White" if GAME_DATA["sound"] else "Gray"
        SOUND_BUTTON = Button(image=None, pos=(WINDOW_WIDTH // 2, 360), 
                            text_input=sound_text, font=get_font(40), base_color=sound_color, hovering_color="Green")

        QUIT_BUTTON = Button(image=None, pos=(WINDOW_WIDTH // 2, 440), 
                            text_input="QUIT", font=get_font(50), base_color="#d7fcd4", hovering_color="White")

        RESET_BUTTON = Button(image=None, pos=(WINDOW_WIDTH // 2, 530), 
                            text_input="RESET PROGRESS", font=get_font(30), base_color="Red", hovering_color="#ff5555")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, CARS_BUTTON, SOUND_BUTTON, QUIT_BUTTON, RESET_BUTTON]:
            button.changeColor(MOUSE_POS)
            button.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MOUSE_POS):
                    play() 
                if CARS_BUTTON.checkForInput(MOUSE_POS):
                    shop() 
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

        pygame.display.update()

if __name__ == "__main__":
    main_menu()