from text_adventure_games import games, things, actions
from .base import Action
class Locate(actions.Action):
    ACTION_NAME = "locate"
    ACTION_DESCRIPTION = "Locate an item or character"
    ACTION_ALIASES = ["find"]

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
            description = "The target couldn't be found."
            self.parser.fail(description)
            return False
        if not self.character.location.here(self.target):
            description = "The target is not here."
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Describes the location of the target
        
        description = "{name} locates the {target}.".format(
            name=self.character.name.capitalize(), target=self.target.name
        )
        self.parser.ok(description)
class Observe(actions.Action):
    ACTION_NAME = "observe"
    ACTION_DESCRIPTION = "Observe something or someone"
    ACTION_ALIASES = ["watch", "view"]

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
            description = "There's nothing to observe."
            self.parser.fail(description)
            return False
        if not self.character.location.here(self.target):
            description = "The target is not here."
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Describes the target
        
        description = "{name} observes the {target}.".format(
            name=self.character.name.capitalize(), target=self.target.name
        )
        if self.target.description:
            description += " " + self.target.description
        self.parser.ok(description)
class Distract(actions.Action):
    ACTION_NAME = "distract"
    ACTION_DESCRIPTION = "Distract a character"
    ACTION_ALIASES = ["divert"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.target = self.parser.get_character(
            command, hint="target", split_words=["distract", "divert"], position="after"
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a character and a target
        #* They must be in the same location
        #* The target must not already be distracted
        
        if not self.was_matched(self.character):
            description = "The character couldn't be found."
            self.parser.fail(description)
            return False
        if not self.was_matched(self.target):
            description = "The target to distract wasn't matched."
            self.parser.fail(description)
            return False
        if not self.character.location.here(self.target):
            description = "The two characters must be in the same location."
            self.parser.fail(description)
            return False
        if self.target.get_property("is_distracted"):
            description = "{name} is already distracted".format(name=self.target.name)
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Distracts the target
        #* Describes the distraction
        
        self.target.set_property("is_distracted", True)
        description = "{name} distracts {target}.".format(
            name=self.character.name.capitalize(), target=self.target.name
        )
        self.parser.ok(description)
class Fly(actions.Action):
    ACTION_NAME = "fly"
    ACTION_DESCRIPTION = "Fly to a location"

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.location = self.parser.match_location(
            command, self.game.locations
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched location
        #* The character must be able to fly
        
        if not self.was_matched(self.location):
            return False
        if not self.character.get_property("can_fly"):
            description = "You can't fly."
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Moves the character to the location
        #* Describes the flight and arrival
        
        self.character.location = self.location
        description = "{name} flies to {location}.".format(
            name=self.character.name.capitalize(), location=self.location.name
        )
        self.parser.ok(description)
class Wait(actions.Action):
    ACTION_NAME = "wait"
    ACTION_DESCRIPTION = "Wait for a while"

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)

    def check_preconditions(self) -> bool:
        # There are no preconditions for waiting
        return True

    def apply_effects(self):
        # There are no effects for waiting
        description = "{name} waits for a while.".format(
            name=self.character.name.capitalize()
        )
        self.parser.ok(description)
class Grab(actions.Action):
    ACTION_NAME = "grab"
    ACTION_DESCRIPTION = "Grab an item"
    ACTION_ALIASES = ["seize", "snatch"]

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
class Avoid(actions.Action):
    ACTION_NAME = "avoid"
    ACTION_DESCRIPTION = "Avoid an attack or a dangerous situation"
    ACTION_ALIASES = ["evade", "dodge"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.danger = self.parser.match_item(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched danger
        #* The danger must be avoidable
        #* The character must not already be safe from the danger
        
        if not self.was_matched(self.danger):
            return False
        if not self.danger.get_property("is_avoidable"):
            description = "That's not something you can avoid."
            self.parser.fail(description)
            return False
        if self.character.get_property("is_safe"):
            description = "You are already safe."
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Makes the character safe from the danger
        #* Describes the avoidance
        self.character.set_property("is_safe", True)
        description = "{name} avoids the {danger}.".format(
            name=self.character.name.capitalize(), danger=self.danger.name
        )
        self.parser.ok(description)
class Hide(actions.Action):
    ACTION_NAME = "hide"
    ACTION_DESCRIPTION = "Hide an item"
    ACTION_ALIASES = ["conceal"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.item = self.parser.match_item(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched item
        #* The item must be in the character's inventory
        
        if not self.was_matched(self.item):
            return False
        if not self.character.is_in_inventory(self.item):
            description = "You don't have it."
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Removes the item from the character's inventory
        #* Adds the item to the location's hidden items
        #* Describes the hiding
        self.character.remove_from_inventory(self.item)
        self.character.location.add_hidden_item(self.item)
        description = "{name} hides the {item}.".format(
            name=self.character.name.capitalize(), item=self.item.name
        )
        self.parser.ok(description)
class Create(actions.Action):
    ACTION_NAME = "create"
    ACTION_DESCRIPTION = "Create something"

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.item_name = self.parser.get_item_name(command)

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* The character must have the necessary skills to create the item
        #* The character must have the necessary materials in their inventory
        
        if not self.character.has_skill("crafting"):
            description = "You don't have the necessary skills to create this."
            self.parser.fail(description)
            return False
        if not self.character.has_materials(self.item_name):
            description = "You don't have the necessary materials to create this."
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Creates the item and adds it to the character's inventory
        #* Removes the necessary materials from the character's inventory
        #* Describes the creation of the item
        self.character.create_item(self.item_name)
        description = "{name} creates a {item}.".format(
            name=self.character.name.capitalize(), item=self.item_name
        )
        self.parser.ok(description)
class Exit(actions.Action):
    ACTION_NAME = "exit"
    ACTION_DESCRIPTION = "Exit from a location"
    ACTION_ALIASES = ["leave"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.location = self.character.location

    def check_preconditions(self) -> bool:
        
        # Preconditions:
        # * The character must be in a location that has an exit
        
        if not self.location.get_connection("out"):
            description = "There's no way out."
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        # Effects:
        # * Moves the character to the connected location
        # * Describes the new location
        
        new_location = self.location.get_connection("out")
        self.character.location = new_location
        description = "{name} exits to the {new_location}.".format(
            name=self.character.name.capitalize(), new_location=new_location.name
        )
        self.parser.ok(description)
        self.game.describe_location(new_location)
class Celebrate(actions.Action):
    ACTION_NAME = "celebrate"
    ACTION_DESCRIPTION = "Celebrate a victory or achievement"

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* The character must have achieved a goal
        
        if not self.character.get_property("goal_achieved"):
            description = "{name} has nothing to celebrate.".format(
                name=self.character.name.capitalize()
            )
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Describes the celebration
        description = "{name} celebrates their victory!".format(
            name=self.character.name.capitalize()
        )
        self.parser.ok(description)


class WorldWeaver(games.Game):
    def __init__(
        self,
        start_at: things.Location,
        player: things.Character,
        characters=None,
        custom_actions=[Locate, Observe, Distract, Celebrate, Wait, Avoid, Exit, Create, Hide, Grab, Locate, Fly],
    ):
        
        super().__init__(start_at, player, characters, custom_actions)

    def is_won(self) -> bool:
        """
        Checks whether the game has been won. For Action Castle, the game is won
        once any character is sitting on the throne (has the property is_reigning).
        """
        for name, character in self.characters.items():
            if character.get_property("bun_stolen"):
                self.parser.ok(
                    "{name} has now stolen the bun and has won the game!".format(
                        name=character.name.title()
                    )
                )
                return True
        return False