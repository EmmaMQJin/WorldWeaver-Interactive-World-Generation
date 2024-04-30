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

def extract_characters(directory):
    characters = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            full_path = os.path.join(directory, filename)
            try:
                json_data = load_json(full_path)
                if 'characters' in json_data:
                    # Process each character to remove the 'location' key
                    for character in json_data['characters']:
                        if 'location' in character:
                            character['location'] = {} 
                    characters.extend(json_data['characters'])
            except json.JSONDecodeError:
                print(f"Error decoding JSON from file {filename}")
            except Exception as e:
                print(f"An error occurred with file {filename}: {str(e)}")
    return characters

# Set the directory containing the JSON files
directory = ''  # Adjust the path to the directory of your JSON files
output_filename = 'extracted_characters.json'  # The filename for the output JSON

# Extract character data
# extracted_characters = extract_characters(directory)

# Save the extracted data to a new JSON file in the same directory as this script
#save_json(extracted_characters, output_filename)
#print(f"Data extracted and saved to {output_filename}")


####################
#few shot GPT-4
def generate_main_character(background_story, example_stories, character_format, examples, directory = ""):
    client = OpenAI(base_url="https://oai.hconeai.com/v1", api_key=os.environ['HELICONE_API_KEY'])

    with open(directory + "data/few-shot-examples/example-characters.json", 'r') as file:
        examples = json.load(file)

    prompt = f"""You are a helpful main character generator for building a text adventure game based on a given story.
Generate one main character from this story in a JSON format.
Remember to leave the values to the location and inventory keys empty.
Output the character in JSON format, like this:
{character_format}"""

    messages = [
        {'role': 'system', 'content': prompt},
        {'role': 'user', 'content': "The example story 1 is : {story}".format(story=example_stories[0])},
        {"role": "assistant", "content": json.dumps(examples[0])},
        {'role': 'user', 'content': "The example story 2 is : {story}".format(story=example_stories[1])},
        {"role": "assistant", "content": json.dumps(examples[1])}
    ]

    messages += [{"role": "user", "content": background_story}]

    response = client.chat.completions.create(
        model='gpt-4',
        messages=messages,
        temperature=1,
        max_tokens=2048,
        top_p=1.0,
        frequency_penalty=0,
        presence_penalty=0
    )
    gpt_response = response.choices[0].message.content
    return json.loads(gpt_response)

def generate_npc_in_location(location_name, location_purpose, background_story, main_character, character_format, stories, all_characters):
    default_num_npc = 1
    try:
        num_npc = int(input(f"\nHow many NPC characters do you want to generate in the location {location_name}?\nChoose a number between 0-4 (Default value is 1):\n"))
        if num_npc < 0 or num_npc > 4:
            num_npc = default_num_npc
            print(f"Invalid input. Using default value: {default_num_npc}")
    except ValueError:
        num_npc = default_num_npc
        print(f"Invalid input. Using default value: {default_num_npc}")
    
    print(f"\nOK, the number of NPCs generated in {location_name} will be {num_npc}.\n")

    client = OpenAI(base_url="https://oai.hconeai.com/v1", api_key=os.environ['HELICONE_API_KEY'])

    try:
        with open("data/few-shot-examples/example-characters.json", 'r') as file:
            examples = json.load(file)
    except FileNotFoundError:
        print("File not found.")
        return []

    npc_dict = {}
    for num in range(num_npc):
        prompt = f"""You are a helpful character generator for building a text adventure game.
Your job is to generate an NPC in the location {location_name}. The purpose of this location is: {location_purpose}, and the player of the game is: {main_character}.
Given the background story of the game from the user, generate one single NPC character in JSON.
Do not generate any previously generated character, i.e. the the generated charecter should not be a duplicate of any character or
be similar to these characters that already exists: {all_characters}.
However, if the location name or the purpose of the location mentions some character name that is not in the list of existing characters,
you should definitely generate that character as an NPC.
The generated NPC should have a goal that either helps the main character achieve their goal or to prevent them from achieving their goal. The goal for the generated NPC should be simple and very specific.
If you dont see any extra characters in the story for NPC roles, create any character from your imagination that fits the story.
Output the character in JSON format, like this:
{character_format}
Remember to leave the location and inventory of each character empty.
"""
        messages = [
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': "{story}".format(story=stories[0])},
            {"role": "assistant", "content": json.dumps(examples[0])},
            {'role': 'user', 'content': "{story}".format(story=stories[1])},
            {"role": "assistant", "content": json.dumps(examples[1])}
        ]

        messages += [{"role": "user", "content": background_story}]

        response = client.chat.completions.create(
            model='gpt-4',
            messages=messages,
            temperature=1,
            max_tokens=2048,
            top_p=1.0,
            frequency_penalty=0,
            presence_penalty=0
        )

        npc_content = response.choices[0].message.content
        print("Generated NPC: \n", npc_content)
        try:
            npc_json = json.loads(npc_content)
            npc_json["location"] = location_name
            npc_dict[npc_json["name"]] = npc_json
            all_characters.append(npc_json)
            
        except json.JSONDecodeError:
            print(f"Failed to parse JSON for NPC {num}: {npc_content}")

    return npc_dict, all_characters
