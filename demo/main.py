from utils.generate_characters_utils import *
from utils.generate_items_utils import *
from utils.generate_locations_utils import *
from utils.utils import *
import copy

def main():
    story_cyberpunk = read_file_to_str("data/story-cyberpunk.txt")
    story_insidetemple = read_file_to_str("data/story-insidetemple.txt")
    story_lake = read_file_to_str("data/story-lake.txt")

    location_format = read_json_examples(
        "data/location-empty.json")

    stories = [story_cyberpunk, story_insidetemple]
    with open("data/few-shot-examples/example-characters.json", 'r') as file:
        example_characters = json.load(file)
    character_format = read_file_to_str("data/character-empty.json")

    central_loc_lake_obj = read_json_examples(
        "data/few-shot-examples/central-loc-lake.json")
    neib_locs_lake_5_list = read_json_examples(
        "data/few-shot-examples/neighb-locs-lake-5.json")
    central_loc_insidetemple_obj = read_json_examples(
        "data/few-shot-examples/central-loc-insidetemple.json")
    neib_locs_insidetemple_3_list = read_json_examples(
        "data/few-shot-examples/neighb-locs-insidetemple-3.json")
    
    hall_of_goddess_obj = read_json_examples("data/few-shot-examples/hall-of-goddess.json")
    royal_tomb_obj = read_json_examples("data/few-shot-examples/royal-tomb.json")

    # few-shot for central location format
    central_loc_shot_1 = create_new_location_shot(story_insidetemple, central_loc_insidetemple_obj)
    central_loc_shot_2 = create_new_location_shot(story_lake, central_loc_lake_obj)
    central_loc_shots = central_loc_shot_1 + central_loc_shot_2

    # few-shot for neighboring locations
    neib_locs_shot_1 = create_neib_locs_shot(
        central_loc_insidetemple_obj, story_insidetemple, 1, neib_locs_insidetemple_3_list[:1])
    neib_locs_shot_2 = create_neib_locs_shot(
        central_loc_insidetemple_obj, story_insidetemple, 3, neib_locs_insidetemple_3_list)
    neib_locs_shot_3 = create_neib_locs_shot(
        central_loc_lake_obj, story_lake, 5, neib_locs_lake_5_list)
    neib_locs_shots = neib_locs_shot_1 + neib_locs_shot_2 + neib_locs_shot_3

    # few-shot for connections
    hall_tomb_connection = [{"direction": "down",
                             "travel description": "Descending the stairs from the Hall of the Goddess, you move towards the Royal Tomb, the air growing cooler and heavier with the weight of centuries."},
                            {"direction": "up",
                             "travel description": "Ascending the stairs from the depths of the Royal Tomb, you journey back towards the Hall of the Goddess. With each step upwards, the air becomes lighter and warmer, shedding the cool, heavy presence of ancient history. The atmosphere subtly shifts, as if leaving behind the echoes of the past to embrace the divine serenity of the Goddess's hall."}]
    connections_shot_1 = create_connections_shot(hall_of_goddess_obj, royal_tomb_obj, hall_tomb_connection)
    connections_shots = connections_shot_1

    print("Welcome to WorldWeaver!!!!")

    background_story = input("\nPlease give a description of the type of game you want to build.\n")

    main_character = generate_main_character(background_story, stories, character_format, example_characters)
    print("\nHere is your main character, who is also your player: \n", json.dumps(main_character))
    all_characters = [main_character]
    initial_state = input("\nWhat do you want the initial state of the game to be?\n")
    print("OK. The initial state of the game will be: ", initial_state)
    winning_state = input("\nWhat do you want the winning state of the game to be?\n")
    print("OK. The winning state of the game will be: ", winning_state)
    actions_list = generate_actions_playthrough(background_story, initial_state, winning_state)
    locations_to_use = generate_locations_to_use(background_story, actions_list)
    remaining_locations = copy.deepcopy(locations_to_use)
    dict_to_json_file(locations_to_use, "test.json")
    num_locs = int(input(f"\nThe number of locations available is {len(locations_to_use)}. How many locations would you like to have in the game?\n"))
    remaining_locations = generate_central_loc_HITL(background_story, neib_locs_insidetemple_3_list[0], central_loc_shots, remaining_locations)
    central_loc = read_json_examples("data/test_generations/init_location.json")
    print("\nOK, here is the generated central location:\n")
    print(json.dumps(central_loc))
    generate_neighbor_locs_HITL(num_locs-1, central_loc, background_story, neib_locs_shots, connections_shots, remaining_locations, location_format)

    all_locations = read_json_examples("data/test_generations/all_the_locations.json")
    print("read all locations of length", len(all_locations))
    print("locations to use:", locations_to_use)
    for i, location_json in enumerate(all_locations):
        name = location_json["name"]
        print("location name:", name)
        if name not in locations_to_use:
            continue
        purpose = locations_to_use[name]
        # location_name, location_purpose, background_story, main_character, character_format, stories, all_characters
        npcs_dict, all_characters = generate_npc_in_location(name, purpose, background_story, main_character, character_format, stories, all_characters)
        all_locations[i]["characters"] = npcs_dict
    dict_to_json_file(all_locations, "data/test_generations/all_the_locations.json")
    dict_to_json_file(all_characters, "data/test_generations/all_the_characters.json")

    # #Object generation based on the generated location json
    # generate_object("games-data")

    

if __name__ == "__main__":
    main()