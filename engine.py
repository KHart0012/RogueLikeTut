import tcod
from components.fighter import Fighter
from components.ai import BasicMonster
from entity import Entity, get_blocking_entity_at
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates
from input_handlers import handle_keys
from map_objects.game_map import GameMap
from render_functions import clear_all, render_all

def main():
    screen_width = 80
    screen_height = 50
    map_width = 80
    map_height = 45
    room_max_size = 10
    room_min_size = 6
    max_rooms = 30
    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10
    max_monsters_per_room = 3

    colors = {
        'dark_wall' : tcod.Color(0, 100, 0),
        'dark_ground' : tcod.Color(50, 150, 50),
        'light_wall' : tcod.Color(130, 110, 50),
        'light_ground' : tcod.Color(200, 180, 50)
    }

    fighter_component = Fighter(hp=30, defense=2, power=5)
    player = Entity(0, 0, '@', tcod.white, 'Player', blocks=True, fighter=fighter_component)
    entities = [player]

    tcod.console_set_custom_font('consolas10x10_gs_tc.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)
    tcod.console_init_root(screen_width, screen_height, 'RogueLike', False)

    con = tcod.console_new(screen_width, screen_height)

    game_map = GameMap(map_width, map_height)
    game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities, max_monsters_per_room)

    fov_recompute = True
    fov_map = initialize_fov(game_map)

    key = tcod.Key()
    mouse = tcod.Mouse()
    game_state = GameStates.PLAYER_TURN

    while not tcod.console_is_window_closed():
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS, key, mouse)
        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)
        render_all(con, entities, game_map, fov_map, fov_recompute, screen_width, screen_height, colors)
        fov_recompute = False
        tcod.console_flush()

        clear_all(con, entities)
        
        action = handle_keys(key)

        move = action.get('move')
        ext = action.get('exit')
        fullscreen = action.get('fullscreen')

        if move and game_state == GameStates.PLAYER_TURN:
            dx, dy = move
            dest_x = player.x + dx
            dest_y = player.y + dy

            if not game_map.is_blocked(dest_x, dest_y):
                target = get_blocking_entity_at(entities, dest_x, dest_y)
                if target:
                    print('You kick the ' + target.name + ' in the shin!')
                else:
                    player.move(dx, dy)
                    fov_recompute = True
                game_state = GameStates.ENEMY_TURN
        
        if ext:
            return True
        
        if fullscreen:
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())
        
        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    entity.ai.take_turn(player, fov_map, game_map, entities)
            game_state = GameStates.PLAYER_TURN


if __name__ == '__main__':
    main()