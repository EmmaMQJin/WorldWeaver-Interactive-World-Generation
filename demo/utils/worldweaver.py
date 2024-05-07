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

class WorldWeaver(games.Game):
    def __init__(
        self,
        start_at: things.Location,
        player: things.Character,
        characters=None,
        custom_actions=[Enter, Dodge, Find, Avoid, Grab],
        custom_blocks=[CostcoEntranceEastBlock, ProduceAisleOutBlock, SecurityGuardStationEastBlock, BakeryAisleWestBlock, CheckoutLaneEastBlock, CostcoExitSouthBlock]
    ):
        super().__init__(start_at, player, characters, custom_actions, custom_blocks)

    def is_won(character) -> bool:
        """
        Checks whether the game has been won. The game is won
        once Pippin the Pigeon has stolen the Costco burger.
        """
        if "Costco Burger" in character["inventory"]:
            return True
        else:
            return False
