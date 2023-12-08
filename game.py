import pygame
from pygame.sprite import Group
from pygame import Vector2

from collections import deque
from board import Board
from ball import Ball, ShootBall

from math import sqrt

import pprint as pp
import os

import screen
import colours


class Game:

    def __init__(self):
        self.running = True
        pygame.init()
        self.screen = pygame.display.set_mode((screen.WIDTH, screen.HEIGHT))  # Create the main surface

        #Instantiating the board
        #   - includes the balls located on the top 5 rows and the empty spaces, represented by 0, from row 5 until row 16
        self.board = Board([[Ball(self, r, c) for c in range(1, 16)] for r in range(1, 6)] + [[0] * 15 for _ in range(10)])
        self.board.game = self #Link to interface
        
        #Balls
        self.shoot_ball = None
        self.generate_shooting_ball()
        self.static_balls =  Group(self.board[:5])
        self.all_falling_balls = Group()

        self.distance_from_shooter_ball = lambda collided_ball : sqrt((self.shoot_ball.rect.centerx - collided_ball.rect.centerx) ** 2 + (self.shoot_ball.rect.centery - collided_ball.rect.centery) ** 2)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False


            for sprite in self.static_balls:
                sprite.handle_event(event)

            for sprite in self.static_balls:
                sprite.handle_event(event)

            self.shoot_ball.handle_event(event)

  
    def update(self):
        
        collisions = pygame.sprite.spritecollide(self.shoot_ball, self.static_balls, dokill=False, collided=pygame.sprite.collide_mask)
        

        if collisions:
            collisions.sort(key=self.distance_from_shooter_ball) 
            print(collisions)
            collided_ball = collisions[0] #Closest ball

            self.shoot_ball.set_new_position_when_collided_with(collided_ball)
            self.board.update()
            
        for sprite in self.static_balls:
            sprite.update()
        
        for sprite in self.all_falling_balls:
            sprite.update()
        
        self.shoot_ball.update() 

    def render(self ):
        self.screen.fill(colours.GREY)
        pygame.draw.line(self.screen, colours.RED, (screen.CENTER_X, 0), (screen.CENTER_X, screen.HEIGHT), 5)  # (start), (end), (line thickness) /middle screen line - unneccasary
        self.draw_shoot_line()
        self.shoot_ball.draw(self.screen)
        self.static_balls.draw(self.screen)
        self.all_falling_balls.draw(self.screen)
    
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

    def generate_shooting_ball(self):
        self.shoot_ball = ShootBall(self, position=Vector2(screen.CENTER_X, screen.HEIGHT-100))

