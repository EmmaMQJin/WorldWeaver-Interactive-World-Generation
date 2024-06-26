from text_adventure_games import games, things, actions, blocks
class Enter(actions.Action):
    ACTION_NAME = "enter"
    ACTION_DESCRIPTION = "Enter a location"
    ACTION_ALIASES = ["access"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.location = self.parser.match_location(
            command, self.character.location.connections
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched location
        #* The location must not be blocked
        
        if not self.was_matched(self.location):
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
        description = "{name} enters the {location}.".format(
            name=self.character.name.capitalize(), location=self.location.name
        )
        self.parser.ok(description)
        self.game.describe_location(self.character.location)
class Dodge(actions.Action):
    ACTION_NAME = "dodge"
    ACTION_DESCRIPTION = "Dodge an attack"
    ACTION_ALIASES = ["avoid", "evade"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* The character must be in a location where an attack is happening
        #* The character must not already be dead or unconscious
        
        if not self.character.location.is_under_attack():
            description = "There's nothing to dodge."
            self.parser.fail(description)
            return False
        if self.character.get_property("is_unconscious"):
            description = "{name} is unconscious and can't dodge.".format(
                name=self.character.name
            )
            self.parser.fail(description)
            return False
        if self.character.get_property("is_dead"):
            description = "{name} is dead and can't dodge.".format(
                name=self.character.name
            )
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* The character dodges the attack
        #* Describes the dodging
        description = "{name} dodges the attack.".format(
            name=self.character.name.capitalize()
        )
        self.parser.ok(description)
class Find(actions.Action):
    ACTION_NAME = "find"
    ACTION_DESCRIPTION = "Find something"
    ACTION_ALIASES = ["spot", "locate"]

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
            description = "There's no such item to find."
            self.parser.fail(description)
            return False
        if not self.character.location.here(self.item):
            description = "The item is not here."
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Describes the item
        description = "{name} found the {item}. {item_desc}".format(
            name=self.character.name.capitalize(),
            item=self.item.name,
            item_desc=self.item.description,
        )
        self.parser.ok(description)
