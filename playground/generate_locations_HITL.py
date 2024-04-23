from generate_locations_utils import *
import tempfile
import subprocess
import os

# TODO: add feature such that user can specify what categories of locations to include
# e.g. shops, bars, etc.
# have an existence flag for each category? If flag is still false, augment prompt with that category

def open_vim_with_string(text):
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as temp_file:
        temp_file.write(text)
    subprocess.run(['vim', temp_file.name])

    with open(temp_file.name, 'r') as edited_file:
        edited_text = edited_file.read()
    os.unlink(temp_file.name)

    return edited_text

def open_vim_with_json(json_data):
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
        json.dump(json_data, temp_file, indent=4)
        temp_file.flush()
    subprocess.run(['vim', temp_file.name])
    with open(temp_file.name, 'r') as edited_file:
        try:
            edited_json = json.load(edited_file)
        except json.JSONDecodeError:
            print("Edited data is not valid JSON.")
            return None
    os.unlink(temp_file.name)
    return edited_json

def generate_central_loc_HITL(desc, example, central_loc_shots):
    # generate central location with user input
    central_loc_desc = input("Do you have any thoughts on what the central location is like?\n")
    all_descs = desc
    if central_loc_desc:
        all_descs += "\nAbout the central location of the game: " + central_loc_desc
    loc_center = generate_new_location(all_descs, example, central_loc_shots)
    
    # get feedback from user about central location
    # input("OK, here is the generated central location:")
    # new_name = open_vim_with_string(loc_center["name"])
    # print("Edited name: ", new_name)
    # new_desc = open_vim_with_string(loc_center["description"])
    # print("Edited description: ", new_desc)
    # loc_center["name"] = new_name
    # loc_center["description"] = new_desc

    dict_to_json_file(loc_center, "data/test_generations/init_location.json")

# TODO:
def generate_neighbor_locs_HITL(all_locs, num_neib_locs, orig_loc_dict, story, neib_shots, connections_shots):
    # A
    # B    C     D
    # EF   GH
    prev_layer = all_locs[:]
    while num_neib_locs > 0:
        temp_layer = []
        for j, loc in enumerate(prev_layer):
            if num_neib_locs == 0:
                break
            if num_neib_locs <= 4:
                n = num_neib_locs
            else:
                n = randint(2, 4)
            print("Number of neighboring locations: ", n)
            neib_locs = generate_neighboring_locations(
                all_locs, n, loc, story, neib_shots)
            # Generate connections
            directions = ["east", "west", "north", "south", "up", "down", "in", "out"]
            for k, _ in enumerate(neib_locs):
                prev_layer[j], neib_locs[k], dir_take_out = generate_connections(
                    prev_layer[j], neib_locs[k], directions, connections_shots)
                print("direction linked: ", dir_take_out)
                directions.remove(dir_take_out)
                print("Took out ", dir_take_out, " | list now: ", directions)
            all_locs += neib_locs[:]
            temp_layer += neib_locs[:]
            num_neib_locs -= n
        print("all locs 1: ", all_locs)
        prev_layer = temp_layer[:]
    print("all locs 2: ", all_locs)
    list_to_json_file(all_locs, "test_generations/all_the_locations.json")


def main():
    story_cyberpunk = read_file_to_str("data/story-cyberpunk.txt")
    story_insidetemple = read_file_to_str("data/story-insidetemple.txt")
    story_lake = read_file_to_str("data/story-lake.txt")

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

    print("Welcome to WorldWeaver!")

    # desc = input("Please give a description of the type of game you want to build.\n")

    choice = input("Would you like to start with generating locations or characters for your game?\n")

    if choice.lower() == "location":
        # generate central location
        generate_central_loc_HITL(story_cyberpunk, neib_locs_insidetemple_3_list[0], central_loc_shots)
        central_loc = read_json_examples("data/test_generations/init_location.json")
        # generate neighboring locations
        num_locs = int(input("How many locations would you like to have in the game?\n"))
        generate_neighbor_locs_HITL([central_loc], num_locs-1, central_loc, story_cyberpunk, neib_locs_shots, connections_shots)
        # generate connections




if __name__ == "__main__":
    main()