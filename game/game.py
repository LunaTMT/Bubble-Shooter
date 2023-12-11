import pygame
from pygame.sprite import Group
from pygame import Vector2


from .board import Board
from .ball import Ball, ShootBall

from math import sqrt

import pprint as pp
import os

from .constants import colours, screen


class Game:

    def __init__(self):
        
        self.running = True
        pygame.init()
        self.screen = pygame.display.set_mode((screen.WIDTH, screen.HEIGHT))  # Create the main surface

        #Balls
        self.shoot_ball = None
        self.static_balls = Group()
        self.all_falling_balls = Group()

        #Instantiating the board
        #   - includes the balls located on the top 5 rows and the empty spaces, represented by 0, from row 5 until row 16
        top_rows = [[Ball(self, (r, c)) for c in range(screen.GRID_WIDTH)] for r in range(screen.TOP_ROWS)]
        remaining_empty_rows = [[0] * screen.GRID_WIDTH for _ in range(11)]
        
        self.board = Board(top_rows + remaining_empty_rows)
        self.board.game = self #Link to interface - Cant include it in class parameter that inherits from list
        
    
        self.generate_shooting_ball()
        

        self.distance_from_shooter_ball = lambda collided_ball : sqrt((self.shoot_ball.rect.centerx - collided_ball.rect.centerx) ** 2 + (self.shoot_ball.rect.centery - collided_ball.rect.centery) ** 2)

        self.end_game_y = (17 * screen.CELL_SIZE)
        self.end_game = False
        self.restart = False

        self.end_game_text_surface = pygame.font.Font(None, 100).render("GAME OVER", True, colours.BLACK)
        self.end_game_text_rect = self.end_game_text_surface.get_rect()
        self.end_game_text_rect.center = (screen.WIDTH // 2, screen.HEIGHT // 2)

        self.end_game_text_surface2 = pygame.font.Font(None, 70).render("CLICK TO PLAY AGAIN", True, colours.BLACK)
        self.end_game_text_rect2 = self.end_game_text_surface2.get_rect()
        self.end_game_text_rect2.center = (screen.WIDTH // 2, (screen.HEIGHT // 2) + 100)
        


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

                for sprite in self.static_balls:
                    sprite.handle_event(event)

                self.shoot_ball.handle_event(event)

  
    def update(self):
        collisions = pygame.sprite.spritecollide(self.shoot_ball, self.static_balls, dokill=False, collided=pygame.sprite.collide_mask)
        if not self.end_game:
            if collisions:
                collisions.sort(key=self.distance_from_shooter_ball) 
                self.shoot_ball.set_new_position_when_collided_with(collisions[0])
                self.board.update()
                
            for sprite in self.static_balls:
                sprite.update()
            
            for sprite in self.all_falling_balls:
                sprite.update()
            
            self.shoot_ball.update() 
        

    def render(self ):
        self.screen.fill(colours.GREY)

        pygame.draw.line(self.screen, colours.RED, (screen.CENTER_X, 0), (screen.CENTER_X, screen.HEIGHT), 5)  # (start), (end), (line thickness) /middle screen line - unneccasary
        pygame.draw.line(self.screen, colours.RED, (0, self.end_game_y), (screen.WIDTH, self.end_game_y), 5)

        self.draw_shoot_line()
        self.shoot_ball.draw(self.screen)
        self.static_balls.draw(self.screen)
        self.all_falling_balls.draw(self.screen)

        if self.end_game:
            self.draw_end_game_text()
            

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            pygame.display.flip() 
        pygame.quit()

    def draw_shoot_line(self):
        if not self.shoot_ball.shot:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            direction = pygame.math.Vector2(mouse_x - self.shoot_ball.rect.centerx, mouse_y - self.shoot_ball.rect.centery)
            direction.normalize_ip()
            endpoint = (self.shoot_ball.rect.centerx + direction.x * 200, self.shoot_ball.rect.centery + direction.y * 200)
            
            # Draw a line from the ball's center to the calculated endpoint
            pygame.draw.line(self.screen, colours.BLACK, self.shoot_ball.rect.center, endpoint, 5)

    def draw_end_game_text(self):
        self.screen.blit(self.end_game_text_surface, self.end_game_text_rect)
        self.screen.blit(self.end_game_text_surface2, self.end_game_text_rect2)

    def generate_shooting_ball(self):
        self.shoot_ball = ShootBall(self, position=Vector2(screen.CENTER_X, screen.HEIGHT-100))
        

