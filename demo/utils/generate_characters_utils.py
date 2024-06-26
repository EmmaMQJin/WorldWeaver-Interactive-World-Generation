import json
import os
from openai import OpenAI
from random import randint
from frontend_utils import *

def load_json(filename):
    """ Load JSON data from a file """
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

def save_json(data, filename):
    """ Save data to a JSON file """
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

# def extract_characters(directory):
#     characters = []
#     for filename in os.listdir(directory):
#         if filename.endswith('.json'):
#             full_path = os.path.join(directory, filename)
#             try:
#                 json_data = load_json(full_path)
#                 if 'characters' in json_data:
#                     # Process each character to remove the 'location' key
#                     for character in json_data['characters']:
#                         if 'location' in character:
#                             character['location'] = {} 
#                     characters.extend(json_data['characters'])
#             except json.JSONDecodeError:
#                 print(f"Error decoding JSON from file {filename}")
#             except Exception as e:
#                 print(f"An error occurred with file {filename}: {str(e)}")
#     return characters

# # Set the directory containing the JSON files
# directory = ''  # Adjust the path to the directory of your JSON files
# output_filename = 'extracted_characters.json'  # The filename for the output JSON

# # Extract character data
# # extracted_characters = extract_characters(directory)

# # Save the extracted data to a new JSON file in the same directory as this script
# #save_json(extracted_characters, output_filename)
# #print(f"Data extracted and saved to {output_filename}")


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
    while True:
        try:
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
            result = json.loads(gpt_response)
            return result
        except:
            print("Error in generating main character --- trying again...")


def generate_npc_shots():
    shot1_user = f"""Please list of 3 potential characters for the location Enchanted Garden based on the information below:
    location name: 
    Enchanted Garden

    location description: 
    A lush, mystical grove shimmering with iridescent plants and the soft glow of ethereal lights.

    location purpose: 
    Where the player can find the magic hat and collect fairy dust.

    player:
    Whisker Wordsmith
    A clever and enchanting talking cat with bright, interested eyes and a black and white coat. Whisker Wordsmith, as he's known, has a nimble mind and a sharp tongue, using his words to guide, aid, or sometimes just entertain whoever he encounters.
    """

    shot1_assistant = """
[
    {
        "name": "Luna the Lightweaver",
        "description": "Luna is a delicate, luminous fairy known for her ethereal beauty and her ability to weave light into shimmering, protective cloaks. With wings that glisten like morning dew, she is a guardian spirit of the Enchanted Garden.",
        "persona": "I'm Luna, the fairy guardian of this mystical grove. By weaving light, I create enchanting illusions and barriers to protect this magical realm and its secrets. My presence ensures that only the worthy can access the garden's most hidden treasures.",
        "location": "",
        "goal": "To protect the magic hat and oversee the distribution of fairy dust to those who are deemed worthy.",
        "inventory": {},
        "properties": {
            "character_type": "fairy",
            "is_dead": false,
            "has_magic": true
        }
    },
    {
        "name": "Thornwick the Elder",
        "description": "Thornwick is a wise old tree spirit whose bark is etched with runes of ancient wisdom. His deep, resonant voice and slow, thoughtful movements make him a revered figure among the garden's mystical creatures.",
        "persona": "I am Thornwick, the ancient keeper of lore and wisdom in this enchanted land. My roots delve deep, binding the magic of the garden with the essence of the earth. I share tales and secrets with those who respect the harmony of nature.",
        "location": "",
        "goal": "To educate visitors about the history of the garden and its magical properties, ensuring that its secrets are respected and preserved.",
        "inventory": {},
        "properties": {
            "character_type": "spirit",
            "is_dead": false,
            "has_magic": true,
            "is_wise": true
        }
    },
    {
        "name": "Glitterpaw the Mischievous",
        "description": "Glitterpaw is a playful and cheeky pixie cat with a coat that sparkles like starlight and eyes full of mischief. Known for her tricks and games, she loves leading visitors on merry chases through the twilight mists of the garden.",
        "persona": "They call me Glitterpaw, the whimsical trickster of the Enchanted Garden. With a flick of my sparkling tail, I lead curious adventurers astray or into magical discoveries, depending on my mood. Laughter and surprise are my favorite creations.",
        "location": "",
        "goal": "To entertain and sometimes mislead visitors, testing their cleverness and sense of humor as they seek the garden's treasures.",
        "inventory": {},
        "properties": {
            "character_type": "cat",
            "is_dead": false
        }
    }
]
"""
    shot2_user = f"""Please list of 3 potential characters for the location Tech Marketplace based on the information below:
    location name: 
    Tech Marketplace

    location description: 
    A bustling, neon-lit bazaar brimming with vendors selling all manner of discarded and refurbished technology, creating a treasure trove for tech enthusiasts and scavengers alike.

    location purpose: 
    Where Echo can gather discarded tech and trade it for cyber wings.

    player:
    Echo the Pigeon
    An unexpected digital explorer who accidentally wandered into the dangerous cyberpunk world. Originally just an average pigeon, they now navigate unpredictable digital landscapes filled with covert corporations and unscrupulous hackers.
    """
    shot2_assistant = """
[
    {
        "name": "Circuit the Fixer",
        "description": "Circuit is a skilled engineer known for her ability to repair and repurpose any piece of technology into something unique and valuable. With a workshop filled with blinking lights and scattered gadgets, she is a central figure in the Tech Marketplace.",
        "persona": "I'm Circuit, the marketplace's master engineer. I transform broken tech into innovative marvels, making old things new and useful.",
        "location": "",
        "goal": "To create innovative tech solutions and trade unique items that help Echo in gathering tech for cyber wings.",
        "inventory": {},
        "properties": {
            "character_type": "human",
            "is_dead": false,
            "is_skilled": true
        }
    },
    {
        "name": "Volt the Trader",
        "description": "Volt is a charismatic vendor with a knack for spotting valuable tech among heaps of electronic waste. His stall is a popular stop for collectors and tech scavengers looking for rare finds.",
        "persona": "I'm Volt, your friendly tech trader. I have an eye for hidden tech treasures and a deal always ready to be struck.",
        "location": "",
        "goal": "To supply Echo with essential components for cyber wings in exchange for interesting tech pieces.",
        "inventory": {},
            "properties": {
            "character_type": "human",
            "is_dead": false,
        }
    },
    {
        "name": "Spark the Informant",
        "description": "Spark is a sly, street-smart informant who deals in information as much as in hardware. Always cloaked in a digital visor, he knows the latest buzz and the deepest secrets of the digital realm.",
        "persona": "Call me Spark. I trade in whispers and wires, knowing more about this digital jungle than anyone else.",
        "location": "",
        "goal": "To provide Echo with vital information and guidance on where to find the best discarded tech for crafting cyber wings.",
        "inventory": {},
            "properties": {
            "character_type": "human",
            "is_dead": false,
            "is_smart": true
        }
    }
]

"""
    shots = [{"role": "user", "content": shot1_user},
             {"role": "assistant", "content": shot1_assistant},
             {"role": "user", "content": shot2_user},
             {"role": "assistant", "content": shot2_assistant}]
    return shots

