from text_adventure_games import games, things, actions, blocks

class Climb(actions.Action):
    ACTION_NAME = "climb"
    ACTION_DESCRIPTION = "Climb something"
    ACTION_ALIASES = ["jump"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.item = self.parser.match_item(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        # Preconditions:
        # * There must be a matched item
        # * The item must be climbable
        
        if not self.was_matched(self.item):
            return False
        if not self.item.get_property("is_climbable"):
            description = "That's not something you can climb."
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        # Effects:
        # * Describes the climbing
        description = "{name} climbs the {item}.".format(
            name=self.character.name.capitalize(), item=self.item.name
        )
        self.parser.ok(description)
from text_adventure_games import games, things, actions, blocks
class Spot(actions.Action):
    ACTION_NAME = "spot"
    ACTION_DESCRIPTION = "Spot something or someone"

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
        #* Describes the target
        description = "{name} spots the {target}.".format(
            name=self.character.name.capitalize(), target=self.target.name
        )
        self.parser.ok(description)
from text_adventure_games import games, things, actions, blocks
class Decode(actions.Action):
    ACTION_NAME = "decode"
    ACTION_DESCRIPTION = "Decode a message or a code"
    ACTION_ALIASES = ["understand"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.item = self.parser.match_item(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched item
        #* The item must be decodable
        #* The character must have the item in their inventory
        
        if not self.was_matched(self.item):
            return False
        if not self.item.get_property("is_decodable"):
            description = "That's not something you can decode."
            self.parser.fail(description)
            return False
        if not self.character.is_in_inventory(self.item):
            description = "You don't have it."
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Decodes the item
        #* Describes the decoding
        self.item.set_property("is_decoded", True)
        description = "{name} decodes the {item}.".format(
            name=self.character.name.capitalize(), item=self.item.name
        )
        self.parser.ok(description)
