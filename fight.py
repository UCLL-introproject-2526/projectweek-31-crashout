# fight.py
import pygame
from pygame import mixer
from fighter1 import Fighter
from hitspark import HitSpark
from button import Button
def draw_text(text, font, col, y, screen):
    img = font.render(text, True, col)
    x = (screen.get_width() // 2) - (img.get_width() // 2)
    screen.blit(img, (x, y))
def fight_menu(screen, bg_image, biome_name):
    """The screen that shows up before the fight starts with a tutorial"""
    menu_font = pygame.font.Font("images/font/Turok.ttf", 80)
    sub_font = pygame.font.Font("images/font/Turok.ttf", 40)
    key_font = pygame.font.Font("images/font/Turok.ttf", 30)
    
    waiting = True
    while waiting:
        # 1. Draw and scale background
        screen.blit(pygame.transform.scale(bg_image, screen.get_size()), (0, 0))
        
        # 2. Dark overlay for readability
        overlay = pygame.Surface(screen.get_size())
        overlay.fill((0, 0, 0))
        overlay.set_alpha(180) # Slightly darker to see tutorial
        screen.blit(overlay, (0, 0))

        # 3. Main Titles
        draw_text("GET READY!", menu_font, (255, 0, 0), 100, screen)
        draw_text(f"LOCATION: {biome_name.upper()}", sub_font, (255, 255, 255), 190, screen)

        # 4. KEYBINDS BOX (Tutorial)
        box_x = screen.get_width()//2 - 200
        box_y = 300
        draw_text("--- CONTROLS ---", sub_font, (255, 215, 0), 320, screen)
        draw_text("ARROWS  -  Move & Jump", key_font, (255, 255, 255), 380, screen)
        draw_text("O KEY   -  Attack 1", key_font, (255, 255, 255), 420, screen)
        draw_text("P KEY   -  Attack 2", key_font, (255, 255, 255), 460, screen)
        draw_text("ESCAPE  -  Menu", key_font, (200, 200, 200), 520, screen)

        # 5. Start Prompt
        draw_text("Press SPACE to Start", sub_font, (0, 255, 0), 620, screen)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False

def main(enemy_type="Knight", biome = "suburbs"):
    
    mixer.init()
    pygame.init()
    screen = pygame.display.get_surface()
    if screen is None:
        screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    if enemy_type == "Knight":
        enemy_sheet = pygame.image.load("images/characters/Knight/untitled.png").convert_alpha()
        enemy_data = [96, 7, [43, 44.5]] # BIKER_DATA
        enemy_steps = [7, 8, 5, 5, 6, 4, 12]
        enemy_name = "Knight"
    elif enemy_type == "Peasant":
        enemy_sheet = pygame.image.load("images/characters/Peasant/peasant.png").convert_alpha()
        enemy_data = [150, 7, [63, 99]] # BIKER_DATA
        enemy_steps = [8, 8, 2, 4, 4, 4, 6]
        enemy_name = "Peasant"
        
    else:
        # Fallback to Biker if something goes wrong
        enemy_sheet = pygame.image.load("images/characters/Gangster/untitled.png").convert_alpha()
        enemy_data = [128, 5, [43, 56]]
        enemy_steps = [7, 10, 10, 6, 6, 4, 5]
        enemy_name = "Gangster"
   
    

    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

    clock = pygame.time.Clock()
    FPS = 60

    YELLOW = (255, 255, 0)
    RED    = (255, 0, 0)
    WHITE  = (255, 255, 255)
    BLACK = (0,0,0)


    BIOME_BACKGROUNDS = {
        "city": "images/background/drerrie.png",
        "forest": "images/background/bos.png",
        "snow": "images/background/snow.jpg",
        "desert": "images/background/desertt.jpg",
        "suburbs": "images/background/suburb.png"
    }
    bg_path = BIOME_BACKGROUNDS.get(biome, "images/background/suburb.png")
    try:
        bg_image = pygame.image.load(bg_path).convert_alpha()
    except:
        bg_image = pygame.image.load("images/background/suburb.png").convert_alpha()
    intro_count = 3
    last_count_update = pygame.time.get_ticks()
    round_over = False
    ROUND_OVER_COOLDOWN = 2000
    sparks = []
    fight_menu(screen, bg_image, biome)

    DRIFTER_DATA = [128, 5, [45, 56]]
    DRIFTER_ANIMATION_STEPS = [11, 8, 16, 5, 3, 3, 4]

    # Assets
    pygame.mixer.music.load("images/audio/music5.mp3")
    pygame.mixer.music.set_volume(0.7)
    pygame.mixer.music.play(-1, 0.0, 2000)
    
    Drifter_sheet = pygame.image.load("images/characters/Jeffrey/full2.png").convert_alpha()
    Biker_sheet = pygame.image.load("images/characters/Gangster/untitled.png").convert_alpha()
    # Load defeat image (replace with your file name)
    defeat_font = pygame.font.Font("images/font/Turok.ttf", int(SCREEN_WIDTH * 0.1))
    count_font = pygame.font.Font("images/font/Turok.ttf", int(SCREEN_WIDTH * 0.10))
    score_font = pygame.font.Font("images/font/Turok.ttf", int(SCREEN_WIDTH * 0.025))
    death_fx = pygame.mixer.Sound("images/fx/death.wav")
    death_fx.set_volume(0.9)
    hit_fx = pygame.mixer.Sound("images/fx/hit.aiff")
    hit_fx.set_volume(2)



    def draw_bg():
        scaled_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled_bg, (0, 0))

    def draw_health_bar(health, x, y):
        bar_width = SCREEN_WIDTH * 0.4
        ratio = health / 100
        pygame.draw.rect(screen, WHITE, (x - 2, y - 2, bar_width + 4, 44))
        pygame.draw.rect(screen, (255, 0, 0), (x,y,bar_width, 40))
        pygame.draw.rect(screen, YELLOW, (x, y, bar_width * ratio, 40))

    fighter_1 = Fighter(1, int(SCREEN_WIDTH * 0.13), int(SCREEN_HEIGHT * 0.88),
                    False, DRIFTER_DATA, Drifter_sheet, DRIFTER_ANIMATION_STEPS, is_cpu=False)
    fighter_2 = Fighter(2, int(SCREEN_WIDTH * 0.75), int(SCREEN_HEIGHT * 0.88),
                    True, enemy_data, enemy_sheet, enemy_steps,  is_cpu=True)


    winner_is_p1 = False
    running = True
    paused = False

    pygame.mouse.set_visible(False)

    while running:
        clock.tick(FPS)
        MOUSE_POS = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused # Toggle pause
                    pygame.mouse.set_visible(paused)

            if paused and event.type == pygame.MOUSEBUTTONDOWN:
                if RESUME_BTN.checkForInput(MOUSE_POS):
                    paused = False
                    pygame.mouse.set_visible(False)
                if QUIT_BTN.checkForInput(MOUSE_POS):
                    pygame.mixer.music.stop()
                    return False
        draw_bg()
        draw_health_bar(fighter_1.health, int(SCREEN_WIDTH * 0.05), int(SCREEN_HEIGHT * 0.05))
        draw_health_bar(fighter_2.health, int(SCREEN_WIDTH * 0.55), int(SCREEN_HEIGHT * 0.05))
        
        fighter_1.draw(screen)
        fighter_2.draw(screen)
        pygame.draw.rect(screen, (0, 255, 0), fighter_1.rect, 2) # Green box for Jeffrey
        pygame.draw.rect(screen, (0, 255, 0), fighter_2.rect, 2)

        for spark in sparks:
            spark.draw(screen)        
        if not paused:              
            draw_bg()

            # Update and check for hits to spawn VFX
            if fighter_1.update(fighter_2):
                sparks.append(HitSpark(fighter_2.rect.centerx, fighter_2.rect.centery, fighter_1.flip))
                if fighter_2.alive:
                    hit_fx.play()
            if fighter_2.update(fighter_1):
                sparks.append(HitSpark(fighter_1.rect.centerx, fighter_1.rect.centery, fighter_2.flip))
                if fighter_1.alive:
                    hit_fx.play()

            fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_2, round_over, intro_count)
            fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_1, round_over, intro_count)

            draw_health_bar(fighter_1.health, int(SCREEN_WIDTH * 0.05), int(SCREEN_HEIGHT * 0.05))
            draw_health_bar(fighter_2.health, int(SCREEN_WIDTH * 0.55), int(SCREEN_HEIGHT * 0.05))

            fighter_1.draw(screen)
            fighter_2.draw(screen)

            jeff_img = score_font.render("Jeffrey", True, RED)
            screen.blit(jeff_img, (int(SCREEN_WIDTH * 0.05), int(SCREEN_HEIGHT * 0.0085)))
            gang_img = score_font.render(enemy_name, True, RED)
            screen.blit(gang_img, (int(SCREEN_WIDTH * 0.86), int(SCREEN_HEIGHT * 0.0085)))
            
            for spark in sparks[:]:
                spark.draw(screen)
                if not spark.alive:
                    sparks.remove(spark)

            if intro_count > 0:
                draw_text(str(intro_count), count_font, RED, SCREEN_HEIGHT / 3, screen)
                if pygame.time.get_ticks() - last_count_update >= 1000:
                    intro_count -= 1
                    last_count_update = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - last_count_update < 1000:
                draw_text("FIGHT!", count_font, RED, SCREEN_HEIGHT / 3, screen)

            

            if not round_over:
                if not fighter_1.alive or not fighter_2.alive:
                    death_fx.play()
                    if not fighter_2.alive:
                        winner_is_p1 = True  # Jeffrey wins
                    else:
                        winner_is_p1 = False
                        
                    round_over = True
                    round_over_time = pygame.time.get_ticks()
                    
            else:
                msg = "VICTORY" if winner_is_p1 == 1 else "DEFEAT"
                msg_img = defeat_font.render(msg, True, RED)
                screen.blit(msg_img, (SCREEN_WIDTH/2 - msg_img.get_width()/2, SCREEN_HEIGHT/3)) 
                    
                if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
                    pygame.mixer.music.stop()
                    running = False
        
        else:
            overlay = pygame.Surface(screen.get_size())
            overlay.fill((0, 0, 0))
            overlay.set_alpha(150)
            screen.blit(overlay, (0, 0))

            draw_text("PAUSED", count_font, YELLOW, SCREEN_HEIGHT // 4, screen)

            # Create the buttons using the class from button.py
            RESUME_BTN = Button(image=None, pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), 
                                text_input="RESUME", font=score_font, base_color="White", hovering_color="Green")
            
            QUIT_BTN = Button(image=None, pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100), 
                                text_input="MAIN MENU", font=score_font, base_color="White", hovering_color="Red")
            for btn in [RESUME_BTN, QUIT_BTN]:
                btn.changeColor(MOUSE_POS)
                btn.update(screen)

        pygame.display.update()

        
    return winner_is_p1

if __name__ == "__main__":
        main()
