import tcod
from components.fighter import Fighter
from components.ai import BasicMonster
from components.item import Item
from components.stairs import Stairs
from random import randint
from entity import Entity
from item_functions import heal, cast_confuse, cast_fireball, cast_lightning
from map_objects.tile import Tile
from map_objects.rectangle import Rect
from game_messages import Message
from render_functions import RenderOrder

class GameMap:
    def __init__(self, width, height, dungeon_level=1):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()
        self.dungeon_level = dungeon_level

    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]

        return tiles
    
    def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, player, 
                entities, max_monsters_per_room, max_items_per_room):
        rooms = []
        num_rooms = 0

        last_center_x = None
        last_center_y = None

        for r in range(max_rooms):
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)
            x = randint(0, map_width - w - 1)
            y = randint(0, map_height - h - 1)

            new_room = Rect(x, y, w, h)

            for other_room in rooms:
                if new_room.intersect(other_room):
                    break
            else:
                # No intersections
                self.create_room(new_room)
                (new_x, new_y) = new_room.center()
                last_center_x = new_x
                last_center_y = new_y

                if num_rooms == 0:
                    player.x = new_x
                    player.y = new_y
                else:
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()
                    if randint(0, 1) == 1:
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)
                self.place_entities(new_room, entities, max_monsters_per_room, max_items_per_room)
                rooms.append(new_room)
                num_rooms += 1 
        
        stairs_comp = Stairs(self.dungeon_level + 1)
        down_stairs = Entity(last_center_x, last_center_y, '>', tcod.white, 'Stairs',
                            render_order=RenderOrder.STAIRS, stairs=stairs_comp)
        entities.append(down_stairs)

    def create_room(self, room):
        # Go through tiles in the rectangle and make them passable
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def place_entities(self, room, entities, max_monsters_per_room, max_items_per_room):
        num_monsters = randint(0, max_monsters_per_room)
        num_items = randint(0, max_items_per_room)

        for i in range(num_monsters):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)
            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                if randint(0, 100) < 80:
                    fighter_comp = Fighter(hp=10, defense=0, power=3, xp=35)
                    ai_comp = BasicMonster()
                    monster = Entity(x, y, 'o', tcod.desaturated_green, 'Orc', blocks=True, 
                                    render_order=RenderOrder.ACTOR, fighter=fighter_comp, ai=ai_comp)
                else:
                    fighter_comp = Fighter(hp=16, defense=1, power=4, xp=100)
                    ai_comp = BasicMonster()
                    monster = Entity(x, y, 'T', tcod.darker_green, 'Troll', blocks=True, 
                                    render_order=RenderOrder.ACTOR, fighter=fighter_comp, ai=ai_comp)
                entities.append(monster)

        for i in range(num_items):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                item_chance = randint(0, 100)

                # Create Healing potion
                if item_chance < 70:
                    item_comp = Item(use_function=heal, amount=4)
                    item = Entity(x, y, '!', tcod.violet, 'Healing Potion', render_order=RenderOrder.ITEM, 
                                item=item_comp)
                    entities.append(item)
                
                # Create Scroll of Fireball
                elif item_chance < 80:
                    item_comp = Item(use_function=cast_fireball, targeting=True, targeting_message=Message(
                        'Left-click a target tile for the fireball, or right-click to cancel.', tcod.light_cyan), damage=12, radius=3)
                    item = Entity(x, y, '#', tcod.red, 'Scroll of Fireball', render_order=RenderOrder.ITEM, 
                                item=item_comp)
                    entities.append(item)
                
                # Create Scroll of Confuse
                elif item_chance < 90:
                    item_comp = Item(use_function=cast_confuse, targeting=True, targeting_message=Message(
                        'Left-click a target tile for the confuse, or right-click to cancel.', tcod.light_cyan))
                    item = Entity(x, y, '#', tcod.light_pink, 'Scroll of Confusion', render_order=RenderOrder.ITEM, 
                                item=item_comp)
                    entities.append(item)

                # Create Scroll of Lightning
                else:
                    item_comp = Item(use_function=cast_lightning, damage=20, max_range=5)
                    item = Entity(x, y, '#', tcod.yellow, 'Scroll of Lightning', render_order=RenderOrder.ITEM, 
                                item=item_comp)
                    entities.append(item)

    def next_floor(self, player, message_log, consts):
        self.dungeon_level += 1
        entities = [player]

        self.tiles = self.initialize_tiles()
        self.make_map(consts['max_rooms'], consts['room_min'], consts['room_max'],
                      consts['map_width'], consts['map_height'], player, entities, 
                      consts['max_monsts_room'], consts['max_items_room'])
        message_log.add_message(Message('You contiue delving deeper...', tcod.light_violet))

        return entities

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True
        return False