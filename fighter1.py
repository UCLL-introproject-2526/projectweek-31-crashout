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
        self.rect= pygame.Rect((x,y, 160, 360))
        self.vel_y = 0
        self.running = False
        self.jump = False
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown  = 0
        self.hit = False
        self.hit_registered = False
        self.health = 100
        self.alive = True
    
    def load_images(self, sprite_sheet, animation_steps):
        animation_list = []
        for y, animation in enumerate(animation_steps):
            temp_img_list = []
            for x in range(animation):
                print(f"DEBUG: Row {y}, Frame {x} | Size: {self.size} | Sheet: {sprite_sheet}")
                temp_img = sprite_sheet.subsurface(x * self.size, y * self.size, self.size, self.size).convert_alpha()
                temp_img_list.append(pygame.transform.scale(temp_img,(self.size * self.image_scale, self.size * self.image_scale)))
            animation_list.append(temp_img_list)
        return animation_list    

    def move(self, screen_width, screen_height,surface, target, round_over, intro_count):
        SPEED = screen_width * 0.008
        GRAVITY = screen_height * 0.0018
        dx = 0
        dy = 0
        self.running = False
        floor_margin = screen_height * 0.12
        
        key = pygame.key.get_pressed()

        if self.attacking == False and self.alive == True and round_over == False and intro_count <= 0:
            if not self.is_cpu:
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
                    if (key[pygame.K_o] or key[pygame.K_p]) and self.attack_cooldown == 0:
                        self.attack(target)
                        if key[pygame.K_o]: self.attack_type = 1
                        if key[pygame.K_p]: self.attack_type = 2
            else:
                dist_x = target.rect.centerx - self.rect.centerx
                dist_y = target.rect.centery - self.rect.centery

                if abs(dist_x) < 150:
                    if self.attack_cooldown == 0:
                        self.attack_type = random.choice([1, 2])
                        self.attack(target)
                        self.attack_cooldown = 60
                
                elif abs(dist_x) > 150:
                    if dist_x > 0:
                        dx = SPEED
                    else:
                        dx = -SPEED
                    self.running = True

                if target.attacking and abs(dist_x) < 250:
                    if not self.jump and random.random() < 0.05:
                        self.vel_y = -30
                        self.jump = True

                if not self.jump and random.random() < 0.005:
                    self.vel_y = -30
                    self.jump = True




            
        self.vel_y += GRAVITY
        dy += self.vel_y
        
        if self.rect.left + dx < 0: dx = -self.rect.left
        if self.rect.right + dx > screen_width: dx = screen_width - self.rect.right
        if self.rect.bottom + dy > screen_height - floor_margin:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - floor_margin - self.rect.bottom

        if self.attacking == False:    
            self.flip = target.rect.centerx < self.rect.centerx
        
        self.rect.x += dx 
        self.rect.y += dy 

    def attack(self, target):
        self.attacking = True
        self.hit_registered = False # Reset hit for the new swing
        self.attack_cooldown = 20

   
    def update(self, target):
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
        animation_cooldown = 80
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        # HITBOX LOGIC
        landed_hit = False
        if self.attacking and not self.hit_registered:
            # Active frames (usually middle of the swing)
            if 3 <= self.frame_index <= 5:
                reach = 140
                hitbox_x = (self.rect.centerx - reach) if self.flip else self.rect.centerx
                attacking_rect = pygame.Rect(hitbox_x, self.rect.y + 100, reach, 150)
                
                if attacking_rect.colliderect(target.rect):
                    target.health -= 10
                    target.hit = True
                    self.hit_registered = True
                    landed_hit = True




        #check if animation has finished
        if self.frame_index >= len(self.animation_list[self.action]):
            #if player is dead end ani
            if self.alive == False:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
                if self.action in [3, 4, 5]:
                    self.attacking = False
                    self.hit = False
                    self.flip = target.rect.centerx < self.rect.centerx
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
        return landed_hit


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