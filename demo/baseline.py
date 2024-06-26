from openai import OpenAI
import os
import json
from utils.json_utils import *

system_prompt = """You are a helpful text adventure game generator. Given the background story, starting state, and winning state of the game, you should generate a game JSON in the following example format:
{
    "player": "",
    "start_at": "Example Location",
    "game_history": [],
    "game_over": false,
    "game_over_description": null,
    "characters": [
        {
            "name": "Example Character",
            "description": "",
            "persona": "",
            "location": "",
            "goal": "",
            "inventory": {...}
        },
        ...
    ],
    "locations": [
        {
            "name": "Example Location",
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
                    "name": "Example Character",
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
The ... means you should expand with more items.
Be sure to populate all empty string fields. Each location should have NPC characters and items in it.
Each character should have objects in their inventory.
The player needs to be an existing character.
Generate at least 5 locations and 5 characters."""

user_prompt = """background story: the player is a talking cat
starting state: player in kitchen
winning state: player at the top of a mountain"""

client = OpenAI(base_url="https://oai.hconeai.com/v1", api_key=os.environ['HELICONE_API_KEY'])
messages = [{"role": "system", "content": system_prompt}]
messages += [{"role": "user", "content": user_prompt}]
completion = client.chat.completions.create(
    model="gpt-4",
    messages=messages
)
model_output = completion.choices[0].message.content
with open("data/test_generations/baseline.txt", 'w') as file:
    file.write(model_output)
try:
    model_output_dict = json.loads(model_output)
except Exception as e:
    print("JSON syntax error: ", e)
dict_to_json_file(model_output_dict, "data/test_generations/baseline.json")