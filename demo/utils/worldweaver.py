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

class KitchenEastBlock(blocks.Block):
    def __init__(self, location: things.Location, bert_the_beagle: things.Character, connection: str):
        super().__init__('Bert the Beagle is blocking the way', 'You need to distract Bert the Beagle to proceed to the Backyard Tree.')
        self.bert_the_beagle = bert_the_beagle
        self.location = location
        self.connection = connection

    def is_blocked(self) -> bool:
        return self.location.here(self.bert_the_beagle)

class BackyardTreeWestBlock(blocks.Block):
    def __init__(self, location: things.Location, breezy_the_bird: things.Character, connection: str):
        super().__init__('Breezy the Bird is blocking the way', 'You need to distract Breezy the Bird to proceed to the City Alleyways.')
        self.breezy_the_bird = breezy_the_bird
        self.location = location
        self.connection = connection

    def is_blocked(self) -> bool:
        return self.location.here(self.breezy_the_bird)

class NeighborsGardenEastBlock(blocks.Block):
    def __init__(self, location: things.Location, inky_the_neighbor_cat: things.Character, connection: str):
        super().__init__('Inky the Neighbor Cat is blocking the way', 'You need to communicate with Inky the Neighbor Cat to proceed to the City\'s River.')
        self.inky_the_neighbor_cat = inky_the_neighbor_cat
        self.location = location
        self.connection = connection

    def is_blocked(self) -> bool:
        return self.location.here(self.inky_the_neighbor_cat)

class SuburbanCatGangsHideoutWestBlock(blocks.Block):
    def __init__(self, location: things.Location, patches_the_adventurer: things.Character, connection: str):
        super().__init__('Patches the Adventurer is blocking the way', 'You need to organize a voyage with Patches the Adventurer to proceed to the Backyard Tree.')
        self.patches_the_adventurer = patches_the_adventurer
        self.location = location
        self.connection = connection

    def is_blocked(self) -> bool:
        return self.location.here(self.patches_the_adventurer)

class CityAlleywaysEastBlock(blocks.Block):
    def __init__(self, location: things.Location, gruff_the_guardian: things.Character, connection: str):
        super().__init__('Gruff the Guardian is blocking the way', 'You need to navigate through the alleyways with Gruff the Guardian to proceed to the Backyard Tree.')
        self.gruff_the_guardian = gruff_the_guardian
        self.location = location
        self.connection = connection

    def is_blocked(self) -> bool:
        return self.location.here(self.gruff_the_guardian)

class LocalCaninesTerritorySouthBlock(blocks.Block):
    def __init__(self, location: things.Location, rusty_the_old_watchdog: things.Character, connection: str):
        super().__init__('Rusty the Old Watchdog is blocking the way', 'You need to understand the dog\'s bark code and avoid Rusty the Old Watchdog to proceed to the Backyard Tree.')
        self.rusty_the_old_watchdog = rusty_the_old_watchdog
        self.location = location
        self.connection = connection

    def is_blocked(self) -> bool:
        return self.location.here(self.rusty_the_old_watchdog)

class CitysRiverWestBlock(blocks.Block):
    def __init__(self, location: things.Location, zephyr_the_breezy: things.Character, connection: str):
        super().__init__('Zephyr the Breezy is blocking the way', 'You need to cross the river by jumping on stones with Zephyr the Breezy to proceed to the Neighbor\'s Garden.')
        self.zephyr_the_breezy = zephyr_the_breezy
        self.location = location
        self.connection = connection

    def is_blocked(self) -> bool:
        return self.location.here(self.zephyr_the_breezy)

class MountainsBaseEastBlock(blocks.Block):
    def __init__(self, location: things.Location, stonefoot_the_elder: things.Character, connection: str):
        super().__init__('Stonefoot the Elder is blocking the way', 'You need to climb the mountain base with Stonefoot the Elder to proceed to the Neighbor\'s Garden.')
        self.stonefoot_the_elder = stonefoot_the_elder
        self.location = location
        self.connection = connection

    def is_blocked(self) -> bool:
        return self.location.here(self.stonefoot_the_elder)

class EaglesNestDownBlock(blocks.Block):
    def __init__(self, location: things.Location, aelius_the_wise: things.Character, connection: str):
        super().__init__('Aelius the Wise is blocking the way', 'You need to distract Aelius the Wise to proceed to the Neighbor\'s Garden.')
        self.aelius_the_wise = aelius_the_wise
        self.location = location
        self.connection = connection

    def is_blocked(self) -> bool:
        return self.location.here(self.aelius_the_wise)

class MountainPeakWestBlock(blocks.Block):
    def __init__(self, location: things.Location, shadow_the_scavenger: things.Character, connection: str):
        super().__init__('Shadow the Scavenger is blocking the way', 'You need to declare the mountain as cat territory with Shadow the Scavenger to proceed to the Suburban Cat Gang\'s Hideout.')
        self.shadow_the_scavenger = shadow_the_scavenger
        self.location = location
        self.connection = connection

    def is_blocked(self) -> bool:
        return self.location.here(self.shadow_the_scavenger)


class KitchenEastBlock(blocks.Block):
    def __init__(self, location: things.Location, bert_the_beagle: things.Character, connection: str):
        super().__init__('Bert the Beagle is blocking the way', 'You need to distract Bert the Beagle to proceed to the Backyard Tree.')
        self.bert_the_beagle = bert_the_beagle
        self.location = location
        self.connection = connection

    def is_blocked(self) -> bool:
        return self.location.here(self.bert_the_beagle)

