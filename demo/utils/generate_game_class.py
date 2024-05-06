import ast
import json
import os
import ast
from openai import OpenAI
from utils.json_utils import read_json_examples
from utils.generate_actions_utils import read_from_file, write_code_to_file
from data.static.constants import Constants
def extract_class_names(file_path):
    with open(file_path, 'r') as file:
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

def generate_game_class(winning_state, main_character):
    worldweaver_init = Constants.worldweaver_init
    iswon = generate_is_won(winning_state, main_character)
    actions = read_from_file("actions.py")
    blocks = read_from_file("extracted_block_classes.py")
    code = worldweaver_init + "\n" + iswon + "\n" + actions + "\n" + blocks
    write_code_to_file("",code, "worldweaver")
    
    
winning_state = "pigeon steal costco burger"
characters = read_json_examples("/Users/manvikaul/Documents/Classwork/CIS-7000/project/WorldWeaver-Interactive-World-Generation/demo/data/test_generations/all_the_characters.json")
generate_game_class(winning_state, characters[0])