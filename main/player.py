import pygame
from support import import_folder
import time

player_speed = 6

class Player(pygame.sprite.Sprite):
    def __init__(self,pos,surface,create_jump_particle,create_fall_jump_particle,):  # level 에서 함수가져오기
        super().__init__()
        self.import_character_assets()
        self.frame_index = 0
        self.anim_speed = 0.075      # anim 속도

        self.image = self.animations['idle'][self.frame_index]
        self.rect = self.image.get_rect(topleft = pos)

        #sound
        self.jump_sound_1 = pygame.mixer.Sound('.\\sound\\jump\\jump_1.wav')
        self.jump_sound_1.set_volume(0.25)
        self.jump_sound_2 = pygame.mixer.Sound('.\\sound\\jump\\jump_2.wav')
        self.jump_sound_2.set_volume(0.25)
        self.super_jump_sound = pygame.mixer.Sound('.\\sound\\jump\\super_jump.wav')
        self.super_jump_sound.set_volume(0.5)

        # dust particles
        self.import_dust_run_particles()
        self.dust_frame_index = 0
        self.dust_anim_speed = 0.23
        self.display_surface = surface
        self.create_jump_particle = create_jump_particle
        self.create_fall_jump_particle = create_fall_jump_particle


        # player movement
        self.direction = pygame.math.Vector2(0,0)     # 2차원 벡터 (x,y) 방향의 벡터를 반환

        self.gravity = 0.8
        self.max_gravity = 22
        self.jump_speed = -16

        # player status
        self.status = 'idle'
        self.facing_right = True
        self.can_jump = True
        self.on_ground = False
        self.can_double_jump = False
        self.can_super_jump = True
        self.is_attack = False
        self.can_move = True

        self.on_right = False
        self.on_left = False

        # game status
        self.jump_count = 100
        self.is_restart = False        
        self.is_credit = False

    # character 에셋 가져오기
    def import_character_assets(self): 
        character_path = './graphics/character/'                          # 에셋들의 경로
        self.animations = {'idle' : [], 'run' : [], 'jump' : [], 'fall' : [], 'dash' : [], 'attack' : []}

        for anim in self.animations.keys():
            full_path = character_path + anim
            self.animations[anim] = import_folder(full_path)        # 딕셔너리의 빈리스트에 png들을 채우기
    
    def import_dust_run_particles(self):
        self.dust_run_particles = import_folder('.\\graphics\\character\\particles\\run')
        
    # 애니메이션 
    def animate(self):
        if self.is_attack == False:
            animation = self.animations[self.status]  # animation은 리스트
            self.anim_speed = 0.075
        else:
            animation = self.animations['attack']   # 공격할떄 에님 불러오기 
            self.anim_speed = 0.225
        
        # frame_index looping
        self.frame_index += self.anim_speed

        # attack anim loop 
        if self.frame_index > len(self.animations['attack']):
            self.is_attack = False
            self.can_move = True

        if self.frame_index > len(animation):
            self.frame_index = 0
        
        image = animation[int(self.frame_index)]

        if self.facing_right == True:
            self.image = image
        else:
            flipped_image = pygame.transform.flip(image, True, False)        # 이미지 전환 pygame.transform.flip(image, x방향, y방향)
            self.image = flipped_image

        # rect
        if self.on_ground and self.on_right:
            self.rect = self.image.get_rect(bottomright = self.rect.bottomright)
        elif self.on_ground and self.on_left:
            self.rect = self.image.get_rect(bottomleft = self.rect.bottomleft)
        elif self.on_ground:
            self.rect = self.image.get_rect(midbottom = self.rect.midbottom)

    def run_dust_animation(self):
        if self.status == 'run':
            self.dust_frame_index += self.dust_anim_speed
            if self.dust_frame_index > len(self.dust_run_particles):
                self.dust_frame_index = 0
            
            dust_particle = self.dust_run_particles[int(self.dust_frame_index)]

            if self.facing_right:
                pos = self.rect.bottomleft - pygame.math.Vector2(2,10)    # Vector2 를 통해 위치조정 가능
                self.display_surface.blit(dust_particle,pos)
            else:
                pos = self.rect.bottomright - pygame.math.Vector2(8,10)
                flipped_dust_particle =  pygame.transform.flip(dust_particle,True,False)
                self.display_surface.blit(flipped_dust_particle,pos)
            

    # 움직임 통제
    def get_input(self):
        keys = pygame.key.get_pressed()   

        if keys[pygame.K_RIGHT] and self.can_move:
            self.direction.x = 1
            self.facing_right = True
        elif keys[pygame.K_LEFT] and self.can_move:
            self.direction.x = - 1
            self.facing_right = False
        else:
            self.direction.x = 0

        if keys[pygame.K_SPACE] and self.can_move:

            if self.can_jump == True and self.jump_count > 0:             
                if self.direction.y > 3 :         # 떨어지면서 점프하면 더블점프
                    pass
                else:
                    self.jump_sound_1.play()
                    self.jump()
                    self.create_jump_particle(self.rect.midbottom)
                    self.jump_count -= 1                                    # 점프카운트 -> 공중점프는 횟수차감 x 
                self.can_jump = False
                self.can_double_jump = True
            elif self.status == 'fall' and self.can_double_jump:         # 더블점프기능 추가하기
                self.jump_speed = -12
                self.jump_sound_2.play()
                self.jump()
                self.create_fall_jump_particle(self.rect.midbottom)
                self.can_double_jump = False
                self.jump_speed = -16

        if keys[pygame.K_s] and self.can_move:
            self.super_jump()

        # Attack
        if keys[pygame.K_a]:
            if self.on_ground == True:
                self.is_attack = True
                self.can_move = False

        if keys[pygame.K_r]:
            self.is_restart = True

            
            
    # player's status  
    def get_status(self):
        if self.direction.y < 0:
            self.status = 'jump'
        elif self.direction.y > 0.8 :       # 중력이 계속 더해져서 [0, 0.8] 이 계속 왔다갔다 하여 error 발생 y > 0.9 로 해결
            self.status = 'fall'
        else:
            if self.direction.x != 0 and self.on_ground :
                self.status = 'run'
            else:
                self.status ='idle'
        
                    

    def apply_gravity(self):                  # player movement의 y축 담당 
        self.direction.y += self.gravity
        if self.direction.y > self.max_gravity:
            self.direction.y = self.max_gravity
        self.rect.y += self.direction.y

    def jump(self):
        self.direction.y = self.jump_speed

    # super jump
    def super_jump(self):
        if self.can_super_jump and self.on_ground:
            self.jump_speed = -28
            self.super_jump_sound.play()
            self.jump()
            self.can_jump = False
            self.create_jump_particle(self.rect.midbottom)
            self.jump_speed = -16
            self.can_super_jump = False


    def update(self):           # rect.x 를 변경 -> 캐릭터를 움직이게 함
        self.get_input()
        self.animate()
        self.get_status()
        self.run_dust_animation()
        #self.rect.x += self.direction.x * self.speed
        #self.apply_gravity()
