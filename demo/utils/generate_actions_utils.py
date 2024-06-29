import json
import os
import ast
from openai import OpenAI

def write_list_to_file(items, filename):
    """
    Writes each item in a list to a file, with each item on a new line.

    Args:
    items (list of str): The list of strings to write to the file.
    filename (str): Path to the file where the data should be written.
    """
    try:
        with open(filename, 'w') as file:
            for item in items:
                file.write(f"{item}\n")
        #print(f"Data successfully written to {filename}")
    except IOError as e:
        print(f"An error occurred while writing to the file: {e}")



def find_class_name(code):
    """
    Parses Python code to find the first class name.
    """
    try:
        tree = ast.parse(code)
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                return node.name
        raise ValueError("No class definition found in the code.")
    except SyntaxError as e:
        raise ValueError(f"Error parsing code: {e}")

def append_code_to_file(folder, code, filename):
    """
    Appends code to a Python file named 'actions.py' in the specified folder, or creates it if it doesn't exist.
    """
    base_path = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script
    full_path = os.path.join(base_path, folder)
    os.makedirs(full_path, exist_ok=True)  # Create the folder if it doesn't exist
    file_path = os.path.join(full_path, filename+".py")
    with open(file_path, 'a') as file:  # Open the file in append mode
        file.write(code.strip() + '\n')  # Append the code to the file
    print(f"Code appended to: {file_path}")


def read_from_file(filename):
    """
    Reads contents from file
    """
    try:
        with open(filename, 'r') as file:
            return file.read()
    except IOError as e:
        print(f"An error occurred while reading the file: {e}")
        return None

