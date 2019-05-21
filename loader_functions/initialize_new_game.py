import tcod

from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from entity import Entity
from game_messages import MessageLog
from game_states import GameStates
from map_objects.game_map import GameMap
from render_functions import RenderOrder

def get_constants():
    window_title = 'Roguelike Game'

    screen_width = 100
    screen_height = 70

    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

    map_width = 75
    map_height = 55

    room_max_size = 13
    room_min_size = 8
    max_rooms = 25

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    max_monsters_per_room = 3
    max_items_per_room = 2

    colors = {
        'dark_wall': tcod.Color(0, 0, 100),
        'dark_ground': tcod.Color(50, 50, 150),
        'light_wall': tcod.Color(130, 110, 50),
        'light_ground': tcod.Color(200, 180, 50)
    }

    consts = {
        'window_title': window_title,
        'scrn_width': screen_width,
        'scrn_height': screen_height,
        'bar_width': bar_width,
        'panel_height': panel_height,
        'panel_y': panel_y,
        'msg_x': message_x,
        'msg_width': message_width,
        'msg_height': message_height,
        'map_width': map_width,
        'map_height': map_height,
        'room_max': room_max_size,
        'room_min': room_min_size,
        'max_rooms': max_rooms,
        'fov_algo': fov_algorithm,
        'fov_light_walls': fov_light_walls,
        'fov_radius': fov_radius,
        'max_monsts_room': max_monsters_per_room,
        'max_items_room': max_items_per_room,
        'colors': colors
    }

    return consts

def get_game_variables(consts):
    # Player
    fighter_component = Fighter(hp=30, defense=2, power=5)
    inventory_comp = Inventory(26)
    level_comp = Level()
    player = Entity(0, 0, '@', tcod.white, 'Player', blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, 
                    inventory=inventory_comp, level=level_comp)
    entities = [player]

    # Game Map
    game_map = GameMap(consts['map_width'], consts['map_height'])
    game_map.make_map(consts['max_rooms'], consts['room_min'], consts['room_max'], consts['map_width'], consts['map_height'], 
                    player, entities, consts['max_monsts_room'], consts['max_items_room'])

    # Game State
    game_state = GameStates.PLAYER_TURN

    # Message Log
    message_log = MessageLog(consts['msg_x'], consts['msg_width'], consts['msg_height'])

    return player, entities, game_map, message_log, game_state