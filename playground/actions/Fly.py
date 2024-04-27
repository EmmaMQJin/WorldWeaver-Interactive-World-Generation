import base
class Fly(base.Action):
    ACTION_NAME = "fly"
    ACTION_DESCRIPTION = "Fly to a location"

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.location = self.parser.match_location(
            command, self.parser.get_locations_in_scope(self.character)
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
        #* Describes the flight
        self.character.move_to(self.location)
        description = "{name} flies to {location}.".format(
            name=self.character.name.capitalize(), location=self.location.name
        )
        self.parser.ok(description)