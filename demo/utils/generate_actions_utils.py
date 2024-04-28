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
        print(f"Data successfully written to {filename}")
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

def write_code_to_file(folder, class_name, code):
    """
    Writes code to a Python file in the specified folder, named after the class.
    """
    base_path = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script
    full_path = os.path.join(base_path, folder)
    os.makedirs(full_path, exist_ok=True)  # Create the folder if it doesn't exist
    file_path = os.path.join(full_path, f"{class_name}.py")
    with open(file_path, 'w') as file:
        file.write(code.strip())
    print(f"File written: {file_path}")

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
    system_prompt_unique_actions = """
    Given a list of action words, analyze each word to determine its uniqueness. For actions that have synonyms, consult the Oxford Dictionary to verify if they are indeed synonymous. 
    For each unique action, compile a list where synonymous actions are grouped together. 
    Use the format "get [alias: procure, retrieve]" to display the primary action followed by its synonyms in brackets, prefixed by "alias:".
    Ensure to include only one primary action for each group of synonyms, with all other synonymous actions listed as aliases.
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
    get [alias: procure, retrieve]
    plant
    """
    user_prompt_two = f"{action_list}"
   
    system_prompt = """
    Task: Develop a Python Class for Game Actions

    You are tasked with creating a Python class to represent a specific action within a game. The class should inherit from a base class and include the following methods:

    1. Constructor (__init__): Initialize with parameters self, game, command: str.
    2. Check Preconditions (check_preconditions): This method should return a boolean value. Return False if any preconditions are not met, otherwise return True if all conditions are met. The method signature should be def check_preconditions(self) -> bool:.
    3. Apply Effects (apply_effects): Implement this method to apply the effects of the action. It should not return any value. The method signature should be def apply_effects(self):.

    The class should also include a class member for aliases of the action word, using the format:
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
    """
    user_example_prompt_one = "get [alias: procure, retrieve]"   
    user_example_prompt_two = "eat [alias: consume, ingest]"
    user_example_prompt_three = "cook"
    user_example_prompt_four = "unlock door"
    user_example_prompt_five = "Unlock"

    assistant_example_prompt_one = """
import base
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
import base
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
import base
class Cook(base.Action):
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
import base 
class Unlock_Door(base.Action):
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
    assistant_example_prompt_five = """
import base
class Unlock(base.Action):
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
        {'role': 'user', 'content': user_example_prompt_five},
        {'role': 'assistant', 'content': assistant_example_prompt_five},
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
            class_name = find_class_name(gpt_response_code)
            write_code_to_file('actions', class_name, gpt_response_code)
        except ValueError as e:
            print(e)

action_list = read_from_file("data/actions.txt")
print(action_list)
generate_action_class(action_list)

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




