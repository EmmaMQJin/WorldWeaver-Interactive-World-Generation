from generate_characters_utils import *
from generate_items_utils import *
from generate_locations_utils import *
from generate_actions_utils import *
from generate_game_class import *
from generate_blocks_utils import *
from utils import *
import copy
import json
from gpt_parser import GptParser
from worldweaver import *
from copy import deepcopy
from text_adventure_games import games

# TODO: Maybe show the neighbor locations and items to the player (make it editable)
# TODO: Maybe can evaluate what the user prefers vs. what the model prefers

def main():
#     story_cyberpunk = read_file_to_str("data/story-cyberpunk.txt")
#     story_insidetemple = read_file_to_str("data/story-insidetemple.txt")
#     story_lake = read_file_to_str("data/story-lake.txt")

#     location_format = read_json_examples(
#         "data/location-empty.json")

#     stories = [story_cyberpunk, story_insidetemple]
#     with open("data/few-shot-examples/example-characters.json", 'r') as file:
#         example_characters = json.load(file)
#     character_format = read_file_to_str("data/character-empty.json")

#     central_loc_lake_obj = read_json_examples(
#         "data/few-shot-examples/central-loc-lake.json")
#     neib_locs_lake_5_list = read_json_examples(
#         "data/few-shot-examples/neighb-locs-lake-5.json")
#     central_loc_insidetemple_obj = read_json_examples(
#         "data/few-shot-examples/central-loc-insidetemple.json")
#     neib_locs_insidetemple_3_list = read_json_examples(
#         "data/few-shot-examples/neighb-locs-insidetemple-3.json")
    
#     hall_of_goddess_obj = read_json_examples("data/few-shot-examples/hall-of-goddess.json")
#     royal_tomb_obj = read_json_examples("data/few-shot-examples/royal-tomb.json")

#     # few-shot for central location format
#     central_loc_shot_1 = create_new_location_shot(story_insidetemple, central_loc_insidetemple_obj)
#     central_loc_shot_2 = create_new_location_shot(story_lake, central_loc_lake_obj)
#     central_loc_shots = central_loc_shot_1 + central_loc_shot_2

#     # few-shot for neighboring locations
#     neib_locs_shot_1 = create_neib_locs_shot(
#         central_loc_insidetemple_obj, story_insidetemple, 1, neib_locs_insidetemple_3_list[:1])
#     neib_locs_shot_2 = create_neib_locs_shot(
#         central_loc_insidetemple_obj, story_insidetemple, 3, neib_locs_insidetemple_3_list)
#     neib_locs_shot_3 = create_neib_locs_shot(
#         central_loc_lake_obj, story_lake, 5, neib_locs_lake_5_list)
#     neib_locs_shots = neib_locs_shot_1 + neib_locs_shot_2 + neib_locs_shot_3

#     # few-shot for connections
#     hall_tomb_connection = [{"direction": "down",
#                              "travel description": "Descending the stairs from the Hall of the Goddess, you move towards the Royal Tomb, the air growing cooler and heavier with the weight of centuries."},
#                             {"direction": "up",
#                              "travel description": "Ascending the stairs from the depths of the Royal Tomb, you journey back towards the Hall of the Goddess. With each step upwards, the air becomes lighter and warmer, shedding the cool, heavy presence of ancient history. The atmosphere subtly shifts, as if leaving behind the echoes of the past to embrace the divine serenity of the Goddess's hall."}]
#     connections_shot_1 = create_connections_shot(hall_of_goddess_obj, royal_tomb_obj, hall_tomb_connection)
#     connections_shots = connections_shot_1

#     print("------------------------Welcome to WorldWeaver!-----------------------")

