import base
class Gather(base.Action):
    ACTION_NAME = "gather"
    ACTION_DESCRIPTION = "Gather items from the environment"

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.location = self.character.location

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be items in the location
        #* The items must be gettable
        
        if not self.location.items:
            description = "There's nothing to gather here."
            self.parser.fail(description)
            return False
        for item in self.location.items:
            if not item.get_property("is_gettable"):
                description = "You can't gather {item_name}.".format(item_name=item.name)
                self.parser.fail(description)
                return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Adds all gettable items in the location to the character's inventory
        #* Removes all gettable items from the location
        #* Describes the gathering
        for item in self.location.items:
            self.character.add_to_inventory(item)
            self.location.remove_item(item)
        description = "{name} gathers all items.".format(name=self.character.name.capitalize())
        self.parser.ok(description)