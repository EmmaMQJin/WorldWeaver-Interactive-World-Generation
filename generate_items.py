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
directory = '/Users/hardikjain/Documents/Spring 24/CIS-7000-Project/WorldWeaver-Interactive-World-Generation/games'  # Adjust the path to the directory of your JSON files
output_filename = 'extracted_items.json'  # The filename for the output JSON

# Extract Item data
extracted_items = extract_items(directory)

# Save the extracted data to a new JSON file in the same directory as this script
# save_json(extracted_items, output_filename)
# print(f"Data extracted and saved to {output_filename}")

# ####################
# #few shot GPT-4
def promptGPT(directory):
    if 'HELICONE_API_KEY' not in os.environ:
        os.environ['HELICONE_API_KEY'] = 'sk-helicone-cp-nuxlzea-i3cuq6q-xpvlrga-pgbu4si'


    client = OpenAI(base_url="https://oai.hconeai.com/v1", api_key=os.environ['HELICONE_API_KEY'])

    objects = {}
    
    with open("extracted_items.json", 'r') as file:
        objects = json.load(file)

     # Prompt user for the number of new objects to create
    num_items = input("Enter the number of new items you want to generate: ")
        
    # objects selected for few-shot learning
    sample_items = json.dumps(objects[:5], indent=4) 
 
    # Create a detailed prompt with a few-shot example and define roles
    messages = [
        {'role': 'system', 'content': 'Generate a new item for a mystical game world. Include all necessary attributes such as name, description, examine text, and properties. Follow the style and depth of the given examples.'},
        {'role': 'user', 'content': 'Here are some examples of items:'},
        {'role': 'assistant', 'content': sample_items},
        {'role': 'user', 'content': f'Can you create {num_items} new items based on these examples?'}
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
    filename = "analysis_items.json"

    with open(filename, 'w') as file:
        json.dump(json.loads(gpt_response), file, indent=4)

promptGPT(directory)
