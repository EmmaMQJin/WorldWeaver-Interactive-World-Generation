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
directory = '/Users/manvikaul/Documents/Classwork/CIS-7000/project/shriyamanvi/WorldWeaver-Interactive-World-Generation/'  # Adjust the path to the directory of your JSON files
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
        os.environ['HELICONE_API_KEY'] = 'sk-helicone-cp-nivtfgy-pyhuewy-tzhkqva-vuhszwy'


    client = OpenAI(base_url="https://oai.hconeai.com/v1", api_key=os.environ['HELICONE_API_KEY'])

    with open(directory + "data/few-shot-examples/example-character.json", 'r') as file:
        examples = json.load(file)
    
    with open(directory+"data/approved_characters.json", "r") as file:
        generated = file.read()

    prompt = "You are a helpful main character generator for building a text adventure game for the following story:{story}. Generate one main character from this story in a JSON format. Character's inventory should be empty so remember to leave the values to the location and inventory keys empty. The JSON should be in the following JSON format:{form}. Do not generate any previously generated character.Generate a character you have never generated before. No value of any of the keys of the character should match any of the previously generated characters' values. None of the characters should match any character or share any value with any character from {gen}".format(story=stories[0],form=examples[0],gen = generated)

    with open("/Users/manvikaul/Documents/Classwork/CIS-7000/project/shriyamanvi/WorldWeaver-Interactive-World-Generation/data/few-shot-examples/example-character.json", 'r') as file:
        output = json.load(file)
 
    messages = [
        {'role': 'system', 'content': prompt},
        {'role': 'user', 'content': "The example story 1 is : {story}".format(story=stories[0])},
        {"role": "assistant", "content": json.dumps(examples[0])},
        {'role': 'user', 'content': "The example story 2 is : {story}".format(story=stories[1])},
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

    # filename = "analysis.json"
    # with open(filename, 'r+') as file:
    #     file.seek(0, 2)  # Move the file pointer to the end of the file
    #     if file.tell()!=0:
    #         file.seek(file.tell() - 1, 0)  # Move the file pointer to just before the last character
    #         file.write(',\n' + json.dumps(json.loads(gpt_response), indent=4) + '\n]')
    #     else:
    #         file.seek(0, 0)
    #         file.write(json.dumps(json.loads(gpt_response), indent=4) + '\n]')


    return json.loads(gpt_response)


def generate_npc(stories, directory):
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
        with open("/Users/manvikaul/Documents/Classwork/CIS-7000/project/shriyamanvi/WorldWeaver-Interactive-World-Generation//data/few-shot-examples/example-character.json", 'r') as file:
            examples = json.load(file)
    except FileNotFoundError:
        print("File not found.")
        return []

    npc_dict = {}
    for num in range(num_npc):
        print("Generating NPC:", num + 1)

        # Adjusting the index to avoid out of range errors
        story_index = num % len(stories)  # Loop back to the first story if there are fewer stories than NPCs
        example_index = num % len(examples)  # Similar wrap-around for examples
        
        with open(directory+"data/approved_characters.json", "r") as file:
            generated = file.read()

        prompt = ("You are a helpful character generator for building a text adventure game for the following story:{story}. Given the "
                  "background story of the game from the user and the main character of the game, generate one single NPC character "
                  "in JSON, formatted like the the following JSON format:{form}. Make sure to leave the fields for location and inventory empty. "
                  "Do not generate any previously generated character, i.e. the the generated charecter should not match any character or "
                  "share any value with any character from {gen}").format(story=stories[0],form=examples[0],gen = generated)
        messages = [
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': "The example story 1 is : {story}".format(story=stories[0])},
            {"role": "assistant", "content": json.dumps(examples[0])},
            {'role': 'user', 'content': "The example story 2 is : {story}".format(story=stories[1])},
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

        npc_content = response.choices[0].message.content
        print("Received NPC Content:", npc_content)
        try:
            npc_dict[str(num)] = json.loads(npc_content)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON for NPC {num}: {npc_content}")
            npc_dict[str(num)] = {"error": "Invalid JSON received"}

    return npc_dict



# def generate_npc(stories, directory):
#     print("here in npc")
#     num_npc = 4
#     num_npc = input("How many NPC charecters do you want to generate? CHoose a number between 0-10 (Default value is 4)")
#     print("num npc: ", num_npc)

#     client = OpenAI(base_url="https://oai.hconeai.com/v1", api_key=os.environ['HELICONE_API_KEY'])

#     output = {}

#     with open("/Users/manvikaul/Documents/Classwork/CIS-7000/project/shriyamanvi/WorldWeaver-Interactive-World-Generation/data/few-shot-examples/example-character.json", 'r') as file:
#         output = json.load(file)

#     with open("/Users/manvikaul/Documents/Classwork/CIS-7000/project/shriyamanvi/WorldWeaver-Interactive-World-Generation//data/few-shot-examples/example-character.json", 'r') as file:
#         examples = json.load(file)
 
#     npc_list = "{"
#     for num in range(int(num_npc)):
#         print("iter: ", (num))

#         prompt = "You are a helpful character generator for building a text adventure game. Given the background story of the game from the user and the main charecter of the game, generate one single NPC character in a JSON, formatted like the given examples. Make sure to leave the fields for location and inventory empty. "
#         messages = [
#             {'role': 'system', 'content': prompt},
#             {'role': 'user', 'content': "The background story is : f{story}".format(story=stories[0])},
#             {"role": "assistant", "content": json.dumps(examples[0])},
#             {'role': 'user', 'content': "The background story is : f{story}".format(story=stories[1])},
#             {"role": "assistant", "content": json.dumps(examples[1])}
#         ]

#         response = client.chat.completions.create(
#             model='gpt-4',
#             messages=messages,
#             temperature=1,
#             max_tokens=2048,
#             top_p=1.0,
#             frequency_penalty=0,
#             presence_penalty=0
#         )
#         print(response.choices[0].message.content)

#         npc_list += "\"{ind}\":".format(ind=num)
#         npc_list += response.choices[0].message.content

#         if num != int(num_npc)-1:
#             npc_list += ","

#     npc_list += "}" 
#     print("npc list: ", npc_list)

#     return json.loads(npc_list)



