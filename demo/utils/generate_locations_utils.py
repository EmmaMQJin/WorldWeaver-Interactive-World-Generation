import json
from random import randint
from openai import OpenAI
import tiktoken
import os
from utils.json_utils import *

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

def generate_central_loc_HITL(desc, formatting_example, central_loc_shots, remaining_locations):
    user_prompt = desc
    user_prompt += "\nList of all locations in the game: " + json.dumps(remaining_locations)
    loc_center = pick_new_location(user_prompt, formatting_example, central_loc_shots)
    string_without_newline = loc_center["name"].replace('\n', '')
    del remaining_locations[string_without_newline] ## TODO - put a check here
    dict_to_json_file(loc_center, "data/test_generations/init_location.json")
    return remaining_locations

def generate_neighbor_locs_HITL(central_loc_dict, story, neib_shots, connections_shots, remaining_locations, format):
    # let the user pick layer by layer
    graph = {central_loc_dict["name"] : {}}
    prev_layer = [central_loc_dict]
    all_locs = [central_loc_dict]
    while len(remaining_locations) > 0:
        temp_layer = []
        for j, loc in enumerate(prev_layer):
            if len(remaining_locations) == 0:
                break
            if len(remaining_locations) <= 3:
                n =  len(remaining_locations)
            else:
                n = randint(1, 3)
            neib_locs, remaining_locations = pick_neighboring_locations(
                n, loc, story, neib_shots, remaining_locations, format)
            # Generate connections
            directions = ["east", "west", "north", "south", "up", "down", "in", "out"]
            for k, _ in enumerate(neib_locs):
                prev_layer[j], neib_locs[k], dir_take_out = generate_connections_step(
                    prev_layer[j], neib_locs[k], directions, connections_shots)

                directions.remove(dir_take_out)
            all_locs += neib_locs[:]
            temp_layer += neib_locs[:]
        prev_layer = temp_layer[:]
    list_to_json_file(all_locs, "data/test_generations/all_the_locations.json")


def create_new_location_shot(story, output):
    user = {"role": "user", "content": story}
    assistant = {"role": "assistant", "content": json.dumps(output)}

    return [user, assistant]

def pick_new_location(user_prompt, formatting_example, shots):
    client = OpenAI(base_url="https://oai.hconeai.com/v1", api_key=os.environ['HELICONE_API_KEY'])
    sys_prompt = f"""You are a helpful location generator for building a text adventure game.

The user will give you the background story of the game and a JSON of all locations that should be in the game.
The keys in the JSON are names of the locations, and the values are what the player needs to do in each location.
Your job is to choose the most logical starting location from the JSON, and generate the appropriate description for it.
The description of the location should focus on the background story of the location; don't mention what the user needs to do in the location at all.
You can mention what the location looks like and contains, but don't mention its neighboring locations at all.
Remember, you are CHOOSING a location from the JSON provided, not inventing a new one. The name of the location you choose should be
kept exactly the same as how it is in the JSON provided by the user.
Format your output like the example below:
{json.dumps(formatting_example)}
Remember to only populate the name, description, and set has_been_visited to false. Leave all values to the other keys empty.
"""
    messages = [{"role": "system", "content": sys_prompt}]
    messages += shots
    messages += [{"role": "user", "content": user_prompt}]
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
    user_prompt += f"\nNumber of neighboring locations to pick: {n}"
    assistant_output = json.dumps(output)
    user = {"role": "user", "content": user_prompt}
    assistant = {"role": "assistant", "content": assistant_output}

    return [user, assistant]


def pick_neighboring_locations(n, orig_loc_dict, story, shots, existing_locs, format):
            # neib_locs, remaining_locations = pick_neighboring_locations(
            #     loc, story, neib_shots, remaining_locations)
    client = OpenAI(base_url="https://oai.hconeai.com/v1", api_key=os.environ['HELICONE_API_KEY'])
    sys_prompt = f"""You are a helpful location generator for building a text adventure game.

The user will give you the background story of the game, the location to pick neighbors for, and the number of neighboring locations to pick.
Your job is to choose the most logical neighboring locations of the location given from this JSON: {json.dumps(existing_locs)}, and generate the appropriate descriptions for each neighboring location.
The description of each location should focus on the background story of the location; don't mention what the user needs to do in the location at all.
Remember, you are CHOOSING locations from the JSON above, not inventing new ones. The names of the locations you choose should be
kept exactly the same as how they are in the JSON above.
Output the neighbors as a list of JSON objects, where each JSON object is formatted as below:
{json.dumps(format)}
Remember to only populate the name, description, and set has_been_visited to false. Leave all values to the other keys empty.
"""
    user_prompt = f"""Background story: {story}
Location to generate neighboring locations for:
"""
    user_prompt += json.dumps(orig_loc_dict)
    user_prompt += f"\nNumber of neighboring locations to pick: {n}"
    messages = [{"role": "system", "content": sys_prompt}]
    messages += shots
    messages += [{"role": "user", "content": user_prompt}]
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    model_output = completion.choices[0].message.content
    model_output_list = json.loads(model_output)
    dict_to_json_file(model_output_list,
                      "data/test_generations/neighbor_locations.json")
    for loc in model_output_list:
        if loc["name"] not in existing_locs:
            print("ERROR, {name} not in remaining_locations".format(name=loc["name"]))
        else:
            del existing_locs[loc["name"]]
    return model_output_list, existing_locs


