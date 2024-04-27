import base
class Enter(base.Action):
    ACTION_NAME = "enter"
    ACTION_DESCRIPTION = "Enter a location or a vehicle"

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.location = self.parser.match_location(
            command, self.parser.get_locations_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched location
        #* The location must be accessible from the current location
        
        if not self.was_matched(self.location):
            return False
        if not self.character.location.is_connected_to(self.location):
            description = "You can't get there from here."
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