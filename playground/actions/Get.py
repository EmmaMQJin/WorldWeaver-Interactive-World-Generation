import base
class Get(base.Action):
    ACTION_NAME = "get"
    ACTION_DESCRIPTION = "Get something and add it to the inventory"
    ACTION_ALIASES = ["retrieve"]

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.location = self.character.location
        self.item = self.parser.match_item(command, self.location.items)

    def check_preconditions(self) -> bool:
       
         #Preconditions:
         #* The item must be matched.
         #* The character must be at the location
         #* The item must be at the location
         #* The item must be gettable
        
        if not self.was_matched(self.item, "I don't see it."):
            message = "I don't see it."
            self.parser.fail(message)
            return False
        if not self.location.here(self.character):
            message = "{name} is not here.".format(name=self.character.name)
            self.parser.fail(message)
            return False
        if not self.location.here(self.item):
            message = "There is no {name} here.".format(name=self.item.name)
            self.parser.fail(message)
            return False
        if not self.item.get_property("is_gettable"):
            error_message = "{name} is not {property_name}.".format(
                name=self.item.name.capitalize(), property_name="gettable"
            )
            self.parser.fail(error_message)
            return False
        return True

    def apply_effects(self):
        
        #Get's an item from the location and adds it to the character's
        #inventory, assuming preconditions are met.
        self.location.remove_item(self.item)
        self.character.add_to_inventory(self.item)
        description = "{character_name} got the {item_name}.".format(
            character_name=self.character.name, item_name=self.item.name
        )
        self.parser.ok(description)