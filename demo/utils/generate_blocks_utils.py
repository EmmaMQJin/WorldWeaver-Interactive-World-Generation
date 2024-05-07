import json
import os
from openai import OpenAI
import re


def load_json(filename):
    """ Load JSON data from a file """
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

def save_json(data, filename):
    """ Save data to a JSON file """
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def save_code_as_str(filename):
    with open(filename , 'r') as file:  
        code_as_string = file.read()
    return code_as_string

# def main():
#     print("in main")
#     background_story = "A Costco themed game with hungry pigeons"

#     action_list = """
#     exit nest
#     fly towards Costco
#     land on Costco roof
#     observe food court
#     locate pizza stand
#     evade Costco employees
#     sneak into food court
#     find leftover pizza
#     grab pizza slice
#     dodge hungry seagull
#     escape back to roof
#     fly back to nest
#     eat pizza slice
#     """

#     game_locations = """
#     {
#     "Nest": "Starting location. The player then needs to exit their nest to start the adventure.",
#     "Central Park": "A intermediate location where player flies after exiting nest",
#     "Costco Entrance": "The player needs to fly to and dodge shopping carts here.",
#     "Free Sample Table": "Where the player can grab a cracker while avoiding the clerk.",
#     "Pizza Display": "Where the player distracts the Costco employee with the cracker and nabs a pizza slice.",
#     "Sky above Park": "An intermediate location to fly back through to get to the nest.",
#     "Back to Nest": "The final location where the player consumes the pizza slice."
#     }
#     """
#     all_locations_path = "data/test_generations/all_the_locations.json"
#     generate_blocks(background_story, action_list,all_locations_path)
#     input_file_path = 'data/generated_blocks.py'  # Path to the file containing the block classes
#     output_file_path = 'data/extracted_block_classes.py'  # Path to save the extracted block classes
#     extract_block_classes(input_file_path, output_file_path)
#     blocks_file_path = 'data/generated_blocks.py'
#     locations_json_path = "data/test_generations/all_the_locations.json"
#     output_json_path = 'data/test_generations/all_the_locations.json'
#     integrate_blocks(locations_json_path, blocks_file_path, output_json_path)

def generate_blocks(background_story, action_list, all_locations_path, directory = "../data"):
    client = OpenAI(base_url="https://oai.hconeai.com/v1", api_key=os.environ['HELICONE_API_KEY'])

    # with open(directory + "data/few-shot-examples/example-character.json", 'r') as file:
    #     examples = json.load(file)

    prompt = ("You are a helpful playthrough block generator for text adventure games. " 
               "Your job is to create blocks in some of the locations of the game so that the user needs to complete a task or puzzle to go forward. "
            "Given the background story of the game, the set locations in the game and the actions that the main character can take, "
            "write a detailed list of blocks that can be added to game locations to make the came more interesting and fun. "
             " The block descriptions should be detailed and should be coherent with the rest of the game objects. "
             "Write python code based on the blocks you generate.")
    
    few_shot_prompt1 = ("For the game given, create a block as a function, that takes in a location and a character as a Troll. "
                        "Block should be applied if the troll is at the location, the troll is alive and conscious, and the troll is still hungry")
    few_shot_prompt2 = ("For the game given, create a block as a function, that takes in a location and a character as a Guard. "
                        "Block should be applied if the guard is at the location, the guard is alive and conscious, and the guard is suspicious")
    few_shot_prompt3 = ("For the game given, create a darkness block as a function, that takes in a location. Block should be applied if the location "
                        "is dark and gets unblocked if any character at the location is carrying a lit item (like a lamp or candle)")
    few_shot_prompt4 = ("For the game given, create a door block as a function, that takes in a location. Gets unblocked if door is unblocked")
    few_shot_prompt5 = ("For the game given, create a block as a function, that takes in a location and a character as a Monster. Block should be "
                        "applied if the monster is at the location, the monster is alive and conscious, and the monster is old")
    few_shot_prompt6 = ("For the game given, create a rock block as a function, that takes in a location. Gets unblocked if rock has cracks")

    few_shot_result1 = save_code_as_str("data/block_few_shots/example1")
    few_shot_result2 = save_code_as_str("data/block_few_shots/example2")
    few_shot_result3 = save_code_as_str("data/block_few_shots/example3")
    few_shot_result4 = save_code_as_str("data/block_few_shots/example4")
    few_shot_result5 = save_code_as_str("data/block_few_shots/example5")
    few_shot_result6 = save_code_as_str("data/block_few_shots/example6")


    messages = [
        {'role': 'system', 'content': prompt},
        {'role': 'user', 'content': few_shot_prompt1},
        {"role": "assistant", "content": few_shot_result1},
        {'role': 'user', 'content': few_shot_prompt2},
        {"role": "assistant", "content": few_shot_result2},
        {'role': 'user', 'content': few_shot_prompt3},
        {"role": "assistant", "content": few_shot_result3},
        {'role': 'user', 'content': few_shot_prompt4},
        {"role": "assistant", "content": few_shot_result4},
        {'role': 'user', 'content': few_shot_prompt5},
        {"role": "assistant", "content": few_shot_result5},
        {'role': 'user', 'content': few_shot_prompt6},
        {"role": "assistant", "content": few_shot_result6}
    ]

     # Load all locations data to use in block generation
    with open(all_locations_path, 'r') as file:
        all_locations = json.load(file)
    with open("test.json", 'r') as file:
        game_locations = json.load(file)

    # Construct a context of game state for block generation
  
    locations_context = ""
    for location in all_locations:
        connections = ", ".join([f"{k} leads to {v}" for k, v in location.get('connections', {}).items()])
        items = ", ".join([item['name'] for item in location.get('items', {}).values()])
        characters = ", ".join([char['name'] for char in location.get('characters', {}).values()])
        locations_context += f"Location: {location['name']}, Connections: {connections}, Items: {items}, Characters: {characters}\n"

    prompt = (
        "You are a playthrough block generator for text adventure games. "
        "Given a background story, locations with specific connections and travel descriptions, and a list of actions, your job is to create Python class definitions for blocks. "
        "These blocks should represent challenges or tasks that must be completed at all locations and connections in the game based on the actions. "
        "Specifically, for locations with multiple connections, ensure that you generate blocks that can be logically and strategically placed based on the storyline and player actions. "
        "Choose connections that are most integral to the story's progression or challenge level for placing these blocks. "
        "Each block should have parameters for characters and items that exactly match their full names as found in the game data, converted into snake_case. "
        "For example, 'Whiskers the Stray Cat' should be 'whiskers_the_stray_cat'. Include the connection direction and the destination name as parameters in the class constructor."
        f"\n\nBackground Story: {background_story}\nGame Actions: {action_list}\n Actions in locations: {game_locations}\nLocations Context: {locations_context}"
    )

    examples = """
    Example output:
    ('Costco Parking Lot', 'west', 'Territory of the Seagulls', 
    '''
    class CostcoParkingLotWestBlock(blocks.Block):
        def __init__(self, location: things.Location, whiskers_the_stray_cat: things.Character, connection: str):
            super().__init__('Whiskers the Stray Cat is blocking the way', 'You need to distract Whiskers the Stray Cat to proceed to the Territory of the Seagulls.')
            self.whiskers_the_stray_cat = whiskers_the_stray_cat
            self.location = location
            self.connection = connection  # This parameter reflects the destination name

        def is_blocked(self) -> bool:
            return self.location.here(self.whiskers_the_stray_cat)
    '''),
    """
    
    full_prompt = f"{prompt}\n{examples}"


    messages += [{"role": "user", "content": full_prompt}]

    response = client.chat.completions.create(
        model='gpt-4',
        messages=messages,
        temperature=0.2,
        max_tokens=2048,
        top_p=1.0,
        frequency_penalty=0,
        presence_penalty=0
    )
    gpt_response = response.choices[0].message.content
    with open("data/generated_blocks.py", 'w') as file:
        file.write(gpt_response)