def generate_action_class(action_list):
    client = OpenAI(base_url="https://oai.hconeai.com/v1", api_key=os.environ['HELICONE_API_KEY'])
    system_prompt_unique_actions = """You are an extractor for valid actions for a text adventure game.
    Given a list of actions that the player needs to take to win the game, extract a list of unique and distinct single-word action verbs from the list.
    If any action verbs are in this list: [Go, Get, Drop, Inventory, Give, Unlock Door, Examine], or are synonyms of these actions, skip them and DO NOT extract them.
    Note that in this step, each extracted action verb should be unique. If synonymous action verbs exist in the given list,
    choose one action verb to be the primary one and put the synonymous action verbs in brackets after the primary action verb, prefixed by "alias:", like this: "get [alias: procure, retrieve]"
    Then, for each action verb you extracted, if the action verb has some commonly-used synonyms (consult the Oxford Dictionary for verification), add fewer than 3 of those to the alias section as well.
    Make sure to include ONLY ONE primary action for each group of synonyms, with all other synonymous actions listed as aliases.
    """
    user_prompt_one = """
    go to the amusement park
    get the beanie
    plant the rose
    go to the palace
    procure the dragon tear
    heal pegasus

    DO NOT EXTRACT:
    [Go, Get, Drop, Inventory, Give, Unlock Door, Examine]
    """
    assistant_prompt_one = """
    plant
    heal [alias: cure]
    """
    user_prompt_two = f"{action_list}\n" + """\nDO NOT EXTRACT:
    [Go, Get, Drop, Inventory, Give, Unlock Door, Examine]"""
   
    system_prompt = """
    You are a game actions developer for a text adventure game. Given an action (and possibly its aliases in the game) from the user,
    your task is to write a Python class to represent that action.

    Remember, this Python class is part of the game and the game needs to be playable, so make sure to always stick to the information you are given
    from the user, and also always double check the logic of each method.

    The class you create should inherit from the base class actions.Action and include the following methods:

    1. __init__: Initialize with parameters (self, game, command: str).
    2. check_preconditions: This method should return a boolean value. Return False if any preconditions are not met, otherwise return True if all conditions are met. The method signature should be def check_preconditions(self) -> bool:.
    3. apply_effects: Implement this method to apply the effects of the action. It should not return any value. The method signature should be def apply_effects(self):.
 
    The class should also include a class member for aliases of the action word, using the following format:
    ACTION_ALIASES = ["procure", "retrieve"]

    Additional Guidelines:
    - Do not add any functions other than the ones specified.
    - Use the following JSON structures to guide your implementation. Ensure properties match exactly with no additions:
    - Item Structure:
        {
        "name": "",
        "description": "",
        "examine_text": "",
        "properties": {
            "is_container": false,
            "is_drink": false,
            "is_food": false,
            "is_gettable": false,
            "is_surface": false,
            "is_weapon": false,
            "is_wearable": false
        }
        }
    - Character Structure:
        {
        "name": "",
        "description": "",
        "persona": "",
        "location": {},
        "goal": "",
        "inventory": {}
        }
    - Location Structure:
        {
        "name": "",
        "description": "",
        "connections": {},
        "travel_descriptions": {},
        "blocks": {},
        "items": {},
        "characters": {},
        "has_been_visited": false,
        "commands": [],
        "properties": {}
        }

    Every character has access to the following functions, so call these functions if you need to apply any function to characters, do not create functions/methods of your own:

    def add_to_inventory(self, item):
        
        Add an item to the character's inventory.
        
        if item.location is not None:
            item.location.remove_item(item)
            item.location = None
        self.inventory[item.name] = item
        item.owner = self

    def is_in_inventory(self, item):
        
        Checks if a character has the item in their inventory
        
        return item.name in self.inventory

    def remove_from_inventory(self, item):
        
        Removes an item to a character's inventory.
        
        item.owner = None
        self.inventory.pop(item.name)

    You can use the following functions for locations,  do not create methods/functions of your own:
    def add_connection(
        self, direction: str, connected_location, travel_description: str = ""
    ):
        
        Add a connection from the current location to a connected location.
        Direction is a string that the player can use to get to the connected
        location.  If the direction is a cardinal direction, then we also
        automatically make a connection in the reverse direction.
        
        direction = direction.lower()
        self.connections[direction] = connected_location
        self.travel_descriptions[direction] = travel_description
        if direction == "north":
            connected_location.connections["south"] = self
            connected_location.travel_descriptions["south"] = ""
        if direction == "south":
            connected_location.connections["north"] = self
            connected_location.travel_descriptions["north"] = ""
        if direction == "east":
            connected_location.connections["west"] = self
            connected_location.travel_descriptions["west"] = ""
        if direction == "west":
            connected_location.connections["east"] = self
            connected_location.travel_descriptions["east"] = ""
        if direction == "up":
            connected_location.connections["down"] = self
            connected_location.travel_descriptions["down"] = ""
        if direction == "down":
            connected_location.connections["up"] = self
            connected_location.travel_descriptions["up"] = ""
        if direction == "in":
            connected_location.connections["out"] = self
            connected_location.travel_descriptions["out"] = ""
        if direction == "out":
            connected_location.connections["in"] = self
            connected_location.travel_descriptions["in"] = ""

    def get_connection(self, direction: str):
        return self.connections.get(direction, None)

    def get_direction(self, location):
        for k, v in self.connections.items():
            if v == location:
                return k
        else:
            return None

    def here(self, thing: Thing, describe_error: bool = True) -> bool:
        
        Checks if the thing is at the location.
        
        # The character must be at the location
        if not thing.location == self:
            return False
        else:
            return True

    def get_item(self, name: str):
        
        Checks if the thing is at the location.
        
        # The character must be at the location
        return self.items.get(name, None)

    def add_item(self, item):
        
        Put an item in this location.
        
        self.items[item.name] = item
        item.location = self
        item.owner = None

    def remove_item(self, item):
        
        Remove an item from this location (for instance, if the player picks
        it up and puts it in their inventory).
        
        self.items.pop(item.name)
        item.location = None

    def add_character(self, character):
        
        Put a character in this location.
        
        self.characters[character.name] = character
        character.location = self

    def remove_character(self, character):
        
        Remove a character from this location.
        
        self.characters.pop(character.name)
        character.location = None

    def is_blocked(self, direction: str) -> bool:
        
        Check to if there is an obstacle in this direction.
        
        if direction not in self.blocks:  # JD logical change
            return False
        block = self.blocks[direction]
        return block.is_blocked()

    def get_block_description(self, direction: str):
        
        Check to if there is an obstacle in this direction.
        
        if direction not in self.blocks:
            return ""
        else:
            block = self.blocks[direction]
            return block.description


    """
    user_example_prompt_one = "cook"
    user_example_prompt_two = "eat [alias: consume, ingest]"
    user_example_prompt_three = "Attack [alias: hit, assault]"   
    user_example_prompt_four = "Unlock"

    assistant_example_prompt_three = """
class Attack(actions.Action):
    ACTION_NAME = "attack"
    ACTION_DESCRIPTION = "Attack someone with a weapon"
    ACTION_ALIASES = ["hit"]

    def __init__(self, game, command: str):
        super().__init__(game)
        attack_words = ["attack", "hit"]
        self.attacker = self.parser.get_character(
            command, hint="attacker", split_words=attack_words, position="before"
        )
        self.victim = self.parser.get_character(
            command, hint="victim", split_words=attack_words, position="after"
        )
        self.weapon = self.parser.match_item(
            command, self.attacker.inventory, hint="weapon"
        )

    def check_preconditions(self) -> bool:
        
        Preconditions:
        * There must be an attacker and a victim
        * They must be in the same location
        * There must be a matched weapon
        * The attacker must have the weapon in their inventory
        * The weapon have the property 'is_weapon'
        * The victim must not already be dead or unconscious
        
        if not self.was_matched(self.attacker):
            description = "The attacker couldn't be found."
            self.parser.fail(description)
            return False
        if not self.was_matched(self.victim):
            description = "The character to attack wasn't matched."
            self.parser.fail(description)
            return False
        if not self.attacker.location.here(self.victim):
            description = "The two characters must be in the same location."
            self.parser.fail(description)
            return False
        if not self.was_matched(
            self.weapon,
            error_message="{name} doesn't have a weapon.".format(
                name=self.attacker.name
            ),
        ):
            return False
        if not self.attacker.is_in_inventory(self.weapon):
            description = "{name} doesn't have the {weapom}.".format(
                name=self.attacker.name, weapon=self.weapon.name
            )
            self.parser.fail(description)
            return False
        if not self.weapon.get_property("is_weapon"):
            description = "{item} is not a weapon".format(item=self.weapon.name)
            self.parser.fail(description)
            return False
        if self.victim.get_property("is_unconscious"):
            description = "{name} is already unconscious".format(name=self.victim.name)
            self.parser.fail(description)
            return False
        if self.victim.get_property("is_dead"):
            description = "{name} is already dead".format(name=self.victim.name)
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        Effects:
        * If the victim is not invulerable to attacks
        ** Knocks the victim unconscious
        ** The victim drops all items in their inventory
        * If the weapon is fragile then it breaks
        
        description = "{attacker} attacked {victim} with the {weapon}.".format(
            attacker=self.attacker.name,
            victim=self.victim.name,
            weapon=self.weapon.name,
        )
        self.parser.ok(description)

        if self.weapon.get_property("is_fragile"):
            description = "The fragile weapon broke into pieces."
            self.attacker.remove_from_inventory(self.weapon)
            self.parser.ok(description)

        if self.victim.get_property("is_invulerable"):
            description = "The attack has no effect on {name}.".format(
                name=self.victim.name
            )
            self.parser.ok(description)
        else:
            # the victim is knocked unconscious
            self.victim.set_property("is_unconscious", True)
            description = "{name} was knocked unconscious.".format(
                name=self.victim.name.capitalize()
            )
            self.parser.ok(description)

            # the victim drops their inventory
            items = list(self.victim.inventory.keys())
            for item_name in items:
                item = self.victim.inventory[item_name]
                command = "{victim} drop {item}".format(
                    victim=self.victim.name, item=item_name
                )
                drop = Drop(self.game, command)
                if drop.check_preconditions():
                    drop.apply_effects()
    """
    assistant_example_prompt_two="""
class Eat(actions.Action):
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
    assistant_example_prompt_one = """
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
class Unlock(actions.Action):
    ACTION_NAME = "unlock"
    ACTION_DESCRIPTION = "Unlock something"

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.item = self.parser.match_item(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched item
        #* The item must be lockable
        #* The item must be locked
        #* The character must have a key in their inventory
        
        if not self.was_matched(self.item):
            return False
        if not self.item.get_property("is_lockable"):
            description = "That's not something you can unlock."
            self.parser.fail(description)
            return False
        if not self.item.get_property("is_locked"):
            description = "It's already unlocked."
            self.parser.fail(description)
            return False
        if not self.character.has_key():
            description = "You don't have a key."
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Unlocks the item
        #* Describes the unlocking
        self.item.set_property("is_locked", False)
        description = "{name} unlocks the {item}.".format(
            name=self.character.name.capitalize(), item=self.item.name
        )
        self.parser.ok(description)
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

    actions = gpt_response.split("\n")
    append_code_to_file('', 'from text_adventure_games import games, things, actions, blocks\n', 'actions')
    c=0
    for action in actions:
        if c>=3:
            break
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
        try:
            append_code_to_file('', gpt_response_code + '\n', 'actions')
        except ValueError as e:
            print(e)
        c+=1

def main():
    action_list = read_from_file("data/actions.txt")
    generate_action_class(action_list)

if __name__ == "__main__":
    main()

# action_list = read_from_file("data/actions.txt")
# generate_action_class(action_list)

# find magic feather
# unlock cottage door
# exit cottage 
# find path to forest
# enter the dark forest
# gather glowing mushrooms
# find the ancient well
# drop feather into well
# get enchanted wing armor
# wear wing armor
# fly upwards towards the moon
# locate ghostly cloud
# use glowing mushrooms to repel ghosts
# find Moon Dancer
# rescue Moon Dancer from ghosts
# fly back down to Earth
# return to cottage
# celebrate victory with Moon Dancer



