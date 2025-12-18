# fight.py
import pygame
from fighter1 import Fighter

def main():
    pygame.init()
    SCREEN_WIDTH, SCREEN_HEIGHT = 1920, 1080
    screen = pygame.display.get_surface()
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

    clock = pygame.time.Clock()
    FPS = 60

    YELLOW = (255, 255, 0)
    RED    = (255, 0, 0)
    WHITE  = (255, 255, 255)

    intro_count = 3
    last_count_update = pygame.time.get_ticks()
    score = [0, 0]
    round_over = False
    round_over_time = 0
    ROUND_OVER_COOLDOWN = 2000

    bg_image = pygame.image.load("images/background/forest.jpg").convert_alpha()
    Drifter_sheet = pygame.image.load("images/characters/Drifter/full2.png").convert_alpha()
    Biker_sheet   = pygame.image.load("images/characters/Biker/untitled.png").convert_alpha()
    victory_img   = pygame.image.load("images/victory/victory.png").convert_alpha()
    victory_img   = pygame.transform.scale(victory_img, (1000, 200))

    DRIFTER_DATA = [128, 5, [45, 56]]
    BIKER_DATA   = [128, 5, [43, 56]]
    DRIFTER_ANIMATION_STEPS = [11, 8, 16, 5, 3, 3, 4]
    BIKER_ANIMATION_STEPS   = [7, 10, 10, 6, 6, 4, 5]

    count_font = pygame.font.Font("images/font/Turok.ttf", 80)
    score_font = pygame.font.Font("images/font/Turok.ttf", 30)
    
    def draw_text(text, font, col, x, y):
        img = font.render(text, True, col)
        screen.blit(img, (x, y))

    def draw_bg():
        scaled_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled_bg, (0, 0))

    def draw_health_bar(health, x, y):
        ratio = health / 100
        pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 604, 44))
        pygame.draw.rect(screen, (255, 0, 0), (x, y, 600, 40))
        pygame.draw.rect(screen, YELLOW, (x, y, 600 * ratio, 40))

    fighter_1 = Fighter(1, int(SCREEN_WIDTH * 0.25), int(SCREEN_HEIGHT * 0.7),
                    False, DRIFTER_DATA, Drifter_sheet, DRIFTER_ANIMATION_STEPS, is_cpu=False)
    fighter_2 = Fighter(2, int(SCREEN_WIDTH * 0.75), int(SCREEN_HEIGHT * 0.7),
                    True,  BIKER_DATA,   Biker_sheet,   BIKER_ANIMATION_STEPS,   is_cpu=True)


    winner_is_p1 = False
    running = True

    while running:
        clock.tick(FPS)
        draw_bg()
        draw_health_bar(fighter_1.health, int(SCREEN_WIDTH * 0.05), int(SCREEN_HEIGHT * 0.05))
        draw_health_bar(fighter_2.health, int(SCREEN_WIDTH * 0.55), int(SCREEN_HEIGHT * 0.05))

        draw_text("P1: " + str(score[0]), score_font, RED,
          int(SCREEN_WIDTH * 0.35), int(SCREEN_HEIGHT * 0.08))
        draw_text("AI: " + str(score[1]), score_font, RED,
          int(SCREEN_WIDTH * 0.75), int(SCREEN_HEIGHT * 0.08))


        if intro_count <= 0:
            fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_2, round_over)
            fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_1, round_over)
        else:
            img = count_font.render(str(intro_count), True, RED)
            screen.blit(img, (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3))
            if pygame.time.get_ticks() - last_count_update >= 1000:
                intro_count -= 1
                last_count_update = pygame.time.get_ticks()

        fighter_1.update()
        fighter_2.update()
        fighter_1.draw(screen)
        fighter_2.draw(screen)

        if not round_over:
            if not fighter_1.alive:
                winner_is_p1 = False
                round_over = True
                round_over_time = pygame.time.get_ticks()
                winner_is_p1 = False
            elif not fighter_2.alive:
                winner_is_p1 = True
                round_over = True
                round_over_time = pygame.time.get_ticks()
                
        else:
            victory_rect = victory_img.get_rect(center=(SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * 0.25)))
            screen.blit(victory_img, victory_rect)

            if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
                running = False  # stop de fight-loop

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                winner_is_p1 = False

        pygame.display.update()

    
    return winner_is_p1  # True = P1 wint, False = verlies

if __name__ == "__main__":
    main()
