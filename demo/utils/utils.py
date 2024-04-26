from openai import OpenAI
from utils.generate_locations_utils import *


def create_actions_playthrough_shots():
    shot_1_user = """Background story:
Princess of Action Castle has been locked away in a tower for nearly 20 years. The player is a simple peasant who is destined with greatness.
Initial state of player:
Inside an abandoned cottage.

Winning state of player:
The player successfully reigns.
"""
    shot_1_assistant = """take pole
catch fish with pole
pick rose
smell rose
get branch
give the troll the fish
hit guard with branch
get key
get candle
light lamp
light candle
read runes
get crown
unlock door
give rose to the princess
propose to the princess
wear crown
sit on throne
"""
    shot_2_user = """Background story:
Echo the Pigeon(the player) accidentally entered a cyberpunk world lurking with danger.
Initial state of player:
Woke up on an abandoned street in the city center.

Winning state of player:
The player successfully finds the machine to transport them to the original world in the secret lab or an evil organization.
"""
    shot_2_assistant = """Collect rusty key
Enter the nearby building
Avoid the stalking drone
Hack into the control room
Get electronic map
Navigate through the city
Gather discarded tech
Trade tech for cyber wings
Fly to rooftop platform
Meet the old hacker
Solve the old hacker's riddle
Receive secret lab coordinates
Avoid corporation security bots
Enter corporation building
Unlock secret lab with key
Hack into transportation machine
Enter the original world
"""
    shot_3_user = """Background Story:
Set aboard the 'Orion' space station, the game revolves around escaping the station before it self-destructs in 60 minutes. Key areas include the command center, crew quarters, engine room, and escape pods. Important items are a space suit, keycards, a toolkit, and oxygen tanks. Characters include the station's AI 'Helios', which provides hints and can control doors, and various crew members who can help or hinder the player.

Initial state:The player starts in the crew quarters with a basic toolkit. The space station's self-destruct sequence has been activated, and there are 15 minutes left. The path to the escape pods is currently blocked by a malfunctioning door.

End state:Based on the game's rules and mechanics described above, generate a sequence of actions the player needs to take to reach the escape pod and launch it. Provide Python code for any new actions or modifications needed to implement these steps in the game.
"""
    shot_3_assistant = """pick up space suit
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
    shot_4_user = """background story: 
flying unicorn

initial state:
cottage

winning state:
the flying unicorn star glider saves her sister moon dancer from ghosts
"""
    shot_4_assistant = """find magic feather
unlock cottage door
exit cottage 
find path to forest
enter the dark forest
gather glowing mushrooms
find the ancient well
drop feather into well
get enchanted wing armor
wear wing armor
fly upwards towards the moon
locate ghostly cloud
use glowing mushrooms to repel ghosts
find Moon Dancer
rescue Moon Dancer from ghosts
fly back down to Earth
return to cottage
celebrate victory with Moon Dancer
"""
    shots = [{"role": "user", "content": shot_1_user},
             {"role": "assistant", "content": shot_1_assistant},
             {"role": "user", "content": shot_2_user},
             {"role": "assistant", "content": shot_2_assistant},
             {"role": "user", "content": shot_3_user},
             {"role": "assistant", "content": shot_3_assistant},
             {"role": "user", "content": shot_4_user},
             {"role": "assistant", "content": shot_4_assistant},
    ]
    return shots

def generate_actions_playthrough(background_story, initial_state, winning_state):
    sys_prompt = """You are a helpful playthrough path finder for text adventure games.
The player needs to complete a series of actions in a specific order to win the game. 
Given the background story of the game, as well as the initial and winning state of the player, 
write a detailed list of sequential actions the player must take to progress through the game and ultimately succeed.
Each action should be  3-5 words, and should be unique and integral to advancing the storyline.
Include tasks like finding a specific object, opening a lock, solving a riddle, beating an adversary, and interacting with NPCs in meaningful ways.
"""
    user_prompt = f"""background story: 
{background_story}

initial state:
{initial_state}

winning state:
{winning_state}"""
    shots = create_actions_playthrough_shots()
    client = OpenAI()
    messages = [{"role": "system", "content": sys_prompt}]
    messages += shots
    messages += [{"role": "user", "content": user_prompt}]
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    model_output = completion.choices[0].message.content
    return model_output

def create_locations_list_shots():
    shot_1_user = """Background story:
Echo the Pigeon(the player) accidentally entered a cyberpunk world lurking with danger.

