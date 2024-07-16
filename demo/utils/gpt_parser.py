from openai import OpenAI
import json
import tiktoken
import os
from getpass import getpass
import re
from text_adventure_games import parsing
from text_adventure_games.things.characters import Character
from text_adventure_games.things.items import Item
from text_adventure_games.things.locations import Location


class GptParser(parsing.Parser):
    def __init__(self, game, echo_commands=True, verbose=False, narration_style=None):
        super().__init__(game, echo_commands=echo_commands)
        self.verbose = verbose
        self.narration_style = narration_style
        if "HELICONE_API_KEY" not in os.environ:
            print(
                "You didn't set your Helicone key to the HELICONE_API_KEY env var on the command line.  Please enter it now."
            )
            os.environ["HELICONE_API_KEY"] = getpass(
                "Please enter your Helicone API Key now: "
            )

        self.client = OpenAI(
            base_url="https://oai.hconeai.com/v1",
            api_key=os.environ["HELICONE_API_KEY"],
        )
        self.gpt_model = "gpt-4"
        self.max_output_tokens = 256
        self.max_tokens = 8192 - self.max_output_tokens
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        # Command descriptions
        self.command_descriptions = {}
        for _, action in self.actions.items():
            description = action.ACTION_DESCRIPTION
            if action.ACTION_ALIASES:
                description += " (can also be invoked with '{aliases}')".format(
                    aliases="', '".join(action.ACTION_ALIASES)
                )
            action_name = action.ACTION_NAME
            if action_name:
                self.command_descriptions[description] = action_name

    def gpt_describe(self, system_instructions, command_history, max_turns=10):
        """
        Generate a description with GPT.
        """
        try:
            messages = [{"role": "system", "content": system_instructions}]
            context = self.limit_context_length(command_history, self.max_tokens)
            messages.extend(context)

            for m in messages:
                print(m)
            
            if self.verbose:
                print(json.dumps(messages, indent=2))
            response = self.client.chat.completions.create(
                model=self.gpt_model,
                messages=messages,
                temperature=1,
                max_tokens=self.max_output_tokens,
                top_p=0,
                frequency_penalty=0,
                presence_penalty=0,
            )
            content = response.choices[0].message.content
            
            return content
        except:
            return "Something went wrong with GPT"

    def limit_context_length(self, command_history, max_tokens, max_turns=1000):
        """
        This method limits the length of the command_history
        to be less than the max_tokens. Disregards the least recently used
        messages. Doesn't modify command_history.
        """
        total_tokens = 0
        limited_history = []

        for message in reversed(command_history):
            msg_tokens = len(self.tokenizer.encode(message["content"]))
            if total_tokens + msg_tokens > max_tokens:
                break
            total_tokens += msg_tokens
            limited_history.append(message)
            if len(limited_history) >= max_turns:
                break
        return list(reversed(limited_history))

    def ok(self, description):
        """
        In this homework, we'll replace this with a call to the OpenAI API
        in order to create more evocative descriptions. For this part,
        all you need to do is create your own system instructions.
        """
        system_instructions = "".join(
            [
                "You are the narrator for a text adventure game. You create short, ",
                "evocative descriptions of the game.",
                "After each command from the user, you will see an assistant command."
                "You should ALWAYS base your description solely on the information of that assistant command.",
                "You should refer to the player in ",
                "2nd person, and you should use present tense. ",
                "If a command doesn't work, tell the player why. "
                "If the command is 'look', describe the game location in a few sentences, and then list its connections, characters, and items according to the information provided to you, in the following format:",
                "Description of location (based on what's given to you)\n",
                "Connections:\n",
                "East to A\n",
                "West to B\n",
                "...\n\n",
                "NPCs:\n",
                "...\n\n",
                "Objects:\n",
                "...\n"
            ]
        )
        # if self.narration_style:
        #     system_instructions += f"\n{self.narration_style}."
        self.add_description_to_history(description)
        gpt_description = self.gpt_describe(system_instructions, self.command_history)
        if self.verbose:
            print("GPT Description:")
        print(self.wrap_text(gpt_description) + "\n")
        self.add_description_to_history(gpt_description)

    def fail(self, description):
        """
        In this homework, we'll replace this with a call to the OpenAI API
        in order to create more useful error messages descriptions.
        """
        system_instructions = "".join(
            [
                "You are the narrator for a text adventure game. The player attempted a ",
                "command that failed in the game. Try to help the player understand ",
                "why the command failed.",
            ]
        )

        self.add_description_to_history(description)
        gpt_description = self.gpt_describe(system_instructions, self.command_history)
        if self.verbose:
            print("GPT Description of Failed Command:")
        print(self.wrap_text(gpt_description) + "\n")
        self.add_description_to_history(gpt_description)

    def gpt_pick_an_option(self, instructions, options, input_str):
        """
        This function calls GPT to choose one option from a set of options.
        Its arguments are:
        * instructions - the system instructions
        * options - a dictionary of option_descriptions -> option_names
        * input_str - the user input which we are trying to match to one of the options

        The function generates an enumerated list of option descriptions
        that are shown to GPT. It then returns a number (which I match with a
        regex, in case it generates more text than is necessary), and then
        returns the option name.
        """
        options_list = list(options.keys())
        choices_str = ""
        # Create a numbered list of options
        for i, option in enumerate(options_list):
            choices_str += "{i}. {option}\n".format(i=i, option=option)
        print(choices_str)
        # Call the OpenAI API
        response = self.client.chat.completions.create(
            model=self.gpt_model,
            messages=[
                {
                    "role": "system",
                    "content": "{instructions}\n\n{choices_str}\nReturn just the number.".format(
                        instructions=instructions, choices_str=choices_str
                    ),
                },
                {"role": "user", "content": input_str},
            ],
            temperature=1,
            max_tokens=256,
            top_p=0,
            frequency_penalty=0,
            presence_penalty=0,
        )
        content = response.choices[0].message.content

        if self.verbose:
            v = "{instructions}\n\n{choices_str}\nReturn just the number.\n---\n> {input_str}"
            print(
                v.format(
                    instructions=instructions,
                    choices_str=choices_str,
                    input_str=input_str,
                )
            )
            print("---\nGPT's response was:", content)

        # Use regular expressions to match a number returned by OpenAI and select that option.
        pattern = r"\d+"
        matches = re.findall(pattern, content)
        if matches:
            index = int(matches[0])
            if index >= len(options_list):
                return None
            option = options_list[index]
            return options[option]
        else:
            return None

    def determine_intent(self, command):
        """
        Instead of the keyword based intent determination, we'll use GPT.
        """
        instructions = "".join(
            [
                "You are the command parser for a text adventure game. Given an input from the player, output which ",
                "of the follwing commands it most closely matches:",
            ]
        )

        return self.gpt_pick_an_option(instructions, self.command_descriptions, command)

    def get_character(
        self, command: str, hint: str = None, split_words=None, position=None
    ) -> Character:
        """
        This method tries to match a character's name in the command.
        If no names are matched, it defaults to `game.player`. 
        Args:
            hint: A hint about the role of character we're looking for 
                  (e.g. "giver" or "recipent")
            split_words: not needed for our GptParser
            position: not needed for our GptParser
        """ """
        This method tries to match a character's name in the command.
        If no names are matched, it defaults to the player.
        """
        if self.verbose:
            print("Matching a character with GPT.")
        character_descriptions = {}
        for name, character in self.game.characters.items():
            if character.location:
                d = "{name} - {description} (currently located in {location})"
                description = d.format(
                    name=name,
                    description=character.description,
                    location=character.location.name,
                )
            else:
                description = "{name} - {description}".format(
                    name=name, description=character.description
                )
            if character == self.game.player:
                description = "The player: {description}".format(
                    description=character.description
                )

            character_descriptions[description] = character

        instructions = "".join(
            [
                "You are the command parser for a text adventure game. Given an input command from the player, ",
                "match the character in the command according to the following list (if no character is mentioned in the ",
                "command, then default to '{player}').".format(
                    player=self.game.player.name
                ),
            ]
        )
        if hint:
            instructions += f"\nHint: the character you are looking for is the {hint}. "
        instructions += "\n\nThe possible characters are:"

        return self.gpt_pick_an_option(instructions, character_descriptions, command)

    def match_item(
        self, command: str, item_dict: dict[str, Item], hint: str = None
    ) -> Item:
        """
        Check whether the name any of the items in this dictionary match the
        command. If so, return Item, else return None.

        Args:
            item_dict: A map from item names to Items (could be a player's 
                       inventory or the items at a location)
            hint: what kind of item we're looking for
        """ """
        Check whether the name any of the items in this dictionary match the
        command. If so, return Item, else return None.
        """
        if self.verbose:
            print("Matching an item with GPT.")
        instructions = "You are the command parser for a text adventure game. Given an input command from the player, try to match the item refered to in the command."
        if hint:
            instructions += f"\nHint: {hint}."
        instructions += "\n\nThe possible items are:"

        item_descriptions = {}
        for name, item in item_dict.items():
            if item.location:
                description = (
                    "{name} - {description} (currently located in {location})".format(
                        name=name,
                        description=item.description,
                        location=item.location.name,
                    )
                )
            else:
                description = "{name} - {description}".format(
                    name=name, description=item.description
                )

            item_descriptions[description] = item
        return self.gpt_pick_an_option(instructions, item_descriptions, command)

    def get_direction(self, command: str, location: Location = None) -> str:
        """
        Return the direction from `location.connections` which the player
        wants to travel to.
        """
        if self.verbose:
            print("Matching a direction with GPT.")
        instructions = "".join(
            [
                "You are the command parser for a text adventure game. For an input command try to ",
                "match the direction in the command. Give the cloest matching one, or say ",
                "None if none match. The possible directions are:",
            ]
        )
        directions = {}
        if location:
            for direction, to_loc in location.connections.items():
                loc_description = "{name} - {description}".format(
                    name=to_loc.name, description=to_loc.description
                )
                location_name_direction = "{direction} toward {loc}".format(
                    direction=direction, loc=loc_description
                )
                directions[location_name_direction] = direction
        other_directions = {
            "'n' can mean north": "north",
            "'s' can mean south": "south",
            "'e' can mean east": "east",
            "'w' can mean west": "west",
            "'out' can mean 'go out'": "out",
            "'in' can mean 'go in'": "in",
            "'up' can mean 'go up'": "up",
            "'down' can mean 'go down'": "down",
        }
        directions.update(other_directions)
        return self.gpt_pick_an_option(instructions, directions, command)
