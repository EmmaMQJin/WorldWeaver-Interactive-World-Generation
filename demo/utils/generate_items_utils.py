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
def generate_object(directory):
    if 'HELICONE_API_KEY' not in os.environ:
        os.environ['HELICONE_API_KEY'] = 'sk-helicone-cp-nuxlzea-i3cuq6q-xpvlrga-pgbu4si'


    client = OpenAI(base_url="https://oai.hconeai.com/v1", api_key=os.environ['HELICONE_API_KEY'])


     # Load location data
    with open(f"../data/test_generations/all_the_locations.json", 'r') as file:
        locations = json.load(file)

    # Load extracted items for few-shot learning
    with open(f"../data/extracted_items.json", 'r') as file:
        extracted_items = json.load(file)
    
     # Sample of extracted items for the few-shot example
    sample_items = json.dumps(extracted_items[:5], indent=4)

    for location in locations:
        print(f"Generating items for: {location['name']}")

        # Prompt user for the number of new objects to create
        num_items = input(f"Enter the number of new items you want to generate for {location['name'].strip()}:")

        # Create a detailed prompt with location context and few-shot examples
        messages = [
            {'role': 'system', 'content': f'Generate {num_items} new items for the mystical setting of {location["name"].strip()}.Include all necessary attributes such as name, description, examine text, and properties. Follow the style and depth of the given examples.'},
            {'role': 'user', 'content': 'Here are some examples of items:'},
            {'role': 'assistant', 'content': sample_items},
            {'role': 'user', 'content': f'Please create {num_items} new items based on these examples for the location: {location["description"].strip()}'}
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
        new_items = json.loads(gpt_response)
        # Append generated items to the location's 'items' field
        location['items'] = new_items

         # Save the updated location data back to the same file
    with open(f"../data/test_generations/all_the_locations.json", 'w') as file:
        json.dump(locations, file, indent=4)


# Example directory to pass
# generate_object(directory)