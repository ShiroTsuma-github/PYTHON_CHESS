import pygame
from random import randint

screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True


class Square(pygame.sprite.Sprite):
    def __init__(self,
                 color,
                 width, height,
                 x, y,
                 parent: 'Square',
                 relation_point='NW',
                 image=None):
        pygame.sprite.Sprite.__init__(self)
        self.image = self.set_image(image, width, height, color)
        self.rect = self.image.get_rect()
        self.parent = parent
        self.rect.x = x
        self.rect.y = y
        self.setting_control = {}
        self.offset_x, self.offset_y = self.calc_relation_point(relation_point)
        self.set_relative_to_parent()

    def set_image(self, image, width, height, color):
        if image is None:
            result = pygame.Surface([width, height])
            result.fill(color)
            return result
        result = pygame.image.load(image)
        result = pygame.transform.scale(result, (width, height))
        return result

    def calc_relation_point(self, relation_point):
        if self.parent is None:
            offset_x, offset_y = 0, 0
            return offset_x, offset_y
        coordinates: dict[str, tuple[int, int]] = {
            'NW': (0, 0),
            'N': (self.parent.rect.width / 2, 0),
            'NE': (self.parent.rect.width, 0),
            'E': (self.parent.rect.width, self.parent.rect.height / 2),
            'SE': (self.parent.rect.width, self.parent.rect.height),
            'S': (self.parent.rect.width / 2, self.parent.rect.height),
            'SW': (0, self.parent.rect.height),
            'W': (0, self.parent.rect.height / 2),
            'C': (self.parent.rect.width / 2, self.parent.rect.height / 2),
        }
        offset_x = coordinates.get(relation_point, 0)[0]
        offset_y = coordinates.get(relation_point, 0)[1]
        return offset_x, offset_y

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

    def set_relative_to_parent(self) -> None:
        if self.parent is None:
            return
        if self.is_inside_parent():
            return
        self.rect.x = self.rect.x + self.parent.rect.x + self.offset_x
        self.rect.y = self.rect.y + self.parent.rect.y + self.offset_y

    def is_inside_parent(self) -> bool:
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

    def get_relative_to_parent(self) -> tuple[int, int]:
        if self.parent is not None:
            return self.rect.x - self.parent.rect.x, self.rect.y - self.parent.rect.y
        else:
            return self.rect.x, self.rect.y

    def update(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                if self.rect.collidepoint(event.pos):
                    self.image.fill("purple")

    def move(self, x, y):
        self.rect.x += x
        self.rect.y += y

    def bound_move(self, x, y):
        if self.parent is None:
            raise Exception("Cannot bound move without parent")
        elif self.offset_x + self.rect.width > self.parent.rect.width:
            raise Exception("Cannot bound_move. Relation point + width > parent width")
        elif self.offset_y + self.rect.height > self.parent.rect.height:
            raise Exception("Cannot bound_move. Relation point + width > parent width")
        max_x = self.parent.rect.width - self.rect.width
        max_y = self.parent.rect.height - self.rect.height
        self.rect.x += x
        self.rect.y += y
        current_x, current_y = self.get_relative_to_parent()
        self.rect.x = self.clamp(current_x, 0, max_x)
        self.rect.y = self.clamp(current_y, 0, max_y)
        self.set_relative_to_parent()

    def stick(self, x, y):
        if self.parent is None:
            raise Exception("Cannot stick without parent")
        self.rect.x = self.parent.rect.x + x + self.offset_x
        self.rect.y = self.parent.rect.y + y + self.offset_y

    def bound_stick(self, x, y, relation_point=None):
        if self.parent is None:
            raise Exception("Cannot bound stick without parent")
        max_x = self.parent.rect.width - self.rect.width
        max_y = self.parent.rect.height - self.rect.height
        self.rect.x = self.parent.rect.x + self.clamp(x + self.offset_x, 0, max_x)
        self.rect.y = self.parent.rect.y + self.clamp(y + self.offset_y, 0, max_y)

    def relative_place(self, x, y):
        if self.parent is None:
            raise Exception("Cannot relative place without parent")
        if self.setting_control.get('parent_rel_pos_x', None) is None:
            self.setting_control['parent_rel_pos_x'] = self.parent.rect.x
        if self.setting_control.get('parent_rel_pos_y', None) is None:
            self.setting_control['parent_rel_pos_y'] = self.parent.rect.y
        self.rect.x = self.setting_control.get('parent_rel_pos_x') + self.offset_x
        self.rect.y = self.setting_control.get('parent_rel_pos_y') + y + self.offset_y

    def place(self, x, y):
        self.rect.x = x
        self.rect.y = y


all_sprites = pygame.sprite.Group()
parent = Square("red", 500, 500, 100, 100, None)
child = Square("blue", 400, 400, 0, 0, parent, relation_point='NE')
child2 = Square("green", 300, 300, 50, 0, child)
child3 = Square("yellow", 200, 150, 50, 0, child2)
child4 = Square("orange", 100, 100, 50, 0, child3, image='resources/images/enemy.png', relation_point='E')
child5 = Square("pink", 50, 50, 50, 0, child4, relation_point='E')
all_sprites.add(parent)
all_sprites.add(child)
all_sprites.add(child2)
all_sprites.add(child3)
all_sprites.add(child4)
all_sprites.add(child5)


while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("purple")
    all_sprites.draw(screen)
    
    # child.bound_move(randint(-3, 3), randint(-3, 3))
    child2.bound_move(randint(-3, 5), randint(-3, 3))
    child3.bound_move(randint(-3, 3), randint(-3, 3))
    child4.bound_stick(0, 0)
    child5.relative_place(0, 0)
    all_sprites.update(events)

    # RENDER YOUR GAME HERE

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
