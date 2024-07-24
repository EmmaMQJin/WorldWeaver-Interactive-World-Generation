from openai import OpenAI
import os
from utils.json_utils import *

###########################################################################################
background_story = "In the eccentric city of Cheddarville, where cheese is the main currency, the Grand Cheese Wheel has rolled away, causing an economic meltdown. The town’s most lactose-intolerant resident must navigate a world of cheese to bring it back and restore balance."
initial_state = "The Grand Cheese Wheel has rolled away, causing an economic meltdown in Cheddarville, and the town's most lactose-intolerant resident is reluctantly tasked with retrieving it."
winning_state = "The player successfully returns the Grand Cheese Wheel to Cheddarville's town square, restoring economic stability and earning the town's gratitude."
###########################################################################################

system_prompt = """You are a helpful text adventure game generator. Given the background story, starting state, and winning state of the game, you should generate a game JSON in the following example format:
{
    "player": "Example Character 1",
    "start_at": "Example Location 1",
    "game_history": [],
    "game_over": false,
    "game_over_description": null,
    "characters": [
        {
            "name": "Example Character 1",
            "description": "",
            "persona": "",
            "location": "",
            "goal": "",
            "inventory": {...}
        },
        {
            "name": ....
            ....
        },
        ....
    ],
    "locations": [
        {
            "name": "Example Location 1",
            "description": "",
            "background": "",
            "commands": [],
            "properties": {},
            "blocks": {},
            "travel_descriptions": {
                "east": "",
                ...
            },
            "connections": {
                "east": "",
                ...
            },
            "items": {
                "Example Location Item": {
                    "name": "Example Location Item",
                    "description": "",
                    "examine_text": "",
                    "properties": {
                        "is_container": false,
                        "is_drink": false,
                        "is_food": false,
                        "is_gettable": true,
                        "is_surface": false,
                        "is_weapon": true,
                        "is_wearable": false
                    },
                    "location": "Example Location"
                },
                ...
            },
            "characters": {
                "Example Character": {
                    "name": "Example Character 2",
                    "description": "",
                    "persona": "",
                    "location": "",
                    "goal": "",
                    "inventory": {
                        "Example Inventory Item": {
                            "name": "",
                            "description": "",
                            "examine_text": "",
                            "properties": {
                                "is_container": false,
                                "is_drink": false,
                                "is_food": true,
                                "is_gettable": true,
                                "is_surface": false,
                                "is_weapon": false,
                                "is_wearable": false
                            },
                            "commands": []
                        },
                        ...
                    }
                },
                ...
            },
            "has_been_visited": false,
        },
        ...
    ],
    "actions": []
}
The ... means you should expand with more actual items.

IMPORTANT RULES TO ABIDE BY:
- Be sure to populate all empty string fields
- DO NOT put any comments
- Generate 5 to 8 locations
- The player should be the first character in the "characters":[...] list
- Generate at least one character (NPC) in each location
- Generate at least 3 Inventory Items for each character
- Generate at least 3 Location Items in each location

Make sure you are GENERATING ENOUGH OF EVERYTHING

"""

user_prompt = "Background Story:" + background_story + "\nInitial State:" + initial_state + "\nWinning State:" + winning_state

client = OpenAI(base_url="https://oai.hconeai.com/v1", api_key=os.environ['HELICONE_API_KEY'])
messages = [{"role": "system", "content": system_prompt}]
messages += [{"role": "user", "content": user_prompt}]
for _ in range(7):
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    model_output = completion.choices[0].message.content
    messages += [{"role": "assistant", "content": model_output}]
    messages += [{"role": "user", "content": "generate more locations and NPCs as well as thier items"}]

    with open("data/test_generations/baseline.txt", 'a') as file:
        file.write(model_output)