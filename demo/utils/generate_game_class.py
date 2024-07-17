import ast
import json
import os
import ast
from openai import OpenAI
from json_utils import read_json_examples
from generate_actions_utils import read_from_file
from constants import Constants

def write_code_to_file(folder, code, filename):
    """
    Appends code to a Python file
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
    Given the winning state of the game and a description of the main character, generate a python function called is_won(self).
    Task: Develop a Python function called is_won(self) for Checking if main character has reached game winning state.
    Make the end state check on a given property of the main character.
    DO NOT create functions/methods of your own. Only create is_won(self) method.
    Notice that the function should itself be indented by one block, and should only contain self as a parameter, as it is a method within a bigger class."""
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
        self.parser.ok(description)    return True
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
    system_prompt = """Write code for the class WorldWeaver(games.Game) that takes the parameters
     self, start_at: things.Location, player: things.Character, characters=None,
    custom_actions=[all the class names extracted from actions code given by the user],
    custom_blocks=[all the classe names extracted from blocks code given by the user]"""
    
    user_prompt = """
from text_adventure_games import games, things, actions, blocks

class Dodge(actions.Action):
    ...
        
class Avoid(actions.Action):
    ...

class CostcoEntranceEastBlock(blocks.Block):
    ...

class ProduceAisleOutBlock(blocks.Block):
    ...

class SecurityGuardStationEastBlock(blocks.Block):
    ...

class BakeryAisleWestBlock(blocks.Block):
    ...

class CheckoutLaneEastBlock(blocks.Block):
    ...

class CostcoExitSouthBlock(blocks.Block):
    ...
"""
    assistant_prompt = """
class WorldWeaver(games.Game):
    custom_actions = [Dodge, Avoid]
    custom_blocks = [CostcoEntranceEastBlock, ProduceAisleOutBlock, SecurityGuardStationEastBlock, BakeryAisleWestBlock, CheckoutLaneEastBlock, CostcoExitSouthBlock]
    def __init__(
        self,
        start_at: things.Location,
        player: things.Character,
        characters=None,
        custom_actions=custom_actions,
        custom_blocks=custom_blocks
    ):
        super().__init__(start_at, player, characters, custom_actions)
"""
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content':user_prompt},
        {'role': 'assistant', 'content': assistant_prompt},
        {'role': 'user', 'content': actions + '\n' + blocks}
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

def main():
    winning_state = "pigeon succcessfully steals breakfast from Target"
    characters = read_json_examples("data/test_generations/all_the_characters.json")
    generate_game_class(winning_state, characters[0])

if __name__ == "__main__":
    main()


# winning_state = "pigeon succcessfully steals breakfast from Target"
# characters = read_json_examples("data/test_generations/all_the_characters.json")
# generate_game_class(winning_state, characters[0])


