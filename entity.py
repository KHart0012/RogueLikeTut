# Generic Object to represent player, enemies, items, etc.
import math

class Entity:

    def __init__(self, x, y, char, color, name, blocks=False, fighter=None, ai=None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.fighter = fighter
        self.ai = ai

        if self.fighter:
            self.fighter.owner = self

        if self.ai:
            self.ai.owner = self

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def move_towards(self, tar_x, tar_y, game_map, entities):
        dx = tar_x - self.x
        dy = tar_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))

        if not (game_map.is_blocked(self.x + dx, self.y + dy) or
                get_blocking_entity_at(entities, self.x + dx, self.y + dy)):
            self.move(dx, dy)

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

def get_blocking_entity_at(entities, dest_x, dest_y):
    for entity in entities:
        if entity.blocks and entity.x == dest_x and entity.y == dest_y:
            return entity
    return None