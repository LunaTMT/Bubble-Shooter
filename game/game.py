import pygame
from pygame.sprite import Group
from pygame import Vector2


from .board import Board
from .ball import Ball, ShootBall
from .fish import Fish
from .bubbles import Bubble

from math import sqrt, atan2, degrees, radians

import pprint as pp
import os
import random

from .constants import colours, screen


class Game:

    def __init__(self):
        
        self.running = True
        pygame.init()
        self.screen = pygame.display.set_mode((screen.WIDTH + (screen.OFFSET), screen.HEIGHT))  # Create the main surface

        #Balls
        self.shoot_ball = None
        self.static_balls = Group()
        self.all_falling_balls = Group()

        self.bubbles = Group()
        self.fishes = Group()

        #Instantiating the board
        #   - includes the balls located on the top 5 rows and the empty spaces, represented by 0, from row 5 until row 16
        top_rows = [[Ball(self, (r, c)) for c in range(screen.GRID_WIDTH)] for r in range(screen.TOP_ROWS)]
        remaining_empty_rows = [[0] * screen.GRID_WIDTH for _ in range(12)]
        
        self.board = Board(top_rows + remaining_empty_rows)
        self.board.game = self #Link to interface - Cant include it in class parameter that inherits from list
        
        self.generate_shooting_ball()
    
        self.distance_from_shooter_ball = lambda collided_ball : sqrt((self.shoot_ball.rect.centerx - collided_ball.rect.centerx) ** 2 + (self.shoot_ball.rect.centery - collided_ball.rect.centery) ** 2)

        self.end_game_y = (17 * screen.CELL_SIZE)
        self.end_game = False
        self.restart = False

        self.background_image = pygame.image.load('assets/images/background.jpeg') 
        
        self.end_game_image = pygame.image.load('assets/images/end_game.png')
        self.end_game_image_rect = self.end_game_image.get_rect()
        self.end_game_image_rect.center = ((screen.WIDTH - self.end_game_image_rect.width)   // 2, 
                                           (screen.HEIGHT - self.end_game_image_rect.height) // 2)

        self.arrow_image = pygame.image.load('assets/images/arrow.png').convert_alpha() 
        self.arrow_rect = self.arrow_image.get_rect(topleft=(screen.CENTER_X, screen.HEIGHT - 100))


        #Fish
        self.max_fish = 10
        self.spawn_rate = 80  # Adjust spawn rate (lower for more frequent spawns)
        self.spawn_counter = 0

        #Bubbles
        self.spawn_interval = 500  # Interval between bubble releases in milliseconds (2 seconds)
        self.last_spawn_time = pygame.time.get_ticks()

    def handle_events(self):
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                self.running = False
            
            elif self.end_game:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.restart = True
                elif self.restart and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.__init__()
            else:           
                for sprite in self.static_balls:
                    sprite.handle_event(event)

                self.shoot_ball.handle_event(event)

  
    def update(self):
        
        self.check_collision()
                
        for sprite in self.static_balls:
            sprite.update()
        
        for sprite in self.all_falling_balls:
            sprite.update()
        
        self.shoot_ball.update() 
        
        self.fishes.update()
        self.generate_fishes()

        self.bubbles.update()
        self.generate_bubbles()
        
        
    def render(self ):
        self.screen.fill(colours.SEA_BLUE_BACKGROUND)
        self.screen.blit(self.background_image, (0,0))
        
        #pygame.draw.line(self.screen, colours.RED, (screen.CENTER_X, 0), (screen.CENTER_X, screen.HEIGHT), 5)  # (start), (end), (line thickness) /middle screen line - unneccasary
        #pygame.draw.line(self.screen, colours.RED, (0, self.end_game_y), (screen.WIDTH, self.end_game_y), 5)

        self.draw_shoot_arrow()

        self.shoot_ball.draw(self.screen)
        self.static_balls.draw(self.screen)
        self.all_falling_balls.draw(self.screen)

        self.fishes.draw(self.screen)
        self.bubbles.draw(self.screen)

        if self.end_game:
            self.screen.blit(self.end_game_image, self.end_game_image_rect.center)
     

            

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            pygame.display.flip() 
        pygame.quit()


    def draw_shoot_arrow(self):
        if not self.shoot_ball.shot:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            direction = pygame.math.Vector2(mouse_x - self.shoot_ball.rect.centerx, mouse_y - self.shoot_ball.rect.centery)
            direction.normalize_ip()

            angle_to_rotate = degrees(atan2(direction.y, direction.x))
            rotated_image = pygame.transform.rotate(self.arrow_image, -angle_to_rotate)  # Negative angle to match coordinate system
            rotated_rect = rotated_image.get_rect(center=self.shoot_ball.rect.center)  # Use the ball's center as reference
            self.screen.blit(rotated_image, rotated_rect.topleft)





    def draw_end_game_text(self):
        self.screen.blit(self.end_game_text_surface, self.end_game_text_rect)
        self.screen.blit(self.end_game_text_surface2, self.end_game_text_rect2)

    def draw_stats_box(self):
        pygame.draw.rect(self.screen, colours.BLACK, (screen.WIDTH, 0, screen.OFFSET, screen.HEIGHT), border_radius=4)


    def generate_shooting_ball(self):
        self.shoot_ball = ShootBall(self, position=Vector2(screen.CENTER_X, screen.HEIGHT-100))

    def generate_fishes(self):
        if len(self.fishes) < self.max_fish:
            self.spawn_counter += 1
            if self.spawn_counter == self.spawn_rate:
                self.fishes.add(Fish())
                self.spawn_counter = 0

    def generate_bubbles(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn_time > self.spawn_interval:
            self.bubbles.add(Bubble(random.randint(75, 100), screen.HEIGHT - 80))
            self.last_spawn_time = current_time

    def check_collision(self):
        collisions = pygame.sprite.spritecollide(self.shoot_ball, self.static_balls, dokill=False, collided=pygame.sprite.collide_mask)
        if not self.end_game:
            if collisions:
                collisions.sort(key=self.distance_from_shooter_ball) 
                self.shoot_ball.set_new_position_when_collided_with(collisions[0])
                self.board.update()

                if not self.end_game:
                    self.generate_shooting_ball()