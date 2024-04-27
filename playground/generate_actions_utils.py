import json
import os
from openai import OpenAI

client = OpenAI(base_url="https://oai.hconeai.com/v1", api_key=os.environ['HELICONE_API_KEY'])
system_prompt_unique_actions = """
Find the unique actions from the list of actions i give you.
If you find actions that are synonymous or similar in meaning, add only one of them to your list and write the others as alias in the format:
get [alias: procure, retrieve]
"""
user_prompt_one = """
go to the amusement park
get the beanie
plant the rose
go to the palace
procure the dragon tear
retreive pegasus
"""
assistant_prompt_one = """
go 
get [alias: procure, pegasus]
plant
"""
user_prompt_two = """
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
system_prompt = ("You are a helpful assistant that will create a python class for the action given to you."+
"""
The class must have the following functions: def __init__(self, game, command: str):,def check_preconditions(self) -> bool: and def apply_effects(self):
No other extra functions must be added.
The aliases part should be added as a class member for the associated action like so : 
class get:

ACTION_ALIASES = ["procure", "retrieve"]

Remember to return False if any precondition is not met and return True at the end of the precondition function if all the conditions are met

__init__ and apply_effects functions will not have any return statements.

The items, characters and locations already generated will have the following JSON structures(Make sure to NOT include any property outside of what is given in the JSONs below):