def create_connections_shot(loc1, loc2, output):
    user_prompt = json.dumps(loc1) + "\n" + json.dumps(loc2)
    user = {"role": "user", "content": user_prompt}
    assistant = {"role": "assistant", "content": json.dumps(output)}

    return [user, assistant]

def get_token_ids(words_list):
    encoding = tiktoken.encoding_for_model("gpt-4")
    text = " ".join(words_list)
    encodings = encoding.encode(text)

    return encodings

def generate_connections_step(loc1, loc2, dirs, shots):
    dirs_ids = get_token_ids(dirs)
    logit_biases = {}
    for tid in dirs_ids:
        logit_biases[tid] = 12
    quote_id = get_token_ids(["'\""])
    logit_biases[quote_id[0]] = -100
    loc1_name, loc2_name = loc1["name"], loc2["name"]
    client = OpenAI(base_url="https://oai.hconeai.com/v1", api_key=os.environ['HELICONE_API_KEY'])
    sys_prompt = f"""You are a helpful map generator for building a text adventure game.
Now, given the name and description of two locations (the first one is location 1, the second one is location 2)
from the user, determine which direction (pick from THIS LIST: {dirs}) the player should go to get from location 1 to location 2.
Remember, the only valid directions are ones in this list: {dirs}; DO NOT pick a direction that is not in the list, even if it makes logical sense.
The direction you choose should be exactly as it shows up in {dirs}, not a character different.
Pick the direction that is the most logically coherent with the location descriptions.
Just output the one word for the direction.
"""
    user_prompt = json.dumps(loc1) + json.dumps(loc2)
    messages = [{"role": "system", "content": sys_prompt}]
    messages += [{"role": "user", "content": user_prompt}]
    direction = ""
    while direction not in dirs:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            logit_bias=logit_biases
        )
        direction = completion.choices[0].message.content.strip().lower()
    print(direction)
    
    messages += [{"role": "assistant", "content": direction}]
    user_prompt_2 = f"""Now, output a one-sentence description of how the player moves {direction} from location 1 to location 2.
Something like this: Leaving the warm blanket nook of the Cozy Corner, you venture into the unknown, led by the magic ribbon. Gradually, entering the different premises of Jerry's Cage - the kingdom of the imprisoned Jerry awaiting liberation.
"""
    messages += [{"role": "user", "content": user_prompt_2}]
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
    )
    travel_desc_to = completion.choices[0].message.content
    messages += [{"role": "assistant", "content": travel_desc_to}]
    user_prompt_3 = f"""Now, output a one-sentence description of how the player moves {direction_mappings[direction]} (the opposite direction) from location 2 to location 1."""
    messages += [{"role": "user", "content": user_prompt_3}]
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
    )
    travel_desc_from = completion.choices[0].message.content
    loc1["connections"][direction] = loc2_name
    loc2["connections"][direction_mappings[direction]] = loc1_name
    loc1["travel_descriptions"][direction] = travel_desc_to
    loc2["travel_descriptions"][direction_mappings[direction]] = travel_desc_from
    return loc1, loc2, direction


def generate_connections(loc1, loc2, dirs, shots):
    loc1_name, loc2_name = loc1["name"], loc2["name"]
    client = OpenAI(base_url="https://oai.hconeai.com/v1", api_key=os.environ['HELICONE_API_KEY'])
    sys_prompt = f"""You are a helpful map generator for building a text adventure game.
Now, given the name and description of two locations (the first one is location 1, the second one is location 2)
from the user, determine which direction (pick from THIS LIST: {dirs}) the player should go to get from location 1 to location 2.
Remember, the only valid directions are ones in this list: {dirs}; DO NOT pick a direction that is not in the list, even if it makes logical sense.
The direction you choose should be exactly as it shows up in {dirs}, not a character different.
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
    _, desc2 = model_output_list[1]["direction"].strip(
    ), model_output_list[1]["travel description"]
    loc1["connections"][direction1] = loc2_name
    loc2["connections"][direction_mappings[direction1]] = loc1_name
    loc1["travel_descriptions"][direction1] = desc1
    loc2["travel_descriptions"][direction_mappings[direction1]] = desc2
    return loc1, loc2, direction1