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

def save_code_as_str(filename):
    with open(filename , 'r') as file:  
        code_as_string = file.read()
    return code_as_string

def main():
    print("in main")
    background_story = """
    Set aboard the 'Orion' space station, the game revolves around escaping the station before it self-destructs in 60 minutes. 
    Key areas include the command center, crew quarters, engine room, and escape pods. 
    Important items are a space suit, keycards, a toolkit, and oxygen tanks. 
    Characters include the station's AI 'Helios', which provides hints and can control doors, and various crew members who can help or hinder the player.
    """

    action_list = """
    pick up space suit
    wear space suit
    pick up oxygen tank
    turn on oxygen tank
    search quarters for keycard
    take keycard
    exit crew quarters
    go to engine room
    use the toolkit to repair door
    enter command centre
    talk to Helios
    show keycard to Helios
    get door code from Helios
    use keycard on malfunctioning door
    put in door code
    enter escape pod area
    take second oxygen tank
    attach tank to space suit
    enter escape pod
    launch escape pod
    """

    game_locations = """
    {
        "Crew Quarters": "Starting location. Where the player can find the space suit, oxygen tank, and search for the keycard.",
        "Engine Room": "Where the player must use the toolkit to repair a door.",
        "Command Center": "Where the player can talk to Helios and get the door code.",
        "Escape Pod Bay": "The final location where the player will launch the escape pod.",
        "Helios Control Room": "A special room where Helios, the AI, is located.",
        "Storage Area": "Where the player can find the second oxygen tank to attach to the space suit."
    }
    """


    print(generate_blocks(background_story, action_list, game_locations))



def generate_blocks(background_story, action_list, game_locations, directory = ""):
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

    print("prompt input1 ", few_shot_prompt1)
    print("prompt input6 ", few_shot_prompt6)

    print("prompt result1 ", few_shot_result1)
    print("prompt result6 ", few_shot_result6)

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

    input_prompt = ("Below is a background story for a game, followed by steps to complete this game, "
    "and the locations it has, based on this,  generate 5 blocks, with code, that are relevant. DO NOT GO OUT OF CONTEXT. "
    "Background Story: {story} "
    "Steps: {steps} "
    "Locations: {locs} ").format(story = background_story, steps = action_list, locs = game_locations)


    messages += [{"role": "user", "content": input_prompt}]

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
    return gpt_response

if __name__ == "__main__":
    main()
