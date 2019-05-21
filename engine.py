import tcod
from components.ai import BasicMonster
from death_functions import kill_monster, kill_player
from entity import get_blocking_entity_at
from fov_functions import initialize_fov, recompute_fov
from game_messages import Message
from game_states import GameStates
from input_handlers import handle_keys, handle_mouse, handle_main_menu
from loader_functions.data_loader import load_game, save_game
from loader_functions.initialize_new_game import get_constants, get_game_variables
from menus import main_menu, message_box
from render_functions import clear_all, render_all

def main():
    consts = get_constants()

    tcod.console_set_custom_font('consolas10x10_gs_tc.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)
    tcod.console_init_root(consts['scrn_width'], consts['scrn_height'], consts['window_title'], False)
    con = tcod.console_new(consts['scrn_width'], consts['scrn_height'])
    panel = tcod.console_new(consts['scrn_width'], consts['panel_height'])

    player = None
    entities = []
    game_map = None
    message_log = None
    game_state = None

    show_main_menu = True
    show_load_err_msg = False

    key = tcod.Key()
    mouse = tcod.Mouse()

    while not tcod.console_is_window_closed():
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse)
        if show_main_menu:
            main_menu(con, consts['scrn_width'], consts['scrn_height'])

            if show_load_err_msg:
                message_box(con, 'No save game to load', 50, consts['scrn_width'], consts['scrn_height'])
            
            tcod.console_flush()

            action = handle_main_menu(key)
            new_game = action.get('new_game')
            load_save = action.get('load_game')
            exit_game = action.get('exit')

            if show_load_err_msg and (new_game or load_save or exit_game):
                show_load_err_msg = False
            elif new_game:
                player, entities, game_map, message_log, game_state = get_game_variables(consts)
                game_state = GameStates.PLAYER_TURN
                show_main_menu = False
            elif load_save:
                try:
                    player, entities, game_map, message_log, game_state = load_game()
                    show_main_menu = False
                except FileNotFoundError:
                    show_load_err_msg = True
            elif exit_game:
                break
        else:
            tcod.console_clear(con)
            play_game(player, entities, game_map, message_log, game_state, con, panel, consts)
            show_main_menu = True


def play_game(player, entities, game_map, message_log, game_state, con, panel, consts):
    # FoV
    fov_recompute = True
    fov_map = initialize_fov(game_map)

    # Input
    key = tcod.Key()
    mouse = tcod.Mouse()
    
    # Game state
    prev_game_state = game_state

    # Targeting
    targeting_item = None

# Main Gameplay Loop
    while not tcod.console_is_window_closed():
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse)
        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, consts['fov_radius'], consts['fov_light_walls'], consts['fov_algo'])
        render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log, 
                consts['scrn_width'], consts['scrn_height'], consts['bar_width'], consts['panel_height'],
                consts['panel_y'], mouse, consts['colors'], game_state)
        fov_recompute = False
        tcod.console_flush()

        clear_all(con, entities)
        
        action = handle_keys(key, game_state)
        mouse_action = handle_mouse(mouse)

        move = action.get('move')
        wait = action.get('wait')
        pickup = action.get('pickup')
        show_inventory = action.get('show_inventory')
        drop_inventory = action.get('drop_inventory')
        inventory_index = action.get('inventory_index')
        descend_stairs = action.get('descend_stairs')
        level_up = action.get('level_up')
        ext = action.get('exit')
        fullscreen = action.get('fullscreen')

        left_click = mouse_action.get('left_click')
        right_click = mouse_action.get('right_click')

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
        
        if pickup and game_state == GameStates.PLAYER_TURN:
            for entity in entities:
                if entity.item and entity.x == player.x and entity.y == player.y:
                    pickup_results = player.inventory.add_item(entity)
                    player_turn_results.extend(pickup_results)
                    break
            else:
                message_log.add_message(Message('There is nothing to pickup.', tcod.yellow))

        if wait:
            game_state = GameStates.ENEMY_TURN

        if show_inventory:
            prev_game_state = game_state
            game_state = GameStates.SHOW_INVENTORY
        
        if drop_inventory:
            prev_game_state = game_state
            game_state = GameStates.DROP_INVENTORY

        if inventory_index is not None and prev_game_state != GameStates.PLAYER_DEAD and inventory_index < len(player.inventory.items):
            item = player.inventory.items[inventory_index]

            if game_state == GameStates.SHOW_INVENTORY:
                player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map))
            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop(item))

        if descend_stairs and game_state == GameStates.PLAYER_TURN:
            for entity in entities:
                if entity.stairs and player.on_top_entity(entity):
                    entities = game_map.next_floor(player, message_log, consts)
                    fov_map = initialize_fov(game_map)
                    fov_recompute = True
                    tcod.console_clear(con)
                    break
            else:
                message_log.add_message(Message('There are no stairs here.', tcod.yellow))

        if level_up:
            player.fighter.level_up(level_up)
            game_state = prev_game_state

        if game_state == GameStates.TARGETING:
            if left_click:
                target_x, target_y = left_click
                item_use_results = player.inventory.use(targeting_item, entities=entities, fov_map=fov_map,
                                                        target_x=target_x, target_y=target_y)
                player_turn_results.extend(item_use_results)
            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})

        if ext:
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
                game_state = prev_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({'targeting_cancelled': True})
            else:
                save_game(player, entities, game_map, message_log, game_state)
                return True
        
        if fullscreen:
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())
        
        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            item_consumed = player_turn_result.get('consumed')
            item_dropped = player_turn_result.get('item_dropped')
            targeting = player_turn_result.get('targeting')
            targeting_cancelled = player_turn_result.get('targeting_cancelled')
            xp = player_turn_result.get('xp')

            if message:
                message_log.add_message(message)
            
            if targeting_cancelled:
                game_state = prev_game_state
                message_log.add_message(Message('Targeting cancelled'))

            if xp:
                leveled_up = player.level.add_xp(xp)
                message_log.add_message(Message('You gain {0} experience points!'.format(xp)))
                if leveled_up:
                    message_log.add_message(Message('You Leveled Up to Level {0}!'.format(player.level.curr_lvl,
                                            tcod.green)))
                    prev_game_state = game_state
                    game_state = GameStates.LEVEL_UP

            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)
                message_log.add_message(message)

            if item_added:
                entities.remove(item_added)
                game_state = GameStates.ENEMY_TURN
            
            if item_consumed:
                game_state = GameStates.ENEMY_TURN
            
            if targeting:
                prev_game_state = GameStates.PLAYER_TURN
                game_state = GameStates.TARGETING
                targeting_item = targeting
                message_log.add_message(targeting_item.item.targeting_message)
            
            if item_dropped:
                entities.append(item_dropped)
                game_state = GameStates.ENEMY_TURN
        
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