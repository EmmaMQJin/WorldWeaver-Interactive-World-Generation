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

def extract_locations(directory):
    locations = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            full_path = os.path.join(directory, filename)
            try:
                json_data = load_json(full_path)
                if 'locations' in json_data:
                    # Process each character to remove the 'location' key
                    for location in json_data['locations']:
                        if 'characters' in location:
                            location['characters'] = {} 
                        if 'items' in location:
                            location['items'] = {}    
                    locations.extend(json_data['locations'])
            except json.JSONDecodeError:
                print(f"Error decoding JSON from file {filename}")
            except Exception as e:
                print(f"An error occurred with file {filename}: {str(e)}")
    return locations

# Set the directory containing the JSON files
directory = '/Users/hardikjain/Documents/Spring 24/CIS-7000-Project/WorldWeaver-Interactive-World-Generation/games'  # Adjust the path to the directory of your JSON files
output_filename = 'extracted_locations.json'  # The filename for the output JSON

# Extract location data
extracted_locations = extract_locations(directory)

# Save the extracted data to a new JSON file in the same directory as this script
save_json(extracted_locations, output_filename)
print(f"Data extracted and saved to {output_filename}")

