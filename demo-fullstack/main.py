from backend.utils.utils import *
from backend.utils.json_utils import *
from backend.utils.frontend_utils import *
from backend.utils.generate_actions_utils import *
from backend.utils.generate_blocks_utils import *
from backend.utils.generate_locations_utils import *
from backend.utils.generate_characters_utils import *
from backend.utils.generate_items_utils import *
from backend.utils.generate_game_json import *    


characters = read_json_examples("data/test_generations/all_the_characters.json")
locations = read_json_examples("data/test_generations/all_the_locations.json")
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

dict_to_json_file(game_dict, "data/test_generations/game.json")
print("\nGenerated the entire game json! ^v^\n")