def generate_npcs_round(location_name, location_description, location_purpose, background_story, main_character, existing_npcs):
    client = OpenAI(base_url="https://oai.hconeai.com/v1", api_key=os.environ['HELICONE_API_KEY'])

    prompt = "You are a helpful character generator for building a text adventure game."
    prompt += "Your job is to generate NPC characters in a given location."
    prompt += f"Given the location's name, description, purpose, as well as the description of the player of the game from the user,"
    prompt += "you should generate a list of 3 suitable and purposeful NPCs that should be in this location."
    prompt += "you should espeially focus on aligning with the location's given purpose."
    prompt += "Output the NPCs as a list of JSON objects."
    prompt += "You should always populate name, description, persona, goal, and properties of an NPC character."
    prompt += "You should always leave the location and inventory of each character empty."
    prompt += f"Here are the NPCs you have already before and SHOULD NOT generate again: {existing_npcs}"

    user_prompt = f"""Please list of 3 potential characters for the location {location_name} based on the information below:
    location name: 
    {location_name}

    location description: 
    {location_description}

    location purpose: 
    {location_purpose}

    player:
    {main_character["name"]}
    {main_character["description"]}
    """

    messages = [{'role': 'system', 'content': prompt}]
    messages += generate_npc_shots()
    messages += [{"role": "user", "content": user_prompt}]
    while True:
        try:
            response = client.chat.completions.create(
                model='gpt-4',
                messages=messages,
                temperature=1,
                max_tokens=2048,
                top_p=1.0,
                frequency_penalty=0,
                presence_penalty=0
            )

            npc_content = json.loads(response.choices[0].message.content)
            return npc_content
        except:
            print("Error in NPC generation --- trying again...")



def generate_npc_in_location(location_name, location_description, location_purpose, background_story, main_character, all_characters):

    already_generated_npcs = []
    all_selected_npcs = []
    while True:
        location_npcs = generate_npcs_round(location_name, location_description, location_purpose, background_story,
                                            main_character, already_generated_npcs)
        render_items_choices(location_npcs)
        already_generated_npcs += location_npcs
        selected_npcs_in_round = get_selected_items(location_npcs)
        all_selected_npcs += selected_npcs_in_round
        render_selected_items(all_selected_npcs)
        if user_submit():
            break
    # Append generated items to the location's 'items' field
    npcs_dict = {}
    for _, npc in enumerate(all_selected_npcs):
        npc['location'] = location_name
        npcs_dict[npc['name']] = npc

    all_characters += all_selected_npcs

    return npcs_dict, all_characters
