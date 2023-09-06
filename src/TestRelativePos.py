from typing import Type
import pygame
from random import randint

screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True


class Square(pygame.sprite.Sprite):
    def __init__(self, color, width, height, x, y, parent: 'Square'):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.parent = parent
        self.rect.x, self.rect.y = x, y
        self.set_relative_to_parent()

    def clamp(self, n: int, min: int, max: int, _bool=False) -> int:
        if n < min:
            if _bool:
                return False
            return min
        elif n > max:
            if _bool:
                return False
            return max
        else:
            if _bool:
                return True
            return n

    def set_relative_to_parent(self):
        if self.parent is None:
            return
        if self.is_inside_parent():
            return
        self.rect.x = self.rect.x + self.parent.rect.x
        self.rect.y = self.rect.y + self.parent.rect.y

    def is_inside_parent(self):
        if self.parent is None:
            if (self.rect.x + self.rect.width in range(0, screen.get_width())) and\
               (self.rect.y + self.rect.height in range(0, screen.get_height())):
                return True
            return False
        rel_x, rel_y = self.get_relative_to_parent()
        if not self.clamp(rel_y, 0, self.parent.rect.height - self.rect.height, True):
            return False
        if not self.clamp(rel_x, 0, self.parent.rect.width - self.rect.width, True):
            return False
        return True

    def get_relative_to_parent(self):
        if self.parent is not None:
            return self.rect.x - self.parent.rect.x, self.rect.y - self.parent.rect.y
        else:
            return self.rect.x, self.rect.y

    def move(self, x, y):
        self.rect.x += x
        self.rect.y += y

    def bound_move(self, x, y):
        if self.parent is not None:
            max_x = self.parent.rect.width - self.rect.width
            max_y = self.parent.rect.height - self.rect.height
        self.rect.x += x
        self.rect.y += y
        current_x, current_y = self.get_relative_to_parent()
        self.rect.x = self.clamp(current_x, 0, max_x)
        self.rect.y = self.clamp(current_y, 0, max_y)
        self.set_relative_to_parent()


all_sprites = pygame.sprite.Group()
parent = Square("red", 500, 500, 100, 100, None)
child = Square("blue", 50, 50, 0, 0, parent)
child2 = Square("green", 50, 50, 50, 0, parent)
all_sprites.add(parent)
all_sprites.add(child)
all_sprites.add(child2)


while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("purple")
    all_sprites.draw(screen)
    child.bound_move(randint(-3, 3), randint(-3, 3))
    child2.bound_move(randint(-3, 3), randint(-3, 3))

    # RENDER YOUR GAME HERE

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
