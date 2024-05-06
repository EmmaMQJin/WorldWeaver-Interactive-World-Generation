class Enter(actions.Action):
    ACTION_NAME = "enter"
    ACTION_DESCRIPTION = "Enter a location"
    ACTION_ALIASES = ["spot"]

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
        self.attack = self.parser.match_item(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched attack
        #* The character must not already be dead or unconscious
        
        if not self.was_matched(self.attack):
            description = "There's nothing to dodge."
            self.parser.fail(description)
            return False
        if self.character.get_property("is_unconscious"):
            description = "{name} is unconscious and can't dodge.".format(name=self.character.name)
            self.parser.fail(description)
            return False
        if self.character.get_property("is_dead"):
            description = "{name} is dead and can't dodge.".format(name=self.character.name)
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Describes the successful dodge
        
        description = "{name} dodges the {attack}.".format(
            name=self.character.name.capitalize(), attack=self.attack.name
        )
        self.parser.ok(description)
class Enter(actions.Action):
    ACTION_NAME = "enter"
    ACTION_DESCRIPTION = "Enter a location"
    ACTION_ALIASES = ["spot"]

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
        if self.character.location.is_blocked(self.character.location.get_direction(self.location)):
            description = self.character.location.get_block_description(self.character.location.get_direction(self.location))
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
        self.attack = self.parser.match_item(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched attack
        #* The character must not already be dead or unconscious
        
        if not self.was_matched(self.attack):
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
        
        description = "{name} dodges the {attack}.".format(
            name=self.character.name.capitalize(), attack=self.attack.name
        )
        self.parser.ok(description)
class Find(actions.Action):
    ACTION_NAME = "find"
    ACTION_DESCRIPTION = "Find a location"
    ACTION_ALIASES = ["navigate"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.location = self.parser.match_location(
            command, self.parser.get_locations_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched location
        #* The location must be reachable from the character's current location
        
        if not self.was_matched(self.location):
            return False
        if not self.character.location.get_direction(self.location):
            description = "You can't get there from here."
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Moves the character to the location
        #* Describes the new location
        self.character.location = self.location
        description = "{name} is now at the {location}.".format(
            name=self.character.name.capitalize(), location=self.location.name
        )
        self.parser.ok(description)
class Grab(actions.Action):
    ACTION_NAME = "grab"
    ACTION_DESCRIPTION = "Grab an item"

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.item = self.parser.match_item(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        # Preconditions:
        # * There must be a matched item
        # * The item must be gettable
        # * The item must be in the same location as the character
        
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
        
        # Effects:
        # * The character grabs the item
        # * The item is removed from the location and added to the character's inventory
        # * Describes the grabbing
        
        self.character.add_to_inventory(self.item)
        description = "{name} grabs the {item}.".format(
            name=self.character.name.capitalize(), item=self.item.name
        )
        self.parser.ok(description)
class Enter(actions.Action):
    ACTION_NAME = "enter"
    ACTION_DESCRIPTION = "Enter a location"
    ACTION_ALIASES = ["spot"]

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
        if self.character.location.is_blocked(self.character.location.get_direction(self.location)):
            description = self.character.location.get_block_description(self.character.location.get_direction(self.location))
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
        self.attack = self.parser.match_item(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched attack
        #* The character must not already be dead or unconscious
        
        if not self.was_matched(self.attack):
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
        #* Describes the dodge
        description = "{name} dodges the {attack}.".format(
            name=self.character.name.capitalize(), attack=self.attack.name
        )
        self.parser.ok(description)
class Find(actions.Action):
    ACTION_NAME = "find"
    ACTION_DESCRIPTION = "Find a location or an item"
    ACTION_ALIASES = ["navigate"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.item = self.parser.match_item(
            command, self.parser.get_items_in_scope(self.character)
        )
        self.location = self.parser.match_location(
            command, self.parser.get_locations_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched item or location
        #* If it's an item, it must be in the same location as the character
        #* If it's a location, it must be connected to the character's current location
        
        if not self.was_matched(self.item) and not self.was_matched(self.location):
            description = "There's nothing to find."
            self.parser.fail(description)
            return False
        if self.was_matched(self.item) and not self.character.location.here(self.item):
            description = "The item is not here."
            self.parser.fail(description)
            return False
        if self.was_matched(self.location) and not self.character.location.get_connection(self.location.name):
            description = "The location is not connected to your current location."
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Describes the item or location
        if self.was_matched(self.item):
            description = "{name} found the {item}.".format(
                name=self.character.name.capitalize(), item=self.item.name
            )
        else:
            description = "{name} found the {location}.".format(
                name=self.character.name.capitalize(), location=self.location.name
            )
        self.parser.ok(description)
class Grab(actions.Action):
    ACTION_NAME = "grab"
    ACTION_DESCRIPTION = "Grab an item"

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
        #* The character grabs the item
        #* The item is removed from the location and added to the character's inventory
        #* Describes the grabbing
        self.character.add_to_inventory(self.item)
        description = "{name} grabs the {item}.".format(
            name=self.character.name.capitalize(), item=self.item.name
        )
        self.parser.ok(description)
class Enter(actions.Action):
    ACTION_NAME = "enter"
    ACTION_DESCRIPTION = "Enter a location"
    ACTION_ALIASES = ["spot"]

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
        if self.character.location.is_blocked(self.character.location.get_direction(self.location)):
            description = self.character.location.get_block_description(self.character.location.get_direction(self.location))
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
        self.attack = self.parser.match_item(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched attack
        #* The character must not already be dead or unconscious
        
        if not self.was_matched(self.attack):
            description = "No attack to dodge."
            self.parser.fail(description)
            return False
        if self.character.get_property("is_unconscious"):
            description = "{name} is unconscious and can't dodge.".format(name=self.character.name)
            self.parser.fail(description)
            return False
        if self.character.get_property("is_dead"):
            description = "{name} is dead and can't dodge.".format(name=self.character.name)
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Describes the dodging
        description = "{name} dodges the attack.".format(
            name=self.character.name.capitalize()
        )
        self.parser.ok(description)
class Find(actions.Action):
    ACTION_NAME = "find"
    ACTION_DESCRIPTION = "Find a location or an item"
    ACTION_ALIASES = ["navigate"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.target = self.parser.match_item_or_location(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched target (item or location)
        
        if not self.was_matched(self.target):
            description = "The target couldn't be found."
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Describes the location of the target (if it's an item, describes its location; if it's a location, describes its connections)
        if isinstance(self.target, locations.Location):
            description = "{name} is at {location}. It's connected to: {connections}".format(
                name=self.character.name.capitalize(),
                location=self.target.name,
                connections=", ".join(self.target.connections.keys()),
            )
        else:
            description = "{item} is at {location}.".format(
                item=self.target.name, location=self.target.location.name
            )
        self.parser.ok(description)
class Grab(actions.Action):
    ACTION_NAME = "grab"
    ACTION_DESCRIPTION = "Grab an item"

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.item = self.parser.match_item(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        # Preconditions:
        # * There must be a matched item
        # * The item must be gettable
        # * The item must be in the same location as the character
        
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
        
        # Effects:
        # * The character grabs the item
        # * The item is removed from the location and added to the character's inventory
        # * Describes the grabbing
        
        self.character.add_to_inventory(self.item)
        description = "{name} grabs the {item}.".format(
            name=self.character.name.capitalize(), item=self.item.name
        )
        self.parser.ok(description)
class Enter(actions.Action):
    ACTION_NAME = "enter"
    ACTION_DESCRIPTION = "Enter a location"
    ACTION_ALIASES = ["spot"]

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
        self.character.location = self.location
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
        self.attack = self.parser.match_item(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched attack
        #* The character must not be unconscious or dead
        
        if not self.was_matched(self.attack):
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
        #* Describes the dodge
        description = "{name} dodges the {attack}.".format(
            name=self.character.name.capitalize(), attack=self.attack.name
        )
        self.parser.ok(description)
class Find(actions.Action):
    ACTION_NAME = "find"
    ACTION_DESCRIPTION = "Find a location or item"
    ACTION_ALIASES = ["navigate"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.target = self.parser.match_item_or_location(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched target (item or location)
        
        if not self.was_matched(self.target):
            description = "The target couldn't be found."
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Describes the location of the target
        if isinstance(self.target, locations.Location):
            description = "{name} is at {location}.".format(
                name=self.target.name, location=self.target.description
            )
        else:
            description = "{name} is at {location}.".format(
                name=self.target.name, location=self.target.location.description
            )
        self.parser.ok(description)
class Grab(actions.Action):
    ACTION_NAME = "grab"
    ACTION_DESCRIPTION = "Grab an item"
    ACTION_ALIASES = ["procure", "retrieve"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.item = self.parser.match_item(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        # Preconditions:
        # * There must be a matched item
        # * The item must be gettable
        # * The item must be in the same location as the character
        
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
        
        # Effects:
        # * The character grabs the item
        # * The item is removed from the location and added to the character's inventory
        # * Describes the grabbing
        
        self.character.add_to_inventory(self.item)
        description = "{name} grabs the {item}.".format(
            name=self.character.name.capitalize(), item=self.item.name
        )
        self.parser.ok(description)
class Enter(actions.Action):
    ACTION_NAME = "enter"
    ACTION_DESCRIPTION = "Enter a location"
    ACTION_ALIASES = ["spot"]

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
        description = "{name} enters the {location}.".format(
            name=self.character.name.capitalize(), location=self.location.name
        )
        self.parser.ok(description)
        self.game.describe_location(self.character.location)
class Enter(actions.Action):
    ACTION_NAME = "enter"
    ACTION_DESCRIPTION = "Enter a location"
    ACTION_ALIASES = ["spot"]

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
        if self.character.location.is_blocked(self.character.location.get_direction(self.location)):
            description = self.character.location.get_block_description(self.character.location.get_direction(self.location))
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
        self.attack = self.parser.match_item(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched attack
        #* The character must not already be dead or unconscious
        
        if not self.was_matched(self.attack):
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
        #* Describes the dodge
        description = "{name} dodges the {attack}.".format(
            name=self.character.name.capitalize(), attack=self.attack.name
        )
        self.parser.ok(description)
class Enter(actions.Action):
    ACTION_NAME = "enter"
    ACTION_DESCRIPTION = "Enter a location"
    ACTION_ALIASES = ["spot"]

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
        self.character.location = self.location
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
        self.attack = self.parser.match_item(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched attack
        #* The character must not already be dead or unconscious
        
        if not self.was_matched(self.attack):
            description = "There's nothing to dodge."
            self.parser.fail(description)
            return False
        if self.character.get_property("is_unconscious"):
            description = "{name} is unconscious and can't dodge.".format(name=self.character.name)
            self.parser.fail(description)
            return False
        if self.character.get_property("is_dead"):
            description = "{name} is dead and can't dodge.".format(name=self.character.name)
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Describes the dodging
        description = "{name} dodges the {attack}.".format(
            name=self.character.name.capitalize(), attack=self.attack.name
        )
        self.parser.ok(description)
class Find(actions.Action):
    ACTION_NAME = "find"
    ACTION_DESCRIPTION = "Find a location or an item"
    ACTION_ALIASES = ["navigate"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.item_or_location = self.parser.match_item_or_location(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched item or location
        #* The item or location must be reachable from the character's current location
        
        if not self.was_matched(self.item_or_location):
            return False
        if not self.character.location.is_reachable(self.item_or_location):
            description = "You can't reach that from here."
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Moves the character to the location
        #* Describes the new location
        #* If the item or location is an item, describes the item
        self.character.location = self.item_or_location
        description = "{name} finds the {item_or_location}.".format(
            name=self.character.name.capitalize(), item_or_location=self.item_or_location.name
        )
        self.parser.ok(description)
        if isinstance(self.item_or_location, Item):
            description = self.item_or_location.description
            self.parser.ok(description)
class Enter(actions.Action):
    ACTION_NAME = "enter"
    ACTION_DESCRIPTION = "Enter a location"
    ACTION_ALIASES = ["spot"]

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
        self.attack = self.parser.match_item(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be an attack to dodge
        #* The character must not be unconscious or dead
        
        if not self.was_matched(self.attack):
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
        #* Describes the dodge
        description = "{name} dodges the {attack}.".format(
            name=self.character.name.capitalize(), attack=self.attack.name
        )
        self.parser.ok(description)
class Find(actions.Action):
    ACTION_NAME = "find"
    ACTION_DESCRIPTION = "Find a location"
    ACTION_ALIASES = ["navigate"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.location = self.parser.match_location(
            command, self.parser.get_locations_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched location
        #* The location must be connected to the character's current location
        
        if not self.was_matched(self.location):
            return False
        if not self.character.location.get_connection(self.location.name):
            description = "You can't get there from here."
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Moves the character to the new location
        #* Describes the new location
        self.character.location = self.location
        description = "{name} moves to the {location}.".format(
            name=self.character.name.capitalize(), location=self.location.name
        )
        self.parser.ok(description)
class Grab(actions.Action):
    ACTION_NAME = "grab"
    ACTION_DESCRIPTION = "Grab an item"

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.item = self.parser.match_item(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        # Preconditions:
        # * There must be a matched item
        # * The item must be gettable
        # * The item must be in the same location as the character
        
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
        
        # Effects:
        # * The character grabs the item
        # * The item is removed from the location and added to the character's inventory
        # * Describes the grabbing
        self.character.add_to_inventory(self.item)
        description = "{name} grabs the {item}.".format(
            name=self.character.name.capitalize(), item=self.item.name
        )
        self.parser.ok(description)
class Enter(actions.Action):
    ACTION_NAME = "enter"
    ACTION_DESCRIPTION = "Enter a location"
    ACTION_ALIASES = ["spot"]

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
        self.attack = self.parser.match_item(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched attack
        #* The character must not already be dead or unconscious
        
        if not self.was_matched(self.attack):
            description = "No attack to dodge."
            self.parser.fail(description)
            return False
        if self.character.get_property("is_unconscious"):
            description = "{name} is unconscious and can't dodge.".format(name=self.character.name)
            self.parser.fail(description)
            return False
        if self.character.get_property("is_dead"):
            description = "{name} is dead and can't dodge.".format(name=self.character.name)
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Describes the dodging
        
        description = "{name} dodges the attack.".format(
            name=self.character.name.capitalize()
        )
        self.parser.ok(description)
class Find(actions.Action):
    ACTION_NAME = "find"
    ACTION_DESCRIPTION = "Find a location or an item"
    ACTION_ALIASES = ["navigate"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.target = self.parser.match_item_or_location(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched target
        #* The target must be reachable from the character's current location
        
        if not self.was_matched(self.target):
            return False
        if not self.character.location.get_direction(self.target):
            description = "You can't find a way to get there."
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Moves the character to the target location
        #* Describes the new location
        self.character.location = self.target
        description = "{name} finds the {target}.".format(
            name=self.character.name.capitalize(), target=self.target.name
        )
        self.parser.ok(description)
        self.character.location.describe()
class Grab(actions.Action):
    ACTION_NAME = "grab"
    ACTION_DESCRIPTION = "Grab an item"

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
        description = "{name} grabs the {item}.".format(
            name=self.character.name.capitalize(), item=self.item.name
        )
        self.parser.ok(description)
class Enter(actions.Action):
    ACTION_NAME = "enter"
    ACTION_DESCRIPTION = "Enter a location"
    ACTION_ALIASES = ["spot"]

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
        if self.character.location.is_blocked(self.character.location.get_direction(self.location)):
            description = self.character.location.get_block_description(self.character.location.get_direction(self.location))
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
        self.attack = self.parser.match_item(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched attack
        #* The character must not be unconscious or dead
        
        if not self.was_matched(self.attack):
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
        #* Describes the dodge
        description = "{name} dodges the {attack}.".format(
            name=self.character.name.capitalize(), attack=self.attack.name
        )
        self.parser.ok(description)
class Find(actions.Action):
    ACTION_NAME = "find"
    ACTION_DESCRIPTION = "Find a location or an item"
    ACTION_ALIASES = ["navigate"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.item_or_location = self.parser.match_item_or_location(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched item or location
        #* The item or location must be reachable from the character's current location
        
        if not self.was_matched(self.item_or_location):
            return False
        if not self.character.location.is_reachable(self.item_or_location):
            description = "You can't reach that from here."
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Moves the character to the location
        #* Describes the new location
        #* If the item or location is an item, describes the item
        self.character.location = self.item_or_location
        description = "{name} finds the {item_or_location}.".format(
            name=self.character.name.capitalize(), item_or_location=self.item_or_location.name
        )
        self.parser.ok(description)
        if isinstance(self.item_or_location, Item):
            description = self.item_or_location.description
            self.parser.ok(description)
class Grab(actions.Action):
    ACTION_NAME = "grab"
    ACTION_DESCRIPTION = "Grab an item"

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
        #* Moves the item to the character's inventory
        #* Describes the grabbing
        self.character.add_to_inventory(self.item)
        description = "{name} grabs the {item}.".format(
            name=self.character.name.capitalize(), item=self.item.name
        )
        self.parser.ok(description)
class Enter(actions.Action):
    ACTION_NAME = "enter"
    ACTION_DESCRIPTION = "Enter a location"
    ACTION_ALIASES = ["spot"]

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
        description = "{name} enters the {location}.".format(
            name=self.character.name.capitalize(), location=self.location.name
        )
        self.parser.ok(description)
        self.game.describe_location(self.character.location)