#This function just extracts the Block class from the tuple and add
def extract_block_classes(input_file_path, output_file_path):
    """
    This function reads a Python file containing tuples of location names, connection direction,
    connection destination, and block class definitions, and extracts just the block class definitions
    to write them to a new Python file.
    
    Args:
    input_file_path (str): The path to the input Python file with block definitions.
    output_file_path (str): The path to the output Python file to store only block classes.
    """
    try:
        with open(input_file_path, 'r') as file:
            lines = file.read()
        
        # Pattern to capture the class definitions within the tuples
        block_class_pattern = re.compile(r"\'\'\'\n(class\s+[\s\S]+?)\'\'\'\)", re.MULTILINE)
        
        block_classes = block_class_pattern.findall(lines)

        # Write the extracted block classes to the output file
        with open(output_file_path, 'w') as file:
            for block_class in block_classes:
                file.write(block_class + '\n\n')

        print(f"Block classes extracted successfully to {output_file_path}")
    
    except Exception as e:
        print(f"An error occurred: {e}")


def normalize_key(name):
    return re.sub(r'\s+|_', '', name).lower()

def parse_block_definitions(blocks_content):
    block_patterns = re.findall(r"\('([^']+)',\s*'([^']+)',\s*'([^']+)',\s*'''\n([\s\S]+?)\n'''\)", blocks_content)
    block_info = {}
    for location, direction, destination, block_code in block_patterns:
        class_name_match = re.search(r"class\s+(\w+)(Block)\(blocks\.Block\):", block_code)
        if class_name_match:
            class_name = class_name_match.group(1) + class_name_match.group(2)
            parameters = dict(re.findall(r"self\.(\w+)\s*=\s*(\w+)", block_code))
            block_info[(location, direction, destination)] = {
                "class_name": f"{class_name}",
                "parameters": parameters
            }
    return block_info

def integrate_blocks(locations_json_path, blocks_file_path, output_json_path):
    with open(locations_json_path, 'r') as file:
        locations = json.load(file)

    with open(blocks_file_path, 'r') as file:
        blocks_content = file.read()

    block_definitions = parse_block_definitions(blocks_content)

    for location in locations:
        location_items = {normalize_key(item): item_data['name'] for item, item_data in location.get('items', {}).items()}
        location_characters = {normalize_key(char): char_data['name'] for char, char_data in location.get('characters', {}).items()}

        for direction, destination in location.get('connections', {}).items():
            key = (location['name'], direction, destination)
            if key in block_definitions:
                info = block_definitions[key]
                block_info = {
                    "_type": info['class_name'],
                    # Initially set connection to the actual destination name
                    "connection": destination
                }
                
                for param, placeholder in info['parameters'].items():
                    if param == 'connection':
                        # Skip processing for 'connection' parameter, it's already correctly assigned
                        continue

                    normalized_param = normalize_key(placeholder)
                    if normalized_param == 'location':
                        actual_value = location['name']
                    elif normalized_param in location_items:
                        actual_value = location_items[normalized_param]
                    elif normalized_param in location_characters:
                        actual_value = location_characters[normalized_param]
                    else:
                        actual_value = placeholder  # Use the placeholder if no match is found
                    
                    block_info[param] = actual_value

                location['blocks'][direction] = block_info

    with open(output_json_path, 'w') as file:
        json.dump(locations, file, indent=4)
    print(f"Block classes extracted integrated to all_the_locations.")




# if __name__ == "__main__":
#     main()
