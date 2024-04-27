import base
class Unlock(base.Action):
    ACTION_NAME = "unlock"
    ACTION_DESCRIPTION = "Unlock something"

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.item = self.parser.match_item(
            command, self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched item
        #* The item must be lockable
        #* The item must be locked
        #* The character must have a key in their inventory
        
        if not self.was_matched(self.item):
            return False
        if not self.item.get_property("is_lockable"):
            description = "That's not something you can unlock."
            self.parser.fail(description)
            return False
        if not self.item.get_property("is_locked"):
            description = "It's already unlocked."
            self.parser.fail(description)
            return False
        if not self.character.has_key():
            description = "You don't have a key."
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Unlocks the item
        #* Describes the unlocking
        self.item.set_property("is_locked", False)
        description = "{name} unlocks the {item}.".format(
            name=self.character.name.capitalize(), item=self.item.name
        )
        self.parser.ok(description)