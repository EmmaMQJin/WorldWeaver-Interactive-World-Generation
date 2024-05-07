import ast
import json
import os
import ast
from openai import OpenAI
from utils.json_utils import read_json_examples
from utils.generate_actions_utils import read_from_file
from utils.constants import Constants

def write_code_to_file(folder, code, filename):
    """
    Appends code to a Python file named 'actions.py' in the specified folder, or creates it if it doesn't exist.
    """
    base_path = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script
    full_path = os.path.join(base_path, folder)
    os.makedirs(full_path, exist_ok=True)  # Create the folder if it doesn't exist
    file_path = os.path.join(full_path, filename+".py")
    with open(file_path, 'w') as file:  # Open the file in append mode
        file.write(code.strip() + '\n')  # Append the code to the file
    print(f"Code appended to: {file_path}")

def extract_class_names(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Parse the content to an AST
    tree = ast.parse(content)

    # This class will visit each ClassDef and store the names
    class ClassVisitor(ast.NodeVisitor):
        def __init__(self):
            self.class_names = []

        def visit_ClassDef(self, node):
            self.class_names.append(node.name)
            self.generic_visit(node)  # Continue traversing

    visitor = ClassVisitor()
    visitor.visit(tree)
    return visitor.class_names


def generate_is_won(winning_state, main_character):
    #end state, main character
    client = OpenAI(base_url="https://oai.hconeai.com/v1", api_key=os.environ['HELICONE_API_KEY'])
    system_prompt_is_won = """
    Given the winning state of the game and a description of the main character, generate is_won python function.
    Task: Develop a Python function called is_won for Checking if main character has reached game winning state.
    Make the end state check on a given property of the main character.
    DO NOT create functions/methods of your own. Only create is_won() method."""
    user_prompt_example = """

    Main Character:
        {
            "name": "The player",
            "description":"You are a simple peasant destined for greatness.",
            "persona":"I am on an adventure.",
            "properties": {
                "character_type": "human",
                "is_dead": false,
                "is_reigning": false
            }
        }

    Winning state: The game is won once any character is sitting on the throne.
"""
    assistant_prompt_example = """
    
    def is_won(self) -> bool:
    \"""
    Checks whether the game has been won. For Action Castle, the game is won
    once any character is sitting on the throne (has the property is_reigning).
    \"""
    for name, character in self.characters.items():
        if character.get_property("is_reigning"):
            self.parser.ok(
                "{name} is now reigns in ACTION CASTLE! {name} has won the game!".format(
                    name=character.name.title()
                )
            )
            return True
    return False
    """

    user_prompt = f"""

    Main Character:
    {json.dumps(main_character)}

    Winning State: {winning_state}
"""

    messages = [
        {'role': 'system', 'content': system_prompt_is_won},
        {'role': 'user', 'content': user_prompt_example},
        {'role': 'assistant', 'content': assistant_prompt_example},
        {'role': 'user', 'content': user_prompt}
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
    iswon = response.choices[0].message.content
    return iswon

def populate_custom_actions(actions, blocks, weaver):
    client = OpenAI(base_url="https://oai.hconeai.com/v1", api_key=os.environ['HELICONE_API_KEY'])
    system_prompt = f"Write {weaver} word for word with the only difference that custom_actions=None is replaced by custom_actions=[all the class names from {actions}] and custom_blocks=None is replaced by custom_blocks=[all the classes from the {blocks}]"
    user_prompt = """
from text_adventure_games import games, things, actions, blocks
class Enter(actions.Action):
    ACTION_NAME = "enter"
    ACTION_DESCRIPTION = "Enter a location"
    ACTION_ALIASES = ["exit"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.location = self.parser.match_location(
            command, self.character.location.connections
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched location
        #* The location must be connected to the character's current location
        #* The path to the location must not be blocked
        
        if not self.was_matched(self.location):
            return False
        if not self.character.location.get_connection(self.location.name):
            description = "You can't get there from here."
            self.parser.fail(description)
            return False
        if self.character.location.is_blocked(self.location.name):
            description = self.character.location.get_block_description(
                self.location.name
            )
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Moves the character to the new location
        #* Describes the new location
        self.character.location.remove_character(self.character)
        self.location.add_character(self.character)
        description = "{name} enters {location}.".format(
            name=self.character.name.capitalize(), location=self.location.name
        )
        self.parser.ok(description)
        self.game.describe_location(self.character.location)
class Dodge(actions.Action):
    ACTION_NAME = "dodge"
    ACTION_DESCRIPTION = "Dodge an attack"
    ACTION_ALIASES = ["evade"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* The character must be in a combat situation
        #* The character must not be unconscious or dead
        
        if not self.character.get_property("in_combat"):
            description = "There's nothing to dodge."
            self.parser.fail(description)
            return False
        if self.character.get_property("is_unconscious"):
            description = "{name} is unconscious and can't dodge.".format(
                name=self.character.name.capitalize()
            )
            self.parser.fail(description)
            return False
        if self.character.get_property("is_dead"):
            description = "{name} is dead and can't dodge.".format(
                name=self.character.name.capitalize()
            )
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* The character dodges the next attack
        #* Describes the dodge
        self.character.set_property("dodging", True)
        description = "{name} prepares to dodge the next attack.".format(
            name=self.character.name.capitalize()
        )
        self.parser.ok(description)
class Find(actions.Action):
    ACTION_NAME = "find"
    ACTION_DESCRIPTION = "Find something"
    ACTION_ALIASES = ["spot"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.item = self.parser.match_item(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched item
        #* The item must be in the same location as the character
        
        if not self.was_matched(self.item):
            return False
        if not self.character.location.here(self.item):
            description = "The item is not here."
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Describes the item
        description = "{name} found the {item}.".format(
            name=self.character.name.capitalize(), item=self.item.name
        )
        self.parser.ok(description)
class Avoid(actions.Action):
    ACTION_NAME = "avoid"
    ACTION_DESCRIPTION = "Avoid a character or an item"

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.target = self.parser.match_item_or_character(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched target
        #* The target must be in the same location as the character
        
        if not self.was_matched(self.target):
            return False
        if not self.character.location.here(self.target):
            description = "The target is not here."
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* The character avoids the target
        #* Describes the avoidance
        description = "{name} avoids the {target}.".format(
            name=self.character.name.capitalize(), target=self.target.name
        )
        self.parser.ok(description)
class Grab(actions.Action):
    ACTION_NAME = "grab"
    ACTION_DESCRIPTION = "Grab an item"
    ACTION_ALIASES = ["navigate"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.item = self.parser.match_item(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched item
        #* The item must be gettable
        #* The item must be in the same location as the character
        
        if not self.was_matched(self.item):
            return False
        if not self.item.get_property("is_gettable"):
            description = "That's not something you can grab."
            self.parser.fail(description)
            return False
        if not self.character.location.here(self.item):
            description = "It's not here."
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Adds the item to the character's inventory
        #* Removes the item from the location
        #* Describes the grabbing
        self.character.add_to_inventory(self.item)
        self.character.location.remove_item(self.item)
        description = "{name} grabs the {item}.".format(
            name=self.character.name.capitalize(), item=self.item.name
        )
        self.parser.ok(description)

class CostcoEntranceEastBlock(blocks.Block):
        def __init__(self, location: things.Location, chester_the_sample_giver: things.Character, connection: str):
            super().__init__('Chester the Sample Giver is blocking the way', 'You need to distract Chester the Sample Giver to proceed to the Bakery Aisle.')
            self.chester_the_sample_giver = chester_the_sample_giver
            self.location = location
            self.connection = connection  # This parameter reflects the destination name

        def is_blocked(self) -> bool:
            return self.location.here(self.chester_the_sample_giver)

class ProduceAisleOutBlock(blocks.Block):
        def __init__(self, location: things.Location, bobby_the_shopper: things.Character, connection: str):
            super().__init__('Bobby the Shopper is blocking the way', 'You need to distract Bobby the Shopper to proceed to the Costco Parking Lot.')
            self.bobby_the_shopper = bobby_the_shopper
            self.location = location
            self.connection = connection  # This parameter reflects the destination name

        def is_blocked(self) -> bool:
            return self.location.here(self.bobby_the_shopper)

class SecurityGuardStationEastBlock(blocks.Block):
        def __init__(self, location: things.Location, ranger_feline: things.Character, connection: str):
            super().__init__('Ranger Feline is blocking the way', 'You need to distract Ranger Feline to proceed to the Costco Parking Lot.')
            self.ranger_feline = ranger_feline
            self.location = location
            self.connection = connection  # This parameter reflects the destination name

        def is_blocked(self) -> bool:
            return self.location.here(self.ranger_feline)

class BakeryAisleWestBlock(blocks.Block):
        def __init__(self, location: things.Location, mrs_crumble: things.Character, connection: str):
            super().__init__('Mrs. Crumble is blocking the way', 'You need to distract Mrs. Crumble to proceed to the Costco Entrance.')
            self.mrs_crumble = mrs_crumble
            self.location = location
            self.connection = connection  # This parameter reflects the destination name

        def is_blocked(self) -> bool:
            return self.location.here(self.mrs_crumble)

class CheckoutLaneEastBlock(blocks.Block):
        def __init__(self, location: things.Location, rusty_the_security_guard: things.Character, connection: str):
            super().__init__('Rusty the Security Guard is blocking the way', 'You need to distract Rusty the Security Guard to proceed to the Costco Entrance.')
            self.rusty_the_security_guard = rusty_the_security_guard
            self.location = location
            self.connection = connection  # This parameter reflects the destination name

        def is_blocked(self) -> bool:
            return self.location.here(self.rusty_the_security_guard)

class CostcoExitSouthBlock(blocks.Block):
        def __init__(self, location: things.Location, shelly_the_shopper: things.Character, connection: str):
            super().__init__('Shelly the Shopper is blocking the way', 'You need to distract Shelly the Shopper to proceed to the Costco Entrance.')
            self.shelly_the_shopper = shelly_the_shopper
            self.location = location
            self.connection = connection  # This parameter reflects the destination name

        def is_blocked(self) -> bool:
            return self.location.here(self.shelly_the_shopper)


"""
    assistant_prompt = """
class WorldWeaver(games.Game):
    def __init__(
        self,
        start_at: things.Location,
        player: things.Character,
        characters=None,
        custom_actions=[Dodge,Find,Avoid,Add],
        custom_blocks=[CostcoEntranceEastBlock, ProduceAisleOutBlock, SecurityGuardStationEastBlock, BakeryAisleWestBlock, CheckoutLaneEastBlock, CostcoExitSouthBlock]
    ):
        super().__init__(start_at, player, characters, custom_actions)
"""
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content':user_prompt},
        {'role': 'assistant', 'content': assistant_prompt},
        {'role': 'user', 'content': actions}
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
    replaced = response.choices[0].message.content
    print(replaced)
    return replaced

def generate_game_class(winning_state, main_character):
    worldweaver_init = Constants.worldweaver_init
    iswon = generate_is_won(winning_state, main_character)
    acts = read_from_file("utils/actions.py")
    blocks = read_from_file("data/extracted_block_classes.py")
    write_code_to_file("",acts+ "\n"+ blocks +"\n"+ populate_custom_actions(acts, blocks, worldweaver_init) + "\n"+iswon, "worldweaver")

# winning_state = "pigeon steal costco burger"
# characters = read_json_examples("data/test_generations/all_the_characters.json")
# generate_game_class(winning_state, characters[0])