List of actions:
Collect rusty key
Enter the nearby building
Avoid the stalking drone
Hack into the control room
Get electronic map
Navigate through the city
Gather discarded tech
Trade tech for cyber wings
Fly to rooftop platform
Meet the old hacker
Solve the old hacker's riddle
Receive secret lab coordinates
Avoid corporation security bots
Enter corporation building
Unlock secret lab with key
Hack into transportation machine
Enter the original world
"""
    shot_1_assistant = """{
  "Dark Alley": "Starting location. This is where Echo the Pigeon finds the rusty key hidden among the garbage.",
  "Abandoned Building": "The nearby building that Echo must enter to escape the stalking drone.",
  "City Streets": "Where Echo must navigate through to avoid the stalking drone.",
  "Control Room": "A hidden location where Echo can hack into the system to obtain the electronic map.",
  "Tech Marketplace": "Where Echo can gather discarded tech and trade it for cyber wings.",
  "Rooftop Platform": "A high vantage point where Echo can meet the old hacker.",
  "Old Hacker's Hideout": "A secret location where Echo can solve the old hacker's riddle.",
  "Corporation Building": "The final location where Echo must enter to unlock the secret lab and transport back to the original world."
}
"""
    shot_2_user = """background story: 
flying unicorn

find magic feather
unlock cottage door
exit cottage 
find path to forest
enter the dark forest
gather glowing mushrooms
find the ancient well
drop feather into well
get enchanted wing armor
wear wing armor
fly upwards towards the moon
locate ghostly cloud
use glowing mushrooms to repel ghosts
find Moon Dancer
rescue Moon Dancer from ghosts
fly back down to Earth
return to cottage
celebrate victory with Moon Dancer
"""
    shot_2_assistant = """{
  "Enchanted Meadow": "Where the magic feather can be found.",
  "Cottage": "Starting location. Where the player must unlock the door and then later return to celebrate victory.",
  "Forest Clearing": "The player must find a path to enter the dark forest.",
  "Dark Forest": "Where the glowing mushrooms can be gathered.",
  "Ancient Well": "A mysterious location where the magic feather must be dropped to receive enchanted wing armor.",
  "Moonlit Sky": "Where the player must wear the enchanted wing armor and fly upwards towards the moon.",
  "Ghostly Cloud": "A mystical area where the player must use glowing mushrooms to repel ghosts.",
  "Moon Dancer's Labyrinth": "Where Moon Dancer is held captive by ghosts.",
  "Celestial Realm": "Where Moon Dancer resides and where the player must eventually return to celebrate victory."
}
"""
    shot_3_user = """Background Story:
Set aboard the 'Orion' space station, the game revolves around escaping the station before it self-destructs in 60 minutes. Key areas include the command center, crew quarters, engine room, and escape pods. Important items are a space suit, keycards, a toolkit, and oxygen tanks. Characters include the station's AI 'Helios', which provides hints and can control doors, and various crew members who can help or hinder the player.

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
    shot_3_assistant = """{
  "Crew Quarters": "Starting location. Where the player can find the space suit, oxygen tank, and search for the keycard.",
  "Engine Room": "Where the player must use the toolkit to repair a door.",
  "Command Center": "Where the player can talk to Helios and get the door code.",
  "Escape Pod Bay": "The final location where the player will launch the escape pod.",
  "Helios Control Room": "A special room where Helios, the AI, is located.",
  "Storage Area": "Where the player can find the second oxygen tank to attach to the space suit."
}
"""
    shots = [{"role": "user", "content": shot_1_user},
             {"role": "assistant", "content": shot_1_assistant},
             {"role": "user", "content": shot_2_user},
             {"role": "assistant", "content": shot_2_assistant},
             {"role": "user", "content": shot_3_user},
             {"role": "assistant", "content": shot_3_assistant},
    ]
    return shots

def generate_locations_to_use(background_story, actions_list):
    sys_prompt = """You are a helpful location generator for building a text adventure game.
Given the background story of the game and the entire list of actions the player needs to take in order to win the game, you should output a list of locations that you think is needed for the player to be able to take all the specified actions and for the game to operate properly, based on the list of actions the user needs to take.
Each location should be one specific place.
Mention which location is the starting location of the game in its description.
"""
    user_prompt = f"""Background story:
{background_story}

{actions_list}
"""
    shots = create_locations_list_shots()
    client = OpenAI()
    messages = [{"role": "system", "content": sys_prompt}]
    messages += shots
    messages += [{"role": "user", "content": user_prompt}]
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    model_output = completion.choices[0].message.content
    return json.loads(model_output)
    
    

def main():
    background_story = "talking cat"
    initial_state = "Talking cat wakes up in fairytopia"
    winning_state = "talking cat saves jerry mouse from flies"
    actions_list = generate_actions_playthrough(background_story, initial_state, winning_state)
    print(actions_list)
    locations_list_json = generate_locations_to_use(background_story, actions_list)
    print(locations_list_json)
    dict_to_json_file(locations_list_json, "test.json")




if __name__ == "__main__":
    main()