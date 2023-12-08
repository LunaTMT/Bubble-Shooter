import pygame
from pygame.sprite import Sprite
from pygame.math import Vector2

import colours
import random
import screen
pygame.mixer.init()

class Ball(Sprite):

    FALL_SOUND = pygame.mixer.Sound('assets/sounds/fall_swoosh.mp3')  
    POP_SOUND = pygame.mixer.Sound('assets/sounds/pop.mp3')
    
    def __init__(self, game, row=None, column=None, position=None):
        super().__init__()
        self.game = game

        self.row, self.columnn = (row, column)
        self.fall_position = None
        
        if position:
            self.screen_position = position
        else:
            self.screen_position = row, column

        self.velocity = Vector2(0, 0)
        self.radius = 25
        self.diameter = self.radius * 2
        self.colour = random.choice(colours.ALL)
         
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.colour, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=self.screen_position)
        self.mask = pygame.mask.from_surface(self.image)

        self.shooter = False
        self.shot = False
        self.moving = False
        self.speed = 15
        self.fall = False

    def __str__(self) -> str:
        return f"{(self.rect.centerx, self.rect.centery)} {self.colour}"

    def __repr__(self) -> str:
        return "1" 

    @property
    def screen_position(self):
        return self._screen_position

    @screen_position.setter
    def screen_position(self, value):
        if isinstance(value, Vector2):
            self._screen_position = value
        else:
            row, column = value
            self._screen_position = Vector2((column * screen.CELL_SIZE) + (10 if not row % 2 else -10), (row * screen.CELL_SIZE))
        
    @property
    def array_position(self):
        row = int((self.rect.centery - 10) / 50) 
        column = int((self.rect.centerx - 10 + (20 if not row%2 else 0))/ 50)  - 1
        return row, column

    


    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.moving and self.shooter: 
            mouse_x, mouse_y = pygame.mouse.get_pos()
            direction_vector = pygame.math.Vector2(mouse_x - self.screen_position.x, mouse_y - self.screen_position.y)
            self.velocity = direction_vector.normalize() * self.speed
           
            self.moving = True
            self.shooter = False
            self.shot = True

    def update(self):     
        if self.moving:
            self.screen_position += self.velocity
            self.rect.center = self.screen_position  # Update the rectangle position to match the circle
            self.rect.clamp_ip(pygame.Rect(0, 0, screen.WIDTH, screen.HEIGHT))

            if self.rect.left == 0 or self.rect.right == screen.WIDTH:
                self.velocity.x *= -1
                
            if self.rect.top == 0 or self.rect.bottom == screen.HEIGHT:
                self.velocity.y *= -1
        else:
            self.velocity = Vector2(0, 0)
        
        if self.fall:
            self.rect.y += 10

            if self.rect.y > screen.HEIGHT:
                r, c = self.fall_position  
                self.kill()
                self.game.board[r][c] = 0

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)
 
    
                

class ShootBall(Ball):
    def __init__(self, game, position):
        super().__init__(game, row=None, column=None, position=position)
        self.shooter = True


    def set_new_position_when_collided_with(self, collided_ball):
        
        #self.board[r][c] = self.shoot_ball.get_array_position()
        """
        This function must do the error check to ensure the new ball position isnt already occupied
        """

        def detect_collision_side(ball_1, ball_2):
            rect1 = ball_1.rect
            rect2 = ball_2.rect

            if rect1.colliderect(rect2):
                # Calculate the distances between the centers in both x and y axes
                dx = rect2.centerx - rect1.centerx
                dy = rect2.centery - rect1.centery

                # Calculate the combined half-widths and half-heights of the rectangles
                combined_half_width = (rect1.width + rect2.width) / 2
                combined_half_height = (rect1.height + rect2.height) / 2

                # Determine the side of collision based on the distances and combined sizes
                if abs(dx) <= combined_half_width and abs(dy) <= combined_half_height:
                    overlap_x = combined_half_width - abs(dx)
                    overlap_y = combined_half_height - abs(dy)

                    if overlap_x >= overlap_y:
                        if dy > 0:
                            return "top"  # Collision on the bottom side of rect1
                        else:
                            return "bottom"  # Collision on the top side of rect1
                    else:
                        if dx > 0:
                            return "left"  # Collision on the right side of rect1
                        else:
                            return "right"  # Collision on the left side of rect1

            return None  # No collision detected or partial overlap

        self.moving = False

        side = detect_collision_side(self, collided_ball)
        collided_row, _ = collided_ball.array_position
        match side:
            case "bottom":                                                                 
                self.rect.center = Vector2(collided_ball.rect.center) + Vector2(0, collided_ball.diameter) + (Vector2(20, 0) if not collided_row%2 else Vector2(-20, 0))
            case "top":
                self.rect.center = Vector2(collided_ball.rect.center) - Vector2(0, collided_ball.diameter) + (Vector2(20, 0) if not collided_row%2 else Vector2(-20, 0))  
            case "right":
                self.rect.center = Vector2(collided_ball.rect.center) + Vector2(collided_ball.diameter, 0)
            case "left":
                self.rect.center = Vector2(collided_ball.rect.center) - Vector2(collided_ball.diameter, 0)
    

    