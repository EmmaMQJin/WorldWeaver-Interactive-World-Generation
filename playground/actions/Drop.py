import base
class Drop(base.Action):
    ACTION_NAME = "drop"
    ACTION_DESCRIPTION = "Drop something from your inventory"

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
        elif not self.character.is_in_inventory(self.item):
            description = "You don't have it."
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Removes the item from the character's inventory
        #* Adds the item to the current location's items
        #* Describes the dropping
        self.character.remove_from_inventory(self.item)
        self.character.location.add_item(self.item)
        description = "{name} drops the {item}.".format(
            name=self.character.name.capitalize(), item=self.item.name
        )
        self.parser.ok(description)