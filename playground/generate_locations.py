# TODO: 5-shot prompt all models
# TODO: can we have a separate function for verifying the JSON format, and regenerate (with an enhanced prompt?)?
"""
Playground for location generation
"""
import json
from random import randint
from openai import OpenAI

direction_mappings = {"up" : "down",
                      "down" : "up",
                      "in": "out",
                      "out": "in",
                      "east": "west",
                      "west": "east",
                      "north": "south",
                      "south": "north"}

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
    with open(filepath, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)     

def extract_keys_from_list(list_json_objs, key):
    to_return = []
    for json_obj in list_json_objs:
        to_return.append(json_obj[key])
    return to_return


def generate_new_location(story, examples):
    def create_shot():
        return
    client = OpenAI()
    sys_prompt = """You are a helpful location generator for building a text adventure game.
Given the background story of the game from the user, what you do think the central location of the game should be?
Give the name and description for the location in a JSON, formatted like the examples below:
"""
    for ex in examples:
        sys_prompt += json.dumps(ex)
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": story},
        ]
    )
    model_output = completion.choices[0].message.content
    model_output_dict = json.loads(model_output)
    dict_to_json_file(model_output_dict, "test_generations/init_location.json")
    return model_output_dict

def generate_neighboring_locations(existing_locs, n, orig_loc_dict, story, example, example_loc_dict, example_story):
    # TODO: separate the n out to be in the user prompt
    def create_shot():
        return
    client = OpenAI()
    sys_prompt = f"""You are a helpful location generator for building a text adventure game.
Given the background story of the game, a location that is already in the game, and the number of neighboring locations to generate from the user,
generate logical neighboring locations of the location given and output as a list of JSON objects.
The locations that already exist in the game are: {existing_locs}. DO NOT generate locations that have the same name or a similar name as an existing location.
"""
    user_prompt = f"""Background story: {story}
Location to generate neighboring locations for:
"""
    user_prompt += json.dumps(orig_loc_dict)
    user_prompt += f"Number of neighboring locations to generate: {n}"
    user_prompt_shot_1 = f"""Background story: {example_story}
Location to generate neighboring locations for:
"""
    user_prompt_shot_1 += json.dumps(example_loc_dict)
    user_prompt_shot_1 += "Number of neighboring locations to generate: 3"
    user_prompt_shot_2 = f"""Background story: {example_story}
Location to generate neighboring locations for:
"""
    user_prompt_shot_2 += json.dumps(example_loc_dict)
    user_prompt_shot_2 += "Number of neighboring locations to generate: 2"

    # TODO: break down few-shot prompts
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt_shot_1},
            {"role": "assistant", "content": json.dumps(example)},
            {"role": "user", "content": user_prompt_shot_2},
            {"role": "assistant", "content": json.dumps(example[:2])},
            {"role": "user", "content": user_prompt}
        ]
    )
    model_output = completion.choices[0].message.content
    model_output_list = json.loads(model_output)
    dict_to_json_file(model_output_list, "test_generations/neighbor_locations.json")
    return model_output_list

def generate_connections(loc1, loc2, dirs):
    def create_shot():
        return
    loc1_name, loc2_name = loc1["name"], loc2["name"]
    client = OpenAI()
    sys_prompt = f"""You are a helpful map generator for building a text adventure game.
Now, given the name and description of two locations (the first one is location 1, the second one is location 2)
from the user, determine which direction (pick from THIS LIST: {dirs}) the player should go to get from location 1 to location 2.
DO NOT pick a direction that is not in the list.
Pick the direction that is the most logically coherent with the location descriptions.
Output the direction and a description of how the player moves from location 1 to location 2 as a JSON object.
Then, generate another description of how the player moves from location 2 to location 1 (i.e. in the opposite ).
Output the direction and description of how the player moves from location 2 to location 1 as a JSON object as well.
Therefore, your output should be a list of 2 JSON objects in a format like this:
[{{"direction": "down", "travel description": "Descending the stairs from the Hall of the Goddess, you move towards the Royal Tomb, the air growing cooler and heavier with the weight of centuries."}},
{{"direction": "up", "travel description": "Ascending the stairs from the depths of the Royal Tomb, you journey back towards the Hall of the Goddess. With each step upwards, the air becomes lighter and warmer, shedding the cool, heavy presence of ancient history. The atmosphere subtly shifts, as if leaving behind the echoes of the past to embrace the divine serenity of the Goddess's hall."}}]
"""
    user_prompt = json.dumps(loc1) + json.dumps(loc2)
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
    model_output = completion.choices[0].message.content
    model_output_list = json.loads(model_output)
    direction1, desc1 = model_output_list[0]["direction"].strip(), model_output_list[0]["travel description"]
    direction2, desc2 = model_output_list[1]["direction"].strip(), model_output_list[1]["travel description"]
    if direction_mappings[direction1] != direction2:
        print(direction1, direction2)
    loc1["connections"][direction1] = loc2_name
    loc2["connections"][direction_mappings[direction1]] = loc1_name
    loc1["travel_descriptions"][direction1] = desc1
    loc2["travel_descriptions"][direction_mappings[direction1]] = desc2
    return loc1, loc2, direction1


def main():
    story_desc = read_file_to_str("data/story-cyberpunk.txt")
    location_init_examples = read_json_examples("data/locations-name-desc-3.json")
    location_init_example_story = read_file_to_str("data/story-insidetemple.txt")
    location_neib_prompt_example = read_json_examples("data/location-name-desc-1.json")
    # loc_center = generate_new_location(story_desc, location_init_examples)
    # num_locs = randint(3, 8)
    # print("Number of neighboring locations: ", num_locs)
    # neib_locs = generate_neighboring_locations(num_locs, loc_center, story_desc,
    #                                            location_init_examples, location_neib_prompt_example, location_init_example_story)
    # directions = ["east", "west", "north", "south", "up", "down", "in", "out"]
    # for i in range(len(neib_locs)):
    #     loc_center, neib_locs[i], dir_take_out = generate_connections(loc_center, neib_locs[i], directions)
    #     directions.remove(dir_take_out)
    #     print("Took out ", dir_take_out, " | list now: ", directions)
    # TODO: read from previously generated json
    neib_locs = read_json_examples("test_generations/locations_first_round_8.json")
    all_locs = neib_locs
    # Do another round of location gen for all first-round locations (except the central)
    for j in range(len(neib_locs[:7])):
        num_locs = randint(0, 3)
        print("Number of neighboring locations: ", num_locs)
        if num_locs == 0:
            continue
        existing_loc_names = extract_keys_from_list(all_locs, "name")
        neib_neib_locs = generate_neighboring_locations(existing_loc_names, num_locs, neib_locs[j], story_desc,
                                                        location_init_examples, location_neib_prompt_example, location_init_example_story)
        directions = ["east", "west", "north", "south", "up", "down", "in", "out"]
        # generate connections for each of these neighboring connections
        for k in range(len(neib_neib_locs)):
            neib_locs[j], neib_neib_locs[k], dir_take_out = generate_connections(neib_locs[j], neib_neib_locs[k], directions)
            print("direction linked: ", dir_take_out)
            directions.remove(dir_take_out)
            print("Took out ", dir_take_out, " | list now: ", directions)
        all_locs += neib_neib_locs

    # all_locs.append(loc_center)
    list_to_json_file(all_locs, "test_generations/locations.json")



if __name__ == "__main__":
    main()