JSON structure for an item:
{
    "name": "",
    "description": "",
    "examine_text": "",
    "properties": {
        "is_container": ,
        "is_drink": ,
        "is_food": ,
        "is_gettable": ,
        "is_surface": ,
        "is_weapon": ,
        "is_wearable": 
    }

JSON structure for a character:
    {
    "name": "",
    "description": "",
    "persona": "",
    "location": {},
    "goal": "",
    "inventory": {}
}
JSON structure for location:
{
    "name": "",
    "description": "",
    "connections": {
    },
    "travel_descriptions": {
    },
    "blocks": {},
    "items": {},
    "characters": {},
    "has_been_visited": ,
    "commands": [],
    "properties": {}
}

game JSON structure:
{

}
    """
)

user_example_prompt_one = "get [alias: procure, retrieve]"   
user_example_prompt_two = "eat [alias: consume, ingest]"
user_example_prompt_three = "cook"
user_example_prompt_four = "unlock door"

assistant_example_prompt_one = """
class Get(base.Action):
    ACTION_NAME = "get"
    ACTION_DESCRIPTION = "Get something and add it to the inventory"
    ACTION_ALIASES = ["take"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.location = self.character.location
        self.item = self.parser.match_item(command, self.location.items)

    def check_preconditions(self) -> bool:
       
         #Preconditions:
         #* The item must be matched.
         #* The character must be at the location
         #* The item must be at the location
         #* The item must be gettable
        
        if not self.was_matched(self.item, "I don't see it."):
            message = "I don't see it."
            self.parser.fail(message)
            return False
        if not self.location.here(self.character):
            message = "{name} is not here.".format(name=self.character.name)
            self.parser.fail(message)
            return False
        if not self.location.here(self.item):
            message = "There is no {name} here.".format(name=self.item.name)
            self.parser.fail(message)
            return False
        if not self.item.get_property("gettable"):
            error_message = "{name} is not {property_name}.".format(
                name=self.item.name.capitalize(), property_name="gettable"
            )
            self.parser.fail(error_message)
            return False
        return True

    def apply_effects(self):
        
        #Get's an item from the location and adds it to the character's
        #inventory, assuming preconditions are met.
        self.location.remove_item(self.item)
        self.character.add_to_inventory(self.item)
        description = "{character_name} got the {item_name}.".format(
            character_name=self.character.name, item_name=self.item.name
        )
        self.parser.ok(description)
"""
assistant_example_prompt_two="""
class Eat(base.Action):
    ACTION_NAME = "eat"
    ACTION_DESCRIPTION = "Eat something"

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.item = self.parser.match_item(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched item
        #* The item must be food
        
        #* The food must be in character's inventory
        
        if not self.was_matched(self.item):
            return False
        elif not self.item.get_property("is_food"):
            description = "That's not edible."
            self.parser.fail(description)
            return False
        elif not self.character.is_in_inventory(self.item):
            description = "You don't have it."
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Removes the food from the inventory so that it has been consumed.
        #* Causes the character's hunger to end
        #* Describes the taste (if the "taste" property is set)
        #* If the food is poisoned, it causes the character to die.
        self.character.remove_from_inventory(self.item)
        self.character.set_property("is_hungry", False)
        description = "{name} eats the {food}.".format(
            name=self.character.name.capitalize(), food=self.item.name
        )

        if self.item.get_property("taste"):
            description += " It tastes {taste}".format(
                taste=self.item.get_property("taste")
            )

        if self.item.get_property("is_poisonous"):
            self.character.set_property("is_dead", True)
            description += " The {food} is poisonous. {name} died.".format(
                food=self.item.name, name=self.character.name.capitalize()
            )
        self.parser.ok(description)
"""
assistant_example_prompt_three = """
    class Cook(actions.Action):
        ACTION_NAME = 'cook'
        ACTION_DESCRIPTION = 'Cook some food'

        def __init__(self, game, command):
            super().__init__(game)
            self.command = command
            self.character = self.parser.get_character(command)
            self.food = self.parser.match_item(
                command, self.parser.get_items_in_scope(self.character)
            )

        def check_preconditions(self) -> bool:
            if not self.food:
                self.parser.fail("No food found")
            if not self.food.get_property("is_food"):
                self.parser.fail(f"{self.food.name} is not food")
                return False
            return True

        def apply_effects(self):
            self.food.set_property("taste", "deliciously cooked")
            self.parser.ok(f"You cooked the {self.food.name}")

"""
assistant_example_prompt_four = """
    class Unlock_Door(actions.Action):
    ACTION_NAME = "unlock door"
    ACTION_DESCRIPTION = "Unlock a door with a key"
    ACTION_ALIASES = []
    
    def __init__(self, game, command):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.key = self.is_in_inventory(self.character, key)
        self.door = door  

    def check_preconditions(self) -> bool:
        if self.door and (self.door.location == self.character.location) and (self.door.get_property("is_locked") is True) and (self.key is True):
            print("unlocking door")
            return True
        return False

    def apply_effects(self):
        if self.door and (self.door.location == self.character.location) and (self.door.get_property("is_locked") is True) and (self.key is True):
            self.door.set_property("is_locked", False)
"""
messages = [
    {'role': 'system', 'content': system_prompt_unique_actions},
    {'role': 'user', 'content': user_prompt_one},
    {'role': 'assistant', 'content': assistant_prompt_one},
    {'role': 'user', 'content': user_prompt_two}
]
response = client.chat.completions.create(
    model='gpt-4',
    messages=messages,
    temperature=0.1,
    max_tokens=2048,
    top_p=1.0,
    frequency_penalty=0,
    presence_penalty=0
)
gpt_response = response.choices[0].message.content
print(gpt_response)

locations= ["Enchanted Meadow: Starting location. Where the magic feather can be found.",
"Cottage:The initial location where the player must unlock the door and then later return to celebrate victory.",
"Forest Clearing:The player must find a path to enter the dark forest.",
"Dark Forest:Where the glowing mushrooms can be gathered.",
"Ancient Well:A mysterious location where the magic feather must be dropped to receive enchanted wing armor.",
"Moonlit Sky:Where the player must wear the enchanted wing armor and fly upwards towards the moon.",
"Ghostly Cloud:A mystical area where the player must use glowing mushrooms to repel ghosts.",
"Moon Dancer's Labyrinth:Where Moon Dancer is held captive by ghosts.",
"Celestial Realm:Where Moon Dancer resides and where the player must eventually return to celebrate victory."]

items = [
    "Magic Feather: Found here, this feather is key to unlocking mystical events; Guide Stone: Offers hints to find the path leading to the Forest Clearing.",
    "Ancient Key: Used to unlock the cottage door; Victory Banner: Appears after victory to celebrate with Moon Dancer.",
    "Pathfinder Compass: Reveals the hidden entrance to the Dark Forest.",
    "Glowing Mushrooms: Can be collected here, used later to repel ghosts; Forest Map: Helps navigate through the dense and dark forest.",
    "Enchanted Bucket: Used to retrieve the enchanted wing armor from the well after dropping the feather.",
    "Wing Armor: Acquired from the well, necessary for flight; Stardust Cloak: Enhances the ability to fly towards the moon.",
    "Mushroom Pouch: Contains the glowing mushrooms collected earlier to repel ghosts; Spirit Lantern: Helps illuminate and navigate through the ghostly cloud.",
    "Rescue Rope: Essential for freeing Moon Dancer from the ghosts; Labyrinth Map: Aids in navigating the complex pathways of the labyrinth.",
    "Celestial Crown: Symbolizes the successful rescue and alliance with Moon Dancer; Festive Fireworks: Used to celebrate the victory with Moon Dancer."
]
actions = gpt_response.split("\n")

for action in actions:
    messages = [
    {'role': 'system', 'content': system_prompt},
    {'role': 'user', 'content': user_example_prompt_one},
    {'role': 'assistant', 'content': assistant_example_prompt_one},
    {'role': 'user', 'content': user_example_prompt_two},
    {'role': 'assistant', 'content': assistant_example_prompt_two},
    {'role': 'user', 'content': user_example_prompt_three},
    {'role': 'assistant', 'content': assistant_example_prompt_three},
    {'role': 'user', 'content': user_example_prompt_four},
    {'role': 'assistant', 'content': assistant_example_prompt_four},
    {'role': 'user', 'content': f"{action}"}
    ]
    response_code = client.chat.completions.create(
        model='gpt-4',
        messages=messages,
        temperature=0.1,
        max_tokens=2048,
        top_p=1.0,
        frequency_penalty=0,
        presence_penalty=0
    )
    gpt_response_code = response_code.choices[0].message.content
    print(gpt_response_code)

