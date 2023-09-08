import pygame
from random import randint
from math import floor, ceil

screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True


class Square(pygame.sprite.Sprite):
    def __init__(self,
                 color,
                 width, height,
                 x, y,
                 parent: 'Square',
                 parent_relation='NW',
                 children_relation='NW',
                 image=None):
        pygame.sprite.Sprite.__init__(self)
        self.image = self.set_image(image, width, height, color)
        self.rect = self.image.get_rect()
        self.parent = parent
        self.initial_offsets = (x, y)
        self.relations = (parent_relation, children_relation)
        self.rect.x = x
        self.rect.y = y
        self.setting_control = {}
        self.offset_x, self.offset_y = self.calc_parent_relation(parent_relation, children_relation)
        self.set_relative_to_parent()

    def set_image(self, image, width, height, color):
        if image is None:
            result = pygame.Surface([width, height])
            result.fill(color)
            return result
        result = pygame.image.load(image)
        result = pygame.transform.scale(result, (width, height))
        return result

    def calc_parent_relation(self, parent_relation, children_relation):
        if self.parent is None:
            offset_x, offset_y = 0, 0
            return offset_x, offset_y
        parent_coordinates: dict[str, tuple[int, int]] = {
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
        children_coordinates: dict[str, tuple[int, int]] = {
            'NW': (0, 0),
            'N': (self.rect.width / 2, 0),
            'NE': (self.rect.width, 0),
            'E': (self.rect.width, self.rect.height / 2),
            'SE': (self.rect.width, self.rect.height),
            'S': (self.rect.width / 2, self.rect.height),
            'SW': (0, self.rect.height),
            'W': (0, self.rect.height / 2),
            'C': (self.rect.width / 2, self.rect.height / 2),
        }
        offset_x = parent_coordinates.get(parent_relation, 0)[0] - children_coordinates.get(children_relation, 0)[0]
        offset_y = parent_coordinates.get(parent_relation, 0)[1] - children_coordinates.get(children_relation, 0)[1]
        return offset_x, offset_y

    def change_parent(self, new_parent: 'Square'):
        self.parent = new_parent
        self.rect.x = self.initial_offsets[0]
        self.rect.y = self.initial_offsets[1]
        self.offset_x, self.offset_y = self.calc_parent_relation(self.relations[0], self.relations[1])
        self.set_relative_to_parent()
        self.setting_control.pop('parent_rel_pos_x', None)
        self.setting_control.pop('parent_rel_pos_y', None)

    def change_relations(self, parent_relation, children_relation):
        self.relations = (parent_relation, children_relation)
        self.offset_x, self.offset_y = self.calc_parent_relation(parent_relation, children_relation)
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

    def __dynamic_remainder(self):
        # NOTE: This is pretty bad way to do this, but it solves the problem
        #      of pixel rounding and difference between actual and expected final position
        #      It also prevents visual stutter, when object snaps to final position
        # NOTE: It also makes it possible, to have very big timespan
        ret_x = 0
        ret_y = 0
        if self.setting_control.get('move_remainders', None) is None:
            self.setting_control['move_remainders'] = {'x': 0, 'y': 0}
        self.setting_control['move_remainders']['x'] += self.setting_control.get('mov_diff_x')
        self.setting_control['move_remainders']['y'] += self.setting_control.get('mov_diff_y')
        if abs(self.setting_control.get('move_remainders')['x']) >= 1:
            ret_x = self.setting_control.get('move_remainders')['x'] -\
                self.setting_control.get('move_remainders')['x'] % 1
        if abs(self.setting_control.get('move_remainders')['y']) >= 1:
            ret_y = self.setting_control.get('move_remainders')['y'] -\
                self.setting_control.get('move_remainders')['y'] % 1
        self.setting_control['move_remainders']['x'] -= ret_x
        self.setting_control['move_remainders']['y'] -= ret_y
        return (
            ret_x,
            ret_y
        )

    def move_to(self, x, y, timespan=1):
        if self.rect.x == x and self.rect.y == y:
            return
        if self.setting_control.get('move_invokes', None) is None:
            self.setting_control['move_invokes'] = 0
            self.setting_control['mov_diff_x'] = (x - self.rect.x) / timespan
            self.setting_control['mov_diff_y'] = (y - self.rect.y) / timespan
        # NOTE: For information, look at note in __dynamic_remainder
        move_x, move_y = self.__dynamic_remainder()
        self.rect.x += move_x
        self.rect.y += move_y
        self.setting_control['move_invokes'] += 1
        if self.setting_control.get('move_invokes') >= timespan:
            self.setting_control.pop('move_invokes', None)
            self.setting_control.pop('move_remainders', None)
            self.rect.x = x
            self.rect.y = y

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

    def bound_stick(self, x, y, parent_relation=None):
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
        self.rect.x = self.setting_control.get('parent_rel_pos_x') + x + self.offset_x
        self.rect.y = self.setting_control.get('parent_rel_pos_y') + y + self.offset_y

    def place(self, x, y):
        self.rect.x = x
        self.rect.y = y


def next_relation():
    relations = ('NW', 'N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'C')
    pointer = 0
    while True:
        yield relations[pointer]
        pointer += 1
        if pointer >= len(relations):
            pointer = 0

gen = next_relation()

all_sprites = pygame.sprite.Group()
parent = Square("red", 400, 400, 100, 100, None)
parent2 = Square("green", 400, 400, 500, 100, None)
child = Square("blue", 300, 300, 0, 0, parent2, 'C', 'C')
all_sprites.add(parent)
all_sprites.add(parent2)
all_sprites.add(child)

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
    all_sprites.update(events)
    # if child.parent == parent:
    #     child.change_parent(parent2)
    # else:
    #     child.change_parent(parent)
    # RENDER YOUR GAME HERE
    relation = next(gen)
    # child.change_relations(relation, relation)
    parent2.move_to(400, 400, 1000)
    child.bound_stick(0, 0)
    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()
