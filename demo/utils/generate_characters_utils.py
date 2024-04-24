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

    with open(directory + "data/few-shot-examples/example-character.json", 'r') as file:
        examples = json.load(file)

    prompt = "You are a helpful main character generator for building a text adventure game based on a given story. Generate one main character from this story in a JSON format. Character's inventory should be empty so remember to leave the values to the location, goal, and inventory keys empty. The JSON should be in the following JSON format:{form}.".format(form=character_format)
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

def generate_npc(background_story, stories, character_format, main_character, directory=""):
    print("here in npc")
    default_num_npc = 4
    try:
        num_npc = int(input("How many NPC characters do you want to generate? Choose a number between 0-10 (Default value is 4): "))
        if num_npc < 0 or num_npc > 10:
            num_npc = default_num_npc
            print(f"Invalid input. Using default value: {default_num_npc}")
    except ValueError:
        num_npc = default_num_npc
        print(f"Invalid input. Using default value: {default_num_npc}")
    
    print("num npc: ", num_npc)

    client = OpenAI(base_url="https://oai.hconeai.com/v1", api_key=os.environ['HELICONE_API_KEY'])

    try:
        with open(directory + "data/few-shot-examples/example-character.json", 'r') as file:
            examples = json.load(file)
    except FileNotFoundError:
        print("File not found.")
        return []

    npc_dict = {}
    for num in range(num_npc):
        print("Generating NPC:", num + 1)

        # with open(directory+"data/approved_characters.json", "r") as file:
        #     generated = file.read()
        # generated = main_character

        # with open(directory+"data/approved_NPC_characters.json", "r") as file:
        #     generated_npc = file.read()
        #generated_npc = main_character

        prompt = ("You are a helpful character generator for building a text adventure game based on a given story description. Given the "
                  "background story of the game from the user and the main character:{character} of the game, generate one single NPC character "
                  "in JSON. Make sure to leave the fields for location and inventory empty. "
                  "Do not generate any previously generated character, i.e. the the generated charecter should not match any character or "
                  "share any value with any character from {character} OR {NPC} "
                  "The generated NPC should have a goal that either helps the main character achieve their goal or to prevent them from achieving their  goal."
                  "The goal for the generated NPC should be simple and very specific."
                  "If you dont see any extra characters in the story for NPC roles, create any character from your imagination that fits the story.").format(form=character_format,NPC = npc_dict, character = main_character)
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
        print("Received NPC Content:", npc_content)
        try:
            npc_dict[str(num)] = json.loads(npc_content)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON for NPC {num}: {npc_content}")
            npc_dict[str(num)] = {"error": "Invalid JSON received"}

    return npc_dict
