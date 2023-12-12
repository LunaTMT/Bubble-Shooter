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

    IMAGES = {  colours.BLACK: 'assets/images/mine/black.png',
                colours.BLUE: 'assets/images/mine/blue.png',
                colours.GREEN: 'assets/images/mine/green.png',
                colours.ORANGE: 'assets/images/mine/orange.png',
                colours.PINK: 'assets/images/mine/pink.png',
                colours.PURPLE: 'assets/images/mine/purple.png',
                colours.RED: 'assets/images/mine/red.png',
                colours.WHITE: 'assets/images/mine/white.png',
                colours.YELLOW: 'assets/images/mine/yellow.png'}

    FALL_SOUND = pygame.mixer.Sound('assets/sounds/fall_swoosh.mp3')  
    POP_SOUND = pygame.mixer.Sound('assets/sounds/pop.mp3')
    
    def __init__(self, game, position):
        super().__init__()
        self.game = game
        
        self.velocity = Vector2(0, 0)
        self.radius = 25
        self.diameter = self.radius * 2
        self.colour = random.choice(colours.ALL)
        self.image = pygame.image.load(Ball.IMAGES[self.colour])
         
        #self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        #pygame.draw.circle(self.image, self.colour, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)

        self._row, self._column = position
        self.fall_position = (None, None)
        self.screen_position = position
        
        self.shooter = False
        self.shot = False
        self.moving = False
        self.speed = 20
        self.fall = False

        self.distance_from_shooter_ball = lambda position : sqrt((self.game.shoot_ball.rect.centerx - position.x) ** 2 + (self.game.shoot_ball.rect.centery - position.y) ** 2)

        if not isinstance(self, ShootBall):
            self.game.static_balls.add(self)

    def __str__(self) -> str:
        return f"{(self.rect.centerx, self.rect.centery)} {self.colour}"

    def __repr__(self) -> str:
        return "1" 
    
    @property 
    def row(self):
        return self._row

    @row.setter
    def row(self, value):
        self._row = value
        self.screen_position = (self._row, self.column)  # Update screen position
    
    @property 
    def column(self):
        return self._column

    @column.setter
    def column(self, value):
        self._column = value
        self.screen_position = (self.row, self._column)
      
    @property
    def screen_position(self):
        return self._screen_position

    @screen_position.setter
    def screen_position(self, value):

        if value != (None, None):
            if isinstance(value, Vector2):
                self._screen_position = value
            else:
                row, column = value
                self._screen_position = Vector2((column * screen.CELL_SIZE) + (12.5 if is_odd(row) else -12.5) + 50, (row * screen.CELL_SIZE) + 50)
            self.rect.center = self._screen_position

    @property
    def array_position(self):
        row = int((self.rect.centery - 50) / screen.CELL_SIZE) 
        column = int( ((self.rect.centerx) - (12.5 if is_odd(row) else - 12.5) -50) / screen.CELL_SIZE) 
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

            if self.rect.left == 0 or self.rect.right == screen.WIDTH :
                self.velocity.x *= -1
                
            if self.rect.top == 0:
                self.velocity.y *= -1
            
            if self.rect.bottom == screen.HEIGHT:
                self.kill()
                self.game.generate_shooting_ball()
                return
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
        
        def get_new_position():

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
        
            def get_array_position_based_on_collision_side(side):
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
            
            def adjust_out_of_bounds(position):
                
                def get_screen_position(position):
                    row, column = position
                    return Vector2((column * screen.CELL_SIZE) + (10 if is_odd(row) else -10) + 50, (row * screen.CELL_SIZE) + 50)
                def get_array_position(position):
                    row = int((position[1] - 50) / screen.CELL_SIZE) 
                    column = int((position[0] - (12.5 if is_odd(row) else - 12.5) -50) / screen.CELL_SIZE) 
                    return (row, column)

                r, c = position
                sides = ["bottom", "top", "right", "left"]
                sides.remove(side)
                
                if self.game.board.in_bounds(position) and self.game.board[r][c]: #if the position is already occupied by a ball
                    positions = [get_screen_position(get_array_position_based_on_collision_side(side)) for side in sides]
                    positions.sort(key=self.distance_from_shooter_ball)
                    print("already in use")
                    print(sides)
                    print(positions)
                    return get_array_position(positions[0])
                    
                #The columns are out of bound
                elif c < 0:
                    return (r + 1, 0) 
                elif c > screen.GRID_WIDTH-1:
                    return (r + 1, screen.GRID_WIDTH-1)

                
                #If the position is fine we just return it
                return position
            
            side = get_collision_side(self, ball)
            return adjust_out_of_bounds(get_array_position_based_on_collision_side(side))
                
        self.moving = False
        
        self.row, self.column = get_new_position()
        #print(self.row, self.column)
        
            
        


            
