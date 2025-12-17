import pygame
import random
class Fighter():
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, is_cpu=False):
        self.player = player
        self.is_cpu = is_cpu
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.flip = flip
        self.animation_list = self.load_images(sprite_sheet, animation_steps)
        self.action = 0 #1walk 2punch 3die
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect= pygame.Rect((x,y, 200, 360))
        self.vel_y = 0
        self.running = False
        self.jump = False
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown  = 0
        self.hit = False
        self.health = 100
        self.alive = True
    
    def load_images(self, sprite_sheet, animation_steps):
        #characters van spritesheet halen
        animation_list = []

        for y, animation in enumerate(animation_steps):
            temp_img_list = []
            for x in range(animation):
                temp_img = sprite_sheet.subsurface(x * self.size, y * self.size, self.size, self.size).convert_alpha()
                temp_img_list.append(pygame.transform.scale(temp_img,(self.size * self.image_scale, self.size * self.image_scale)))
            animation_list.append(temp_img_list)
        return animation_list    

    def move(self, screen_width, screen_height, surface, target, round_over):
        SPEED = 10
        GRAVITY = 2
        dx = 0
        dy = 0
        self.running = False
        self.attack_type = 0
        
        key = pygame.key.get_pressed()

        #alleen wanneer niet attacking
        if self.attacking == False and self.alive == True and round_over == False:

            if not self.is_cpu:
                #check player 1 controls
                if self.player == 1:
                    #left,right
                    if key[pygame.K_LEFT]:
                        dx = -SPEED
                        self.running = True
                    if key[pygame.K_RIGHT]:
                        dx = +SPEED
                        self.running = True
                    #jump
                    if key[pygame.K_UP] and self.jump == False:
                        self.vel_y = -30
                        self.jump = True
                    #attack
                    if key[pygame.K_o] or key[pygame.K_p]:
                        self.attack(target)
                        #welk attack type
                        if key[pygame.K_o]:
                            self.attack_type = 1
                        if key[pygame.K_p]:
                            self.attack_type = 2
            else:
                # --- VERBETERDE AI LOGICA ---
                dist_x = target.rect.centerx - self.rect.centerx
                dist_y = target.rect.centery - self.rect.centery

                # 1. AFSTAND BEPALEN (AI gedrag baseren op afstand)
                # Dichtbij: Aanvallen
                if abs(dist_x) < 250:
                    if self.attack_cooldown == 0:
                        # Kies willekeurig tussen aanval 1 of 2
                        self.attack_type = random.choice([1, 2])
                        self.attack(target)
                # Middelmatig: Naar de speler toe lopen
                elif abs(dist_x) > 200:
                    if dist_x > 0:
                        dx = SPEED
                    else:
                        dx = -SPEED
                    self.running = True

                # 2. DEFENSIEF GEDRAG (Springen of ontwijken)
                # Als de speler aanvalt en de AI is dichtbij, kleine kans om te springen
                if target.attacking and abs(dist_x) < 150:
                    if not self.jump and random.random() < 0.05:
                        self.vel_y = -30
                        self.jump = True

                # 3. RANDOM JUMP (Om het minder voorspelbaar te maken)
                if not self.jump and random.random() < 0.005:
                    self.vel_y = -30
                    self.jump = True




            
        self.vel_y += GRAVITY
        dy += self.vel_y
        
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
        if self.rect.bottom + dy > screen_height - 270:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 270 - self.rect.bottom
        if self.attacking == False:    
            #ensure players face eachother
            if target.rect.centerx > self.rect.centerx:
                self.flip = False
            else: 
                self.flip = True
        #apply cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        self.rect.x += dx 
        self.rect.y += dy 
    #animatie updates
    def update(self):
        #check what action is happening
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(6)#death
        elif self.hit == True:
            self.update_action(5)#hit
        elif self.attacking == True:
            if self.attack_type == 1:
                self.update_action(3)#atk1
            elif self.attack_type == 2:
                self.update_action(4)#atk2
        elif self.jump == True:
            self.update_action(2)#jump
        elif self.running == True:
            self.update_action(1)#run
        else:
            self.update_action(0)#idle
        animation_cooldown = 50
        #update image
        self.image = self.animation_list[self.action][self.frame_index]
        #check if enough time has passes since update
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        #check if animation has finished
        if self.frame_index >= len(self.animation_list[self.action]):
            #if player is dead end ani
            if self.alive == False:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
                #check if attack has happened
                if self.action == 3 or self.action == 4:
                    self.attacking = False
                    self.attack_cooldown = 20
                if self.action == 5:
                    self.hit = False
                    self.attacking = False
                    self.attack_cooldown = 20


    def attack(self, target):
        if not self.alive or not target.alive:
            return
        if self.attack_cooldown == 0:
            self.attacking = True
            attacking_rect = pygame.Rect(self.rect.centerx - (self.rect.width * self.flip), self.rect.y +self.rect.height * 0.25, self.rect.width, self.rect.height * 0.5)
            if attacking_rect.colliderect(target.rect,):
                target.health -= 10
                target.hit = True

    def update_action(self, new_action):
        #check if the new action is different
        if new_action != self.action:
            self.action = new_action
            #update animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img,(self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))