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
def promptGPT(stories, directory):
    if 'HELICONE_API_KEY' not in os.environ:
        os.environ['HELICONE_API_KEY'] = 'sk-helicone-cp-spr2h6y-tdie7wq-whq5thq-oq33ugy'


    client = OpenAI(base_url="https://oai.hconeai.com/v1", api_key=os.environ['HELICONE_API_KEY'])

    with open(directory + "data/few-shot-examples/example-character.json", 'r') as file:
        examples = json.load(file)
    
    with open(directory+"data/approved_characters.json", "r") as file:
        generated = file.read()

    prompt = "You are a helpful main character generator for building a text adventure game for the following story:{story}. Generate one main character from this story in a JSON format. Character's inventory should be empty so remember to leave the values to the location and inventory keys empty. The JSON should be in the following JSON format:{form}. Do not generate any previously generated character.Generate a character you have never generated before. No value of any of the keys of the character should match any of the previously generated characters' values. None of the characters should match any character or share any value with any character from {gen}".format(story=stories[0],form=examples[0],gen = generated)
    messages = [
        {'role': 'system', 'content': prompt},
        {'role': 'user', 'content': "The example story 1 is : {story}".format(story=stories[1])},
        {"role": "assistant", "content": json.dumps(examples[0])},
        {'role': 'user', 'content': "The example story 2 is : {story}".format(story=stories[2])},
        {"role": "assistant", "content": json.dumps(examples[1])}
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
    gpt_response = response.choices[0].message.content
    return json.loads(gpt_response)
