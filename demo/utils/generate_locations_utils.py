import json
from random import randint
from openai import OpenAI
import tempfile
import subprocess
import os

direction_mappings = {"up": "down",
                      "down": "up",
                      "in": "out",
                      "out": "in",
                      "east": "west",
                      "west": "east",
                      "north": "south",
                      "south": "north"}

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

def generate_central_loc_HITL(desc, example, central_loc_shots, main_character, winning_state):
    # generate central location with user input
    central_loc_desc = input("Do you have any thoughts on what the central location is like?\n")
    all_descs = desc
    if central_loc_desc:
        all_descs += "\nAbout the central location of the game: " + central_loc_desc
    loc_center = generate_new_location(all_descs, example, central_loc_shots, main_character, winning_state)
    
    # get feedback from user about central location
    print("OK, here is the generated central location:")
    new_name = open_vim_with_string(loc_center["name"])
    print("Edited name: ", new_name)
    new_desc = open_vim_with_string(loc_center["description"])
    print("Edited description: ", new_desc)
    loc_center["name"] = new_name
    loc_center["description"] = new_desc

    dict_to_json_file(loc_center, "data/test_generations/init_location.json")

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
    list_to_json_file(all_locs, "data/test_generations/all_the_locations.json")

def read_file_to_str(filepath):
    to_return = ""
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        file.close()
    to_return = ''.join(lines)
    return to_return.strip()


def read_json_examples(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        example_jsons = json.load(file)
    return example_jsons


def dict_to_json_file(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)


def list_to_json_file(data, filepath):
    print("data before writing: ", data)
    print(type(data))
    for i, obj in enumerate(data):
        temp_path = f"data/test_generations/obj{i}.json"
        with open(temp_path, 'w') as tempfile:
            json.dump(obj, tempfile, indent=4)
        print(obj)
        print(type(obj))

    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)


def extract_keys_from_list(list_json_objs, key):
    to_return = []
    for json_obj in list_json_objs:
        to_return.append(json_obj[key])
    return to_return

def create_new_location_shot(story, output):
    user = {"role": "user", "content": story}
    assistant = {"role": "assistant", "content": json.dumps(output)}

    return [user, assistant]

def generate_new_location(story, example, shots, main_character, winning_state):
    client = OpenAI(base_url="https://oai.hconeai.com/v1", api_key=os.environ['HELICONE_API_KEY'])
    sys_prompt = f"""You are a helpful location generator for building a text adventure game.
The player (main character) of this game is {main_character}, and their goal is: {winning_state}.
Given the background story of the game from the user, what you do think the central location of the game should be?
Give the name and description for the location in a JSON, formatted like the examples below:
"""
    sys_prompt += json.dumps(example)
    messages = [{"role": "system", "content": sys_prompt}]
    messages += shots
    messages += [{"role": "user", "content": story}]
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    model_output = completion.choices[0].message.content
    model_output_dict = json.loads(model_output)
    dict_to_json_file(model_output_dict, "data/test_generations/init_location.json")
    return model_output_dict


def create_neib_locs_shot(orig_loc, story, n, output):
    user_prompt = f"""Background story: {story}
Location to generate neighboring locations for:
"""
    user_prompt += json.dumps(orig_loc)
    user_prompt += f"\nNumber of neighboring locations to generate: {n}"
    assistant_output = json.dumps(output)
    user = {"role": "user", "content": user_prompt}
    assistant = {"role": "assistant", "content": assistant_output}

    return [user, assistant]


def generate_neighboring_locations(existing_locs, n, orig_loc_dict, story, shots):
    client = OpenAI(base_url="https://oai.hconeai.com/v1", api_key=os.environ['HELICONE_API_KEY'])
    sys_prompt = f"""You are a helpful location generator for building a text adventure game.
Given the background story of the game, a location that is already in the game, and the number of neighboring locations to generate from the user,
generate logical neighboring locations of the location given and output as a list of JSON objects.
The locations that already exist in the game are: {existing_locs}. DO NOT generate locations that have the same name or a similar name as an existing location.
"""
    user_prompt = f"""Background story: {story}
Location to generate neighboring locations for:
"""
    user_prompt += json.dumps(orig_loc_dict)
    user_prompt += f"\nNumber of neighboring locations to generate: {n}"
    messages = [{"role": "system", "content": sys_prompt}]
    messages += shots
    messages += [{"role": "user", "content": user_prompt}]
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    model_output = completion.choices[0].message.content
    print(model_output)
    model_output_list = json.loads(model_output)
    dict_to_json_file(model_output_list,
                      "data/test_generations/neighbor_locations.json")
    return model_output_list


