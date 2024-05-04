import json
import os
from openai import OpenAI
from utils.frontend_utils import *

def load_json(filename):
    """ Load JSON data from a file """
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

def save_json(data, filename):
    """ Save data to a JSON file """
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def extract_items(directory):
    items = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            full_path = os.path.join(directory, filename)
            try:
                json_data = load_json(full_path)
                if 'locations' in json_data:
                    for location in json_data['locations']:
                        if 'items' in location:
                            for item in location['items'].values():
                                if 'location' in item:
                                    del item['location']
                            items.extend(location['items'].values())
            except json.JSONDecodeError:
                print(f"Error decoding JSON from file {filename}")
            except Exception as e:
                print(f"An error occurred with file {filename}: {str(e)}")
    return items

# Set the directory containing the JSON files
directory = 'games-data'  # Adjust the path to the directory of your JSON files
output_filename = 'data/extracted_items.json'  # The filename for the output JSON

# Extract Item data
# extracted_items = extract_items(directory)

# Save the extracted data to a new JSON file in the same directory as this script
# save_json(extracted_items, output_filename)
# print(f"Data extracted and saved to {output_filename}")

# ####################
# #few shot GPT-4

def generate_inventory_items(character, main_character, winning_state, location_name, location_actions, 
                             location_items, sample_items, existing_items):
    client = OpenAI(base_url="https://oai.hconeai.com/v1", api_key=os.environ['HELICONE_API_KEY'])
        # Determine if the character is the main character
    goal = winning_state if character["name"] == main_character["name"] else character["goal"]
    # Create a detailed prompt with location context, action list, and few-shot examples
    prompt = "You are a helpful character inventory generator for building a text adventure game."
    prompt = f"Given the character '{character['name']}', described as '{character['description']}'"
    prompt += f"who must achieve the goal: '{goal}', generate 5 suitable inventory items for this character."
    prompt += f"The character is in the location {location_name}, and the purpose of location is: {location_actions}."
    prompt += f"The items that are in '{location_name}' are: {location_items}."
    prompt += f"Taking all this information into consideration, generate inventory items for the given character."
    prompt += f"Each inventory should include name, description, examine text,"
    prompt += "and properties that fit the character's role and actions in the narrative."
    prompt += f"Here are the inventory items you have already generated for this character before and SHOULD NOT generate again: {existing_items}"
    
    messages = [
        {'role': 'system', 'content': prompt},
        {'role': 'user', 'content': f"Please list 5 potential items for the character Bonny the Fisherman based on their goal, actions, and available location items."},
        {'role': 'assistant', 'content': sample_items},
        {'role': 'user', 'content': f"Please list 5 potential items for the character {character['name']} based on their goal, actions, and available location items."}
    ]

    response = client.chat.completions.create(
        model='gpt-4',
        messages=messages,
        temperature=1,
        max_tokens=2048,
        top_p=1.0,
        frequency_penalty=0,
        presence_penalty=0
    )

    inventory_items = json.loads(response.choices[0].message.content)
    return inventory_items

def populate_character_inventories(directory, main_character, winning_state):
    # Load location data
    with open(f"data/test_generations/all_the_locations.json", 'r') as file:
        locations_data = json.load(file)

     # Load action descriptions
    with open("test.json", 'r') as file:
        action_descriptions = json.load(file)

    # Load extracted items for few-shot learning
    with open(f"data/extracted_items.json", 'r') as file:
        extracted_items = json.load(file)
    
     # Sample of extracted items for the few-shot example
    sample_items = json.dumps(extracted_items[:5], indent=4)

    all_characters = []  # List to store all characters for all_the_characters.json
    # Iterate through each location and their characters
    for loc_ind, location in enumerate(locations_data):
        location_actions = action_descriptions.get(location['name'], "No specific actions described.") # purpose of location
        location_items_names = [item_name for item_name in location["items"]]
        location_items = json.dumps(location_items_names, indent=4)
        
        for char_name, character in location["characters"].items():
            already_generated_items = []
            all_selected_items = []
            while True:
                inventory_items = generate_inventory_items(character, main_character, winning_state, 
                                                        location["name"], location_actions, location_items,
                                                        sample_items, already_generated_items)
                # render inventory items to user
                render_items_choices(inventory_items)
                already_generated_items += inventory_items
                selected_items_in_round = get_selected_items(inventory_items)
                all_selected_items += selected_items_in_round
                render_selected_items(all_selected_items)
                if user_submit():
                    break
            items_dict = {}
            for _, item in enumerate(all_selected_items):
                items_dict[item['name']] = item

            character['inventory'] = items_dict
            all_characters.append(character)  # Add updated character to the list
            locations_data[loc_ind]["characters"][char_name]["inventory"] = items_dict

    # Save the updated location data back to the same file
    with open(f"data/test_generations/all_the_locations.json", 'w') as file:
        json.dump(locations_data, file, indent=4)
     # Save all characters to all_the_characters.json
    with open(f"data/test_generations/all_the_characters.json", 'w') as file:
        json.dump(all_characters, file, indent=4)


def populate_objects_in_location_round(location, action_descriptions, sample_items, existing_items):
    client = OpenAI(base_url="https://oai.hconeai.com/v1", api_key=os.environ['HELICONE_API_KEY'])

    location_actions = action_descriptions.get(location['name'], "No specific actions described.")

    prompt = "You are a helpful objects generator for building a text adventure game."
    prompt += f"Given the location name, its description, and its purpose from the user,"
    prompt += "generate a list of 5 suitable and purposeful objects that should be in this location."
    prompt += "Output the objects as a list of JSON objects."
    prompt += "Include all necessary attributes such as name, description, examine text, and properties."
    prompt += f"Here are the objects you have already generated for this location before and SHOULD NOT generate again: {existing_items}"


    shot1_user = """Please list of 5 potential objects for the location Lake Shore based on its description and purpose:
    location name: Lake Shore
    location description: Lake Shore is a serene spot where the gentle lapping of crystal-clear waters blends with the rustle of reeds, offering a peaceful retreat for both nature lovers and fishing enthusiasts.
    location purpose: The player needs to catch fish with a fishing rod and collect a shellfish.
    """
    user_prompt = f"""Please list of 5 potential objects for the location Lake Shore based on its description and purpose:
    location name: {location['name'].strip()}
    location description: {location["description"].strip()}
    location purpose: {location_actions}
    """

    messages = [
        {'role': 'system', 'content': prompt},
        {'role': 'user', 'content': shot1_user},
        {'role': 'assistant', 'content': sample_items},
        {'role': 'user', 'content': user_prompt}
    ]

    response = client.chat.completions.create(
            model='gpt-4',
            messages=messages,
            temperature=0.8,
            max_tokens=2048,
            top_p=1.0,
            frequency_penalty=0,
            presence_penalty=0
        )
    gpt_response = response.choices[0].message.content
    new_items = json.loads(gpt_response)
    return new_items

def generate_objects_in_locations(directory):

     # Load location data
    with open(f"data/test_generations/all_the_locations.json", 'r') as file:
        locations = json.load(file)
    # Load the action descriptions from the test.json file
    with open("test.json", 'r') as file:
        action_descriptions = json.load(file)
    # Load extracted items for few-shot learning
    with open(f"data/extracted_items.json", 'r') as file:
        extracted_items = json.load(file)
    
     # Sample of extracted items for the few-shot example
    sample_items = json.dumps(extracted_items[5:10], indent=4)
    for loc_ind, location in enumerate(locations):
        print(f"\nNow, let's generate items in the location {location['name']}......\n")
         # Retrieve action description from test.json for the current location

        already_generated_items = []
        all_selected_items = []
        while True:
            location_items = populate_objects_in_location_round(location, action_descriptions, 
                                                                sample_items, already_generated_items)
            render_items_choices(location_items)
            already_generated_items += location_items
            selected_items_in_round = get_selected_items(location_items)
            all_selected_items += selected_items_in_round
            render_selected_items(all_selected_items)
            if user_submit():
                break
        # Append generated items to the location's 'items' field
        items_dict = {}
        for _, item in enumerate(all_selected_items):
            item['location'] = location['name']
            items_dict[item['name']] = item

        locations[loc_ind]['items'] = items_dict

         # Save the updated location data back to the same file
    with open(f"data/test_generations/all_the_locations.json", 'w') as file:
        json.dump(locations, file, indent=4)


# #Object generation based on the generated location json
# main_character = {
#         "name": "Serenity",
#         "description": "In a calming, serene world, Serenity is a tranquil entity. Known for her calm demeanor, she embodies peace and tranquility. With her soft voice and gentle touch, she exerts a soothing aura that radiates restfulness. Often found meditating or reading under a sprawling tree, she is considered by many to be the epitome of relaxation.",
#         "persona": "I am Serenity. They say my presence is like a gentle melody, soothing and calm. I believe in the rhythm of nature and the power of stillness to bring about harmony and balance. I find joy in quiet moments, in watching the sunset, listening to the rustling leaves, and in the peace that solitude brings.",
#         "location": {},
#         "goal": "",
#         "inventory": {}
#     }
# winning_state = "Serenity finds peace"
# generate_object(directory)
# populate_character_inventories(directory, main_character, winning_state)