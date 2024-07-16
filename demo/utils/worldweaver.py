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

class CostcoEntranceEastBlock(blocks.Block):
        def __init__(self, location: things.Location, chester_the_sample_giver: things.Character, connection: str):
            super().__init__('Chester the Sample Giver is blocking the way', 'You need to distract Chester the Sample Giver to proceed to the Bakery Aisle.')
            self.chester_the_sample_giver = chester_the_sample_giver
            self.location = location
            self.connection = connection  # This parameter reflects the destination name

        def is_blocked(self) -> bool:
            if self.chester_the_sample_giver:
                if not self.location.here(self.chester_the_sample_giver):
                    return False
                if self.chester_the_sample_giver.get_property("is_dead"):
                    return False
                if self.chester_the_sample_giver.get_property("is_unconscious"):
                    return False
            return False
        
        @classmethod
        def from_primitive(cls, data):
            location = data["location"]
            door = data["chester_the_sample_giver"]
            connection = data["connection"]
            instance = cls(location, door, connection)
            return instance

class ProduceAisleOutBlock(blocks.Block):
        def __init__(self, location: things.Location, bobby_the_shopper: things.Character, connection: str):
            super().__init__('Bobby the Shopper is blocking the way', 'You need to distract Bobby the Shopper to proceed to the Costco Parking Lot.')
            self.bobby_the_shopper = bobby_the_shopper
            self.location = location
            self.connection = connection  # This parameter reflects the destination name

        def is_blocked(self) -> bool:
            return self.location.here(self.bobby_the_shopper)
        
        @classmethod
        def from_primitive(cls, data):
            location = data["location"]
            door = data["bobby_the_shopper"]
            connection = data["connection"]
            instance = cls(location, door, connection)
            return instance


class SecurityGuardStationEastBlock(blocks.Block):
        def __init__(self, location: things.Location, ranger_feline: things.Character, connection: str):
            super().__init__('Ranger Feline is blocking the way', 'You need to distract Ranger Feline to proceed to the Costco Parking Lot.')
            self.ranger_feline = ranger_feline
            self.location = location
            self.connection = connection  # This parameter reflects the destination name

        def is_blocked(self) -> bool:
            return self.location.here(self.ranger_feline)
        
        @classmethod
        def from_primitive(cls, data):
            location = data["location"]
            door = data["ranger_feline"]
            connection = data["connection"]
            instance = cls(location, door, connection)
            return instance

class BakeryAisleWestBlock(blocks.Block):
        def __init__(self, location: things.Location, mrs_crumble: things.Character, connection: str):
            super().__init__('Mrs. Crumble is blocking the way', 'You need to distract Mrs. Crumble to proceed to the Costco Entrance.')
            self.mrs_crumble = mrs_crumble
            self.location = location
            self.connection = connection  # This parameter reflects the destination name

        def is_blocked(self) -> bool:
            return self.location.here(self.mrs_crumble)
        
        @classmethod
        def from_primitive(cls, data):
            location = data["location"]
            door = data["mrs_crumble"]
            connection = data["connection"]
            instance = cls(location, door, connection)
            return instance

class CheckoutLaneEastBlock(blocks.Block):
        def __init__(self, location: things.Location, rusty_the_security_guard: things.Character, connection: str):
            super().__init__('Rusty the Security Guard is blocking the way', 'You need to distract Rusty the Security Guard to proceed to the Costco Entrance.')
            self.rusty_the_security_guard = rusty_the_security_guard
            self.location = location
            self.connection = connection  # This parameter reflects the destination name

        def is_blocked(self) -> bool:
            return self.location.here(self.rusty_the_security_guard)
        
        @classmethod
        def from_primitive(cls, data):
            location = data["location"]
            door = data["rusty_the_security_guard"]
            connection = data["connection"]
            instance = cls(location, door, connection)
            return instance

class CostcoExitSouthBlock(blocks.Block):
        def __init__(self, location: things.Location, shelly_the_shopper: things.Character, connection: str):
            super().__init__('Shelly the Shopper is blocking the way', 'You need to distract Shelly the Shopper to proceed to the Costco Entrance.')
            self.shelly_the_shopper = shelly_the_shopper
            self.location = location
            self.connection = connection  # This parameter reflects the destination name

        def is_blocked(self) -> bool:
            return self.location.here(self.shelly_the_shopper)
        
        @classmethod
        def from_primitive(cls, data):
            location = data["location"]
            door = data["shelly_the_shopper"]
            connection = data["connection"]
            instance = cls(location, door, connection)
            return instance


class WorldWeaver(games.Game):
    custom_actions = [[Enter, Dodge, Find]]
    custom_blocks=[CostcoEntranceEastBlock, ProduceAisleOutBlock, SecurityGuardStationEastBlock, BakeryAisleWestBlock, CheckoutLaneEastBlock, CostcoExitSouthBlock]
    def __init__(
        self,
        start_at: things.Location,
        player: things.Character,
        characters=None,
        custom_actions=custom_actions,
        custom_blocks=custom_blocks
    ):
        super().__init__(start_at, player, characters, custom_actions, custom_blocks)

    def is_won(self) -> bool:
        """
        Checks whether the game has been won. For this game, the game is won
        once Pippin the Pigeon successfully steals breakfast from Target.
        """
        if self.characters["Pippin the Pigeon"].get_property("Hidden Bread Bud"):
            return True
        return False
