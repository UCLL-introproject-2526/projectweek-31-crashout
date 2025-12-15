import random
import time

class Fighter:
    def __init__(self, name, health=100, attack=10, defense=5, is_player=False):
        self.name = name
        self.health = health
        self.attack = attack
        self.defense = defense
        self.is_player = is_player

    def is_alive(self):
        return self.health > 0

    def take_damage(self, damage):
        reduced = max(0, damage - self.defense)
        self.health -= reduced
        return reduced

    def choose_action(self):
        if self.is_player:
            print("Choose action: [1] Attack  [2] Defend  [3] Special")
            choice = input("> ")
            return {"1": "attack", "2": "defend", "3": "special"}.get(choice, "attack")
        else:
            return random.choice(["attack", "defend", "special"])

    def special_attack(self):
        return self.attack + random.randint(5, 15)


def fight(ai, player):
    round_num = 1
    while ai.is_alive() and player.is_alive():
        print(f"\n--- Round {round_num} ---")

        # Player turn
        action = player.choose_action()
        if action == "attack":
            damage = player.attack + random.randint(0, 5)
            taken = ai.take_damage(damage)
            print(f"You attack {ai.name} for {taken} damage")
        elif action == "special":
            damage = player.special_attack()
            taken = ai.take_damage(damage)
            print(f"You use SPECIAL on {ai.name} for {taken} damage")
        elif action == "defend":
            player.defense += 2
            print("You defend and increase defense")

        if not ai.is_alive():
            break

        time.sleep(0.5)

        # AI turn
        action = ai.choose_action()
        if action == "attack":
            damage = ai.attack + random.randint(0, 5)
            taken = player.take_damage(damage)
            print(f"{ai.name} attacks you for {taken} damage")
        elif action == "special":
            damage = ai.special_attack()
            taken = player.take_damage(damage)
            print(f"{ai.name} uses SPECIAL on you for {taken} damage")
        elif action == "defend":
            ai.defense += 2
            print(f"{ai.name} defends and increases defense")

        print(f"Status: You HP={player.health} | {ai.name} HP={ai.health}")
        round_num += 1

    winner = player if player.is_alive() else ai
    print(f"\n🏆 {winner.name} wins the fight!")


if __name__ == "__main__":
    ai_fighter = Fighter("AI Alpha", attack=12, defense=4)
    player = Fighter("Player", attack=11, defense=5, is_player=True)

    fight(ai_fighter, player)
