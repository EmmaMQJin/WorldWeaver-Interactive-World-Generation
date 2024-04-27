import base
class Wear(base.Action):
    ACTION_NAME = "wear"
    ACTION_DESCRIPTION = "Wear something"

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.item = self.parser.match_item(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched item
        #* The item must be wearable
        #* The item must be in character's inventory
        
        if not self.was_matched(self.item):
            return False
        elif not self.item.get_property("is_wearable"):
            description = "That's not something you can wear."
            self.parser.fail(description)
            return False
        elif not self.character.is_in_inventory(self.item):
            description = "You don't have it."
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* The character wears the item
        #* Describes the action
        self.character.set_property("is_wearing", self.item)
        description = "{name} wears the {item}.".format(
            name=self.character.name.capitalize(), item=self.item.name
        )
        self.parser.ok(description)