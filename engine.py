import tcod
from components.fighter import Fighter
from components.ai import BasicMonster
from components.inventory import Inventory
from death_functions import kill_monster, kill_player
from entity import Entity, get_blocking_entity_at
from fov_functions import initialize_fov, recompute_fov
from game_messages import MessageLog
from game_states import GameStates
from input_handlers import handle_keys
from map_objects.game_map import GameMap
from render_functions import clear_all, render_all, RenderOrder

def main():
# Variables
    # Screen
    screen_width = 80
    screen_height = 50
    
    # Bar/Panel
    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height
    
    # Message Log
    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1
    
    # Game Map
    map_width = 80
    map_height = 43
    room_max_size = 10
    room_min_size = 6
    max_rooms = 30
    max_monsters_per_room = 3
    max_items_per_room = 2

    # FoV
    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    # Color
    colors = {
        'dark_wall' : tcod.Color(0, 100, 0),
        'dark_ground' : tcod.Color(50, 150, 50),
        'light_wall' : tcod.Color(130, 110, 50),
        'light_ground' : tcod.Color(200, 180, 50)
    }

    # Player
    fighter_component = Fighter(hp=30, defense=2, power=5)
    inventory_comp = Inventory(26)
    player = Entity(0, 0, '@', tcod.white, 'Player', blocks=True, render_order=RenderOrder.ACTOR, fighter=fighter_component, 
                    inventory=inventory_comp)
    entities = [player]

# Console Setup
    # Initialization
    tcod.console_set_custom_font('consolas10x10_gs_tc.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)
    tcod.console_init_root(screen_width, screen_height, 'RogueLike', False)
    con = tcod.console_new(screen_width, screen_height)
    panel = tcod.console_new(screen_width, panel_height)

    # Game Map
    game_map = GameMap(map_width, map_height)
    game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player, 
                    entities, max_monsters_per_room, max_items_per_room)

    # FoV
    fov_recompute = True
    fov_map = initialize_fov(game_map)

    # Message Log
    message_log = MessageLog(message_x, message_width, message_height)

    # Input
    key = tcod.Key()
    mouse = tcod.Mouse()

    # Game state
    game_state = GameStates.PLAYER_TURN

    while not tcod.console_is_window_closed():
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse)
        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)
        render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, screen_width, screen_height, 
                    bar_width, panel_height, panel_y, mouse, colors)
        fov_recompute = False
        tcod.console_flush()

        clear_all(con, entities)
        
        action = handle_keys(key)

        move = action.get('move')
        pickup = action.get('pickup')
        ext = action.get('exit')
        fullscreen = action.get('fullscreen')

        player_turn_results = []

        if move and game_state == GameStates.PLAYER_TURN:
            dx, dy = move
            dest_x = player.x + dx
            dest_y = player.y + dy

            if not game_map.is_blocked(dest_x, dest_y):
                target = get_blocking_entity_at(entities, dest_x, dest_y)
                if target:
                    attack_results = player.fighter.attack(target)
                    player_turn_results.extend(attack_results)
                else:
                    player.move(dx, dy)
                    fov_recompute = True
                game_state = GameStates.ENEMY_TURN
        
        if ext:
            return True
        
        if fullscreen:
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())
        
        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')

            if message:
                message_log.add_message(message)
            
            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)

                message_log.add_message(message)
        
        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)
                    for enemy_turn_result in enemy_turn_results:
                        message = enemy_turn_result.get('message')
                        dead_entity = enemy_turn_result.get('dead')

                        if message:
                            message_log.add_message(message)
            
                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)

                            message_log.add_message(message)

                            if game_state == GameStates.PLAYER_DEAD:
                                break
                    if game_state == GameStates.PLAYER_DEAD:
                                break
            else:
                game_state = GameStates.PLAYER_TURN


if __name__ == '__main__':
    main()