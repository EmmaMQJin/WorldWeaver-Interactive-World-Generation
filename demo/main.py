from utils.generate_characters_utils import *
from utils.generate_items_utils import *
from utils.generate_locations_utils import *

def main():
    story_cyberpunk = read_file_to_str("data/story-cyberpunk.txt")
    story_insidetemple = read_file_to_str("data/story-insidetemple.txt")
    story_lake = read_file_to_str("data/story-lake.txt")

    stories = [story_cyberpunk, story_insidetemple]
    with open("data/few-shot-examples/example-character.json", 'r') as file:
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

    background_story = input("Please give a description of the type of game you want to build.\n")

    main_character = generate_main_character(background_story, stories, character_format, example_characters)
    print("Here is your main character, which is also your player: \n", json.dumps(main_character))

    winning_state = input("What do you want the winning state of the game to be?")
    print("winning state is: ", winning_state)
    # TODO: ask GPT to output a one-sentence goal of main character given json obj and winning_state
    generate_central_loc_HITL(background_story, neib_locs_insidetemple_3_list[0], central_loc_shots, main_character, winning_state)
    central_loc = read_json_examples("data/test_generations/init_location.json")

    num_locs = int(input("How many locations would you like to have in the game?\n"))
    generate_neighbor_locs_HITL([central_loc], num_locs-1, central_loc, background_story, neib_locs_shots, connections_shots)

    # TODO: loop through all locations to generate npcs
    npcs = generate_npc(background_story, stories, character_format)
    print(npcs)

    

if __name__ == "__main__":
    main()