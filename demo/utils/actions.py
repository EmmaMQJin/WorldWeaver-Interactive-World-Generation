from utils.text_adventure_games import games, things, actions, blocks
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