def create_connections_shot(loc1, loc2, output):
    user_prompt = json.dumps(loc1) + "\n" + json.dumps(loc2)
    user = {"role": "user", "content": user_prompt}
    assistant = {"role": "assistant", "content": json.dumps(output)}

    return [user, assistant]

def generate_connections(loc1, loc2, dirs, shots):
    loc1_name, loc2_name = loc1["name"], loc2["name"]
    client = OpenAI(base_url="https://oai.hconeai.com/v1", api_key=os.environ['HELICONE_API_KEY'])
    sys_prompt = f"""You are a helpful map generator for building a text adventure game.
Now, given the name and description of two locations (the first one is location 1, the second one is location 2)
from the user, determine which direction (pick from THIS LIST: {dirs}) the player should go to get from location 1 to location 2.
DO NOT pick a direction that is not in the list.
Pick the direction that is the most logically coherent with the location descriptions.
Output the direction and a description of how the player moves from location 1 to location 2 as a JSON object.
Then, generate another description of how the player moves from location 2 to location 1 (i.e. in the opposite ).
Output the direction and description of how the player moves from location 2 to location 1 as a JSON object as well.
Therefore, your output should be a list of 2 JSON objects, where each JSON object has the keys "direction" and "travel description".
Note that the values of the "direction" key of the 2 JSON objects should be opposite directions, such as "up" and "down", or "east" and "west".
"""
    user_prompt = json.dumps(loc1) + json.dumps(loc2)

    messages = [{"role": "system", "content": sys_prompt}]
    messages += shots
    messages += [{"role": "user", "content": user_prompt}]
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    model_output = completion.choices[0].message.content
    model_output_list = json.loads(model_output)
    direction1, desc1 = model_output_list[0]["direction"].strip(
    ), model_output_list[0]["travel description"]
    direction2, desc2 = model_output_list[1]["direction"].strip(
    ), model_output_list[1]["travel description"]
    if direction_mappings[direction1] != direction2:
        print(direction1, direction2)
    loc1["connections"][direction1] = loc2_name
    loc2["connections"][direction_mappings[direction1]] = loc1_name
    loc1["travel_descriptions"][direction1] = desc1
    loc2["travel_descriptions"][direction_mappings[direction1]] = desc2
    return loc1, loc2, direction1


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



    # Generate the central location
    loc_center = generate_new_location(
        story_cyberpunk, neib_locs_insidetemple_3_list[0], central_loc_shots)
    print("Central location: ", loc_center)
    # Generate first-round of neighbors
    num_locs = randint(3, 7)
    print("Number of neighboring locations: ", num_locs)
    neib_locs = generate_neighboring_locations(
        [loc_center], num_locs, loc_center, story_cyberpunk, neib_locs_shots)

    # Generate connections for first-round of neighbors
    directions = ["east", "west", "north", "south", "up", "down", "in", "out"]
    for i, _ in enumerate(neib_locs):
        loc_center, neib_locs[i], dir_take_out = generate_connections(
            loc_center, neib_locs[i], directions, connections_shots)
        directions.remove(dir_take_out)
        print("Took out ", dir_take_out, " | list now: ", directions)

    # neib_locs = read_json_examples("test_generations/locations_first_round_8.json")
    all_locs = neib_locs + [loc_center]

    # Do another round of location gen for all first-round locations (except the central)
    for j, _ in enumerate(neib_locs):
        num_locs = randint(0, 3)
        print("Number of neighboring locations: ", num_locs)
        if num_locs == 0:
            continue
        existing_loc_names = extract_keys_from_list(all_locs, "name")
        neib_neib_locs = generate_neighboring_locations(existing_loc_names, num_locs, neib_locs[j], story_cyberpunk,
                                                        neib_locs_shots)
        directions = ["east", "west", "north",
                      "south", "up", "down", "in", "out"]
        # Generate connections for each of these neighboring connections
        for k, _ in enumerate(neib_neib_locs):
            neib_locs[j], neib_neib_locs[k], dir_take_out = generate_connections(
                neib_locs[j], neib_neib_locs[k], directions, connections_shots)
            print("direction linked: ", dir_take_out)
            directions.remove(dir_take_out)
            print("Took out ", dir_take_out, " | list now: ", directions)
        all_locs += neib_neib_locs

    # all_locs.append(loc_center)
    list_to_json_file(all_locs, "data/test_generations/locations.json")


if __name__ == "__main__":
    main()