class BackyardTreeWestBlock(blocks.Block):
    def __init__(self, location: things.Location, breezy_the_bird: things.Character, connection: str):
        super().__init__('Breezy the Bird is blocking the way', 'You need to distract Breezy the Bird to proceed to the City Alleyways.')
        self.breezy_the_bird = breezy_the_bird
        self.location = location
        self.connection = connection

    def is_blocked(self) -> bool:
        return self.location.here(self.breezy_the_bird)

class NeighborsGardenEastBlock(blocks.Block):
    def __init__(self, location: things.Location, inky_the_neighbor_cat: things.Character, connection: str):
        super().__init__('Inky the Neighbor Cat is blocking the way', 'You need to communicate with Inky the Neighbor Cat to proceed to the City\'s River.')
        self.inky_the_neighbor_cat = inky_the_neighbor_cat
        self.location = location
        self.connection = connection

    def is_blocked(self) -> bool:
        return self.location.here(self.inky_the_neighbor_cat)

class SuburbanCatGangsHideoutWestBlock(blocks.Block):
    def __init__(self, location: things.Location, patches_the_adventurer: things.Character, connection: str):
        super().__init__('Patches the Adventurer is blocking the way', 'You need to organize a voyage with Patches the Adventurer to proceed to the Backyard Tree.')
        self.patches_the_adventurer = patches_the_adventurer
        self.location = location
        self.connection = connection

    def is_blocked(self) -> bool:
        return self.location.here(self.patches_the_adventurer)

class CityAlleywaysEastBlock(blocks.Block):
    def __init__(self, location: things.Location, gruff_the_guardian: things.Character, connection: str):
        super().__init__('Gruff the Guardian is blocking the way', 'You need to navigate through the alleyways with Gruff the Guardian to proceed to the Backyard Tree.')
        self.gruff_the_guardian = gruff_the_guardian
        self.location = location
        self.connection = connection

    def is_blocked(self) -> bool:
        return self.location.here(self.gruff_the_guardian)

class LocalCaninesTerritorySouthBlock(blocks.Block):
    def __init__(self, location: things.Location, rusty_the_old_watchdog: things.Character, connection: str):
        super().__init__('Rusty the Old Watchdog is blocking the way', 'You need to understand the dog\'s bark code and avoid Rusty the Old Watchdog to proceed to the Backyard Tree.')
        self.rusty_the_old_watchdog = rusty_the_old_watchdog
        self.location = location
        self.connection = connection

    def is_blocked(self) -> bool:
        return self.location.here(self.rusty_the_old_watchdog)

class CitysRiverWestBlock(blocks.Block):
    def __init__(self, location: things.Location, zephyr_the_breezy: things.Character, connection: str):
        super().__init__('Zephyr the Breezy is blocking the way', 'You need to cross the river by jumping on stones with Zephyr the Breezy to proceed to the Neighbor\'s Garden.')
        self.zephyr_the_breezy = zephyr_the_breezy
        self.location = location
        self.connection = connection

    def is_blocked(self) -> bool:
        return self.location.here(self.zephyr_the_breezy)

class MountainsBaseEastBlock(blocks.Block):
    def __init__(self, location: things.Location, stonefoot_the_elder: things.Character, connection: str):
        super().__init__('Stonefoot the Elder is blocking the way', 'You need to climb the mountain base with Stonefoot the Elder to proceed to the Neighbor\'s Garden.')
        self.stonefoot_the_elder = stonefoot_the_elder
        self.location = location
        self.connection = connection

    def is_blocked(self) -> bool:
        return self.location.here(self.stonefoot_the_elder)

class EaglesNestDownBlock(blocks.Block):
    def __init__(self, location: things.Location, aelius_the_wise: things.Character, connection: str):
        super().__init__('Aelius the Wise is blocking the way', 'You need to distract Aelius the Wise to proceed to the Neighbor\'s Garden.')
        self.aelius_the_wise = aelius_the_wise
        self.location = location
        self.connection = connection

    def is_blocked(self) -> bool:
        return self.location.here(self.aelius_the_wise)

class MountainPeakWestBlock(blocks.Block):
    def __init__(self, location: things.Location, shadow_the_scavenger: things.Character, connection: str):
        super().__init__('Shadow the Scavenger is blocking the way', 'You need to declare the mountain as cat territory with Shadow the Scavenger to proceed to the Suburban Cat Gang\'s Hideout.')
        self.shadow_the_scavenger = shadow_the_scavenger
        self.location = location
        self.connection = connection

    def is_blocked(self) -> bool:
        return self.location.here(self.shadow_the_scavenger)

class WorldWeaver(games.Game):
    def __init__(
        self,
        start_at: things.Location,
        player: things.Character,
        characters=None,
        custom_actions=[Climb, Spot, Decode],
        custom_blocks=[KitchenEastBlock, BackyardTreeWestBlock, NeighborsGardenEastBlock, SuburbanCatGangsHideoutWestBlock, CityAlleywaysEastBlock, LocalCaninesTerritorySouthBlock, CitysRiverWestBlock, MountainsBaseEastBlock, EaglesNestDownBlock, MountainPeakWestBlock]
    ):
        super().__init__(start_at, player, characters, custom_actions, custom_blocks)

    def is_won(character) -> bool:
        """
        Checks whether the game has been won. The game is won
        once the character Whisper is on a mountain.
        """
        if character['name'] == 'Whisper' and character['location'] == 'mountain':
            return True
        return False