#     background_story = input("\nPlease give a description of the game you want to build.\ne.g. I want to build a fairy tale with a talking cat.\n")
#     print("\nOK, generating the main character for your game... ...\n")
#     main_character = generate_main_character(background_story, stories, character_format, example_characters)
#     print("\nHere is your main character, who is also your player: \n\n")
#     print("-------Main Character-------")
#     print(main_character["name"])
#     print()
#     print(main_character["description"])
#     print("----------------------------")
#     # all_characters = [main_character]
#     initial_state = input("\nWhat do you want the starting state of the game to be?\n(This could be something like: the main character wakes up in a cave.)\n")
#     print("\nOK. The starting state of the game will be: ", initial_state)
#     winning_state = input("\nWhat do you want the winning state of the game to be?\n(This could be something like: the main character saves the poisoned princess.)\n")
#     print("\nOK. The winning state of the game will be: ", winning_state)
#     actions_list = generate_actions_playthrough(background_story, main_character, initial_state, winning_state)
#     write_list_to_file(actions_list.strip().split("\n"), "data/actions.txt")
#     locations_to_use = generate_locations_to_use(background_story, actions_list, initial_state, winning_state, main_character)
#     remaining_locations = copy.deepcopy(locations_to_use)
#     dict_to_json_file(locations_to_use, "test.json")
#     print(f"\nThe number of locations that will be generated is {len(locations_to_use)}.\n")
#     num_locs = len(locations_to_use)
#     print("\nNow, let's generate the starting location of the game!\n")
#     remaining_locations = generate_central_loc_HITL(background_story, neib_locs_insidetemple_3_list[0], central_loc_shots, remaining_locations)
#     central_loc = read_json_examples("data/test_generations/init_location.json")
#     print("\nOK, here is the generated central location:\n")
#     print("-------Starting Location-------")
#     print(central_loc["name"])
#     print()
#     print(central_loc["description"])
#     print("-------------------------------")
#     main_character["location"] = central_loc["name"]
#     all_characters = [main_character]
#     print("\nGenerating the entire map......\n")
#     generate_neighbor_locs_HITL(central_loc, background_story, neib_locs_shots, connections_shots, remaining_locations, location_format)
#     print("\nLocation generation completed! ^v^\n")
#     print("Now, let's populate each location with NPCs\n")
#     all_locations = read_json_examples("data/test_generations/all_the_locations.json")
#     for i, location_json in enumerate(all_locations):
#         name = location_json["name"]
#         if name not in locations_to_use:
#             continue
#         purpose = locations_to_use[name]
#         print(f"\nLet's generate NPCs in the location {name}... ...")
#         npcs_dict, all_characters = generate_npc_in_location(name, location_json["description"], purpose, background_story, main_character, all_characters)
#         all_locations[i]["characters"] = npcs_dict
#     dict_to_json_file(all_locations, "data/test_generations/all_the_locations.json")
#     dict_to_json_file(all_characters, "data/test_generations/all_the_characters.json")
#     print("\nNPC generation completed! ^v^\n")
#     # #Object generation based on the generated location json
#     print("\nLastly, let's populate generate the objects in each location and each character's inventory!\n")
#     print("\nGenerating objects in each location......\n")
#     generate_objects_in_locations("games-data")
#     print("\nPopulating character inventories......\n")
#     populate_character_inventories("games-data", main_character, winning_state)


# #     background_story = "I want to build a gma with a pigeon in costco"
# #     actions_list = """ Enter Costco
# # Dodge eager shoppers
# # Find bakery aisle
# # Spot bread buds
# # Avoid security guards
# # Grab bread buds
# # Navigate to exit
# # Evade final security guard
# # Exit Costco"""
#     #Block Generation
#     print("\nGenerating Blocks in the game......\n")
#     all_locations_path = "data/test_generations/all_the_locations.json"
#     generate_blocks(background_story, actions_list,all_locations_path)
#     input_file_path = 'data/generated_blocks.py'  # Path to the file containing the block classes
#     output_file_path = 'data/extracted_block_classes.py'  # Path to save the extracted block classes
#     extract_block_classes(input_file_path, output_file_path)
#     blocks_file_path = 'data/generated_blocks.py'
#     locations_json_path = "data/test_generations/all_the_locations.json"
#     output_json_path = 'data/test_generations/all_the_locations.json'
#     integrate_blocks(locations_json_path, blocks_file_path, output_json_path)

#     print("\nGenerating the entire game JSON... ...\n")
#     characters = read_json_examples("data/test_generations/all_the_characters.json")
#     locations = read_json_examples("data/test_generations/all_the_locations.json")
#     main_char_name = characters[0]["name"]
#     starting_location_name = characters[0]["location"]

#     game_dict = {}
#     game_dict["player"] = main_char_name
#     game_dict["start_at"] = starting_location_name
#     game_dict["game_history"] = []
#     game_dict["game_over"] = False
#     game_dict["game_over_description"] = None
#     game_dict["characters"] = characters
#     game_dict["locations"] = locations
#     game_dict["actions"] = []

#     dict_to_json_file(game_dict, "data/test_generations/game.json")
#     print("\nGenerated the entire game json! ^v^\n")

#     generate_action_class(actions_list)
#     generate_game_class(winning_state, characters[0])

    with open('data/test_generations/game.json') as f:
        data = json.load(f)

    data_obj = WorldWeaver.from_primitive(deepcopy(data), custom_actions=[Enter, Dodge, Find], custom_blocks=[CostcoEntranceEastBlock, ProduceAisleOutBlock, SecurityGuardStationEastBlock, BakeryAisleWestBlock, CheckoutLaneEastBlock, CostcoExitSouthBlock])
    parser = GptParser(data_obj, verbose=False)
    data_obj.set_parser(parser)
    data_obj.game_loop()

if __name__ == "__main__":
    main()