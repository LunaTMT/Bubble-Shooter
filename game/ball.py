import pygame
from pygame.sprite import Sprite
from pygame.math import Vector2

from .constants import colours, screen
import random
from math import sqrt
pygame.mixer.init()


def is_odd(value):
        return True if value%2 else False
   

class Ball(Sprite):

    FALL_SOUND = pygame.mixer.Sound('assets/sounds/fall_swoosh.mp3')  
    POP_SOUND = pygame.mixer.Sound('assets/sounds/pop.mp3')
    
    def __init__(self, game, position):
        super().__init__()
        self.game = game
        

        self.row, self.columnn = position
        self.fall_position = (None, None)
        self.screen_position = position 
            
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

        self.distance_from_shooter_ball = lambda position : sqrt((self.game.shoot_ball.rect.centerx - position.x) ** 2 + (self.game.shoot_ball.rect.centery - position.y) ** 2)

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
            self._screen_position = Vector2((column * screen.CELL_SIZE) + (10 if is_odd(row) else -10) + 50, (row * screen.CELL_SIZE) + 50)

    @property
    def array_position(self):
        row = int((self.rect.centery - 50) / screen.CELL_SIZE) 
        column = int( ((self.rect.centerx) - (10 if is_odd(row) else - 10) -50) / screen.CELL_SIZE) 
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
    def __init__(self, game , position):
        super().__init__(game, position)
        self.center = False
        self.shooter = True
 

    def set_new_position_when_collided_with(self, ball):
        
        """
        This function must do the error check to ensure the new ball position isnt already occupied
        """

        def get_collision_side(ball_1, ball_2):
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

        def get_new_position_based_on_side(side):

            def get_screen_position(position):
                row, column = position
                return Vector2((column * screen.CELL_SIZE) + (10 if is_odd(row) else -10) + 50, (row * screen.CELL_SIZE) + 50)

            def adjust_out_of_bounds(position):
                r, c = position
                
                if self.game.board[r][c]: #if the position is already occupied by a ball
                    print("Already used")
                    positions = [get_screen_position(get_new_array_position_based_on_collision_side(side)) for side in ("bottom", "top", "right", "left")]
                    positions.sort(key=self.distance_from_shooter_ball)
                    return positions[0]
                    
                #The columns are out of bound
                elif c < 0:
                    return (r + 1, 0) 
                elif c > screen.GRID_WIDTH-1:
                    return (r + 1, screen.GRID_WIDTH-1)
                
                #If the position is fine we just return it
                return position
                    
            def get_new_array_position_based_on_collision_side(side):
                match side:
                    case "bottom":                                                                 
                        position = Vector2(ball.array_position) + Vector2(1, 0)
                    case "top":
                        position = Vector2(ball.array_position) + Vector2(-1, 0)
                    case "right":
                        position = Vector2(ball.array_position) + Vector2(0, 1)
                    case "left":
                        position = Vector2(ball.array_position) + Vector2(0, -1)
                
                position = (int(position.x), int(position.y))
                return position
            
            return adjust_out_of_bounds(get_new_array_position_based_on_collision_side(side))
                

              
        self.moving = False
        new_position = get_new_position_based_on_side(get_collision_side(self, ball))  

        self.screen_position = new_position
        self.rect.center = self.screen_position
            
        

            
