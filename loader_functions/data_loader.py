import os
import pickle

def save_game(player, entities, game_map, message_log, game_state):
    data  = dict()
    data['player_index'] = entities.index(player)
    data['entities'] = entities
    data['game_map'] = game_map
    data['msg_log'] = message_log
    data['game_state'] = game_state
    with open('save_game.pkl', 'wb') as f:
        pickle.dump(data, f)

def load_game():
    if not os.path.isfile('save_game.pkl'):
        raise FileNotFoundError
    
    with open('save_game.pkl', 'rb') as f:
        data = pickle.load(f)
    
    entities = data['entities']
    player = entities[data['player_index']]
    game_map = data['game_map']
    message_log = data['msg_log']
    game_state = data['game_state']

    return player, entities, game_map, message_log, game_state