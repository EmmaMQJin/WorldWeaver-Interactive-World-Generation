import json
import os
from openai import OpenAI

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
directory = '../games-data'  # Adjust the path to the directory of your JSON files
output_filename = 'data/extracted_items.json'  # The filename for the output JSON

# Extract Item data
# extracted_items = extract_items(directory)

# Save the extracted data to a new JSON file in the same directory as this script
# save_json(extracted_items, output_filename)
# print(f"Data extracted and saved to {output_filename}")

# ####################
# #few shot GPT-4


def populate_character_inventories(directory, main_character, winning_state):
    if 'HELICONE_API_KEY' not in os.environ:
        os.environ['HELICONE_API_KEY'] = 'sk-helicone-cp-nuxlzea-i3cuq6q-xpvlrga-pgbu4si'

    client = OpenAI(base_url="https://oai.hconeai.com/v1", api_key=os.environ['HELICONE_API_KEY'])

    # Load location data
    with open(f"../data/test_generations/all_the_locations.json", 'r') as file:
        locations_data = json.load(file)

     # Load action descriptions
    with open("../test.json", 'r') as file:
        action_descriptions = json.load(file)

    # Load extracted items for few-shot learning
    with open(f"../data/extracted_items.json", 'r') as file:
        extracted_items = json.load(file)
    
     # Sample of extracted items for the few-shot example
    sample_items = json.dumps(extracted_items[:5], indent=4)

    all_characters = []  # List to store all characters for all_the_characters.json
    print("-----------ITEM GENERATION----------------")
    print(f"Generating Inventory for all characters:")
    # Iterate through each location and their characters
    for location in locations_data:
        location_actions = action_descriptions.get(location['name'], "No specific actions described.")
        location_items_names = [item_name for item_name in location["items"]]
        location_items = json.dumps(location_items_names, indent=4)
        
        for char_name, character in location["characters"].items():
            # Determine if the character is the main character
            goal = winning_state if character["name"] == main_character["name"] else character["goal"]

            # Create a detailed prompt with location context, action list, and few-shot examples
            prompt = f"Given the character '{char_name}', described as '{character['description']}', who must achieve the goal: '{goal}', generate suitable inventory items. Consider the actions: {location_actions}. Available items in '{location['name']}' are: {location_items}. Each item should include name, description, examine text, and properties that fit the character's role and actions in the narrative."
            
            messages = [
                {'role': 'system', 'content': prompt},
                {'role': 'user', 'content': f"Please list potential items for {char_name} based on their goal, actions, and available location items."},
                {'role': 'assistant', 'content': sample_items},
                {'role': 'user', 'content': f"Now, generate detailed inventory items for {char_name} based on the goal and available items."}
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
            items_dict = {}
            # Append generated items to the location's 'items' field
            
            for i, item_key in enumerate(inventory_items):
                items_dict[inventory_items[i]['name']] = inventory_items[i]

            character['inventory'] = items_dict
            all_characters.append(character)  # Add updated character to the list

    # Save the updated location data back to the same file
    with open(f"../data/test_generations/all_the_locations.json", 'w') as file:
        json.dump(locations_data, file, indent=4)
     # Save all characters to all_the_characters.json
    with open(f"../data/test_generations/all_the_characters.json", 'w') as file:
        json.dump(all_characters, file, indent=4)



def generate_object(directory):
    if 'HELICONE_API_KEY' not in os.environ:
        os.environ['HELICONE_API_KEY'] = 'sk-helicone-cp-nuxlzea-i3cuq6q-xpvlrga-pgbu4si'


    client = OpenAI(base_url="https://oai.hconeai.com/v1", api_key=os.environ['HELICONE_API_KEY'])


     # Load location data
    with open(f"../data/test_generations/all_the_locations.json", 'r') as file:
        locations = json.load(file)
    # Load the action descriptions from the test.json file
    with open("../test.json", 'r') as file:
        action_descriptions = json.load(file)
    # Load extracted items for few-shot learning
    with open(f"../data/extracted_items.json", 'r') as file:
        extracted_items = json.load(file)
    
     # Sample of extracted items for the few-shot example
    sample_items = json.dumps(extracted_items[:5], indent=4)
    print("-----------ITEM GENERATION----------------")
    for location in locations:
        print(f"Generating items for: {location['name']}")
         # Retrieve action description from test.json for the current location
        location_actions = action_descriptions.get(location['name'], "No specific actions described.")

        # Create a detailed prompt with location context, action list, and few-shot examples
        prompt = f"Based on the activities described for {location['name'].strip()}: '{location_actions}', generate appropriate items. Include all necessary attributes such as name, description, examine text, and properties. Follow the style and depth of the given examples."
        num_items = input(f"Enter the number of new items you want to generate for {location['name'].strip()}:")

        messages = [
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': 'Here are some examples of items:'},
            {'role': 'assistant', 'content': sample_items},
            {'role': 'user', 'content': f'Please create a list of {num_items} new items based on these examples for the location: {location["description"].strip()}'}
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
        items_dict = {}
        # Append generated items to the location's 'items' field
        print("NEW ITEMS: \n", new_items)
        for i, item_key in enumerate(new_items):
            print(i, item_key)
            new_items[i]['location'] = location['name']
            items_dict[new_items[i]['name']] = new_items[i]

        location['items'] = items_dict

         # Save the updated location data back to the same file
    with open(f"../data/test_generations/all_the_locations.json", 'w') as file:
        json.dump(locations, file, indent=4)


# #Object generation based on the generated location json
main_character = {
        "name": "Serenity",
        "description": "In a calming, serene world, Serenity is a tranquil entity. Known for her calm demeanor, she embodies peace and tranquility. With her soft voice and gentle touch, she exerts a soothing aura that radiates restfulness. Often found meditating or reading under a sprawling tree, she is considered by many to be the epitome of relaxation.",
        "persona": "I am Serenity. They say my presence is like a gentle melody, soothing and calm. I believe in the rhythm of nature and the power of stillness to bring about harmony and balance. I find joy in quiet moments, in watching the sunset, listening to the rustling leaves, and in the peace that solitude brings.",
        "location": {},
        "goal": "",
        "inventory": {}
    }
winning_state = "Serenity finds peace"
generate_object(directory)
populate_character_inventories(directory, main_character, winning_state)