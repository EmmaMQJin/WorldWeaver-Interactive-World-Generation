from json_utils import *

import copy

characters = read_json_examples("../data/test_generations/all_the_characters.json")
locations = read_json_examples("../data/test_generations/all_the_locations.json")

main_char_name = characters[0]["name"]
starting_location_name = characters[0]["location"]

game_dict = {}
game_dict["player"] = main_char_name
game_dict["start_at"] = starting_location_name
game_dict["game_history"] = []
game_dict["game_over"] = False
game_dict["game_over_description"] = None
game_dict["characters"] = characters
game_dict["locations"] = locations
game_dict["actions"] = []

dict_to_json_file(game_dict, "../data/test_generations/game.json")
