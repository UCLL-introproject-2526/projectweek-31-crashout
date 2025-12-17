import pygame
import random

pygame.init()

# Window setup
WIDTH, HEIGHT = 800, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AI Fighter")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 32)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
BLUE = (50, 50, 200)

class Fighter:
    def __init__(self, name, x, color, health=100, attack=10, defense=5, is_player=False):
        self.name = name
        self.health = health
        self.attack = attack
        self.defense = defense
        self.is_player = is_player
        self.rect = pygame.Rect(x, 200, 80, 80)
        self.color = color

    def is_alive(self):
        return self.health > 0

    def take_damage(self, damage):
        reduced = max(0, damage - self.defense)
        self.health -= reduced
        return reduced

    def special_attack(self):
        return self.attack + random.randint(5, 15)

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        hp_text = font.render(f"HP: {self.health}", True, WHITE)
        screen.blit(hp_text, (self.rect.x, self.rect.y - 25))


def draw_text(text, y):
    render = font.render(text, True, WHITE)
    screen.blit(render, (WIDTH // 2 - render.get_width() // 2, y))


def main():
    player = Fighter("Player", 150, BLUE, attack=11, defense=5, is_player=True)
    ai = Fighter("AI Alpha", 570, RED, attack=12, defense=4)

    turn = "player"
    info_text = "Press A=Attack  S=Special  D=Defend"
    running = True

    while running:
        clock.tick(60)
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if turn == "player" and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    dmg = player.attack + random.randint(0, 5)
                    ai.take_damage(dmg)
                    info_text = f"You attack for {dmg}"
                    turn = "ai"
                elif event.key == pygame.K_s:
                    dmg = player.special_attack()
                    ai.take_damage(dmg)
                    info_text = f"You use SPECIAL for {dmg}"
                    turn = "ai"
                elif event.key == pygame.K_d:
                    player.defense += 2
                    info_text = "You defend"
                    turn = "ai"

        if turn == "ai" and ai.is_alive():
            pygame.time.delay(500)
            action = random.choice(["attack", "special", "defend"])
            if action == "attack":
                dmg = ai.attack + random.randint(0, 5)
                player.take_damage(dmg)
                info_text = f"AI attacks for {dmg}"
            elif action == "special":
                dmg = ai.special_attack()
                player.take_damage(dmg)
                info_text = f"AI uses SPECIAL for {dmg}"
            else:
                ai.defense += 2
                info_text = "AI defends"
            turn = "player"

        player.draw()
        ai.draw()
        draw_text(info_text, 20)

        if not player.is_alive() or not ai.is_alive():
            winner = "Player" if player.is_alive() else "AI"
            draw_text(f"{winner} wins!", HEIGHT // 2)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
