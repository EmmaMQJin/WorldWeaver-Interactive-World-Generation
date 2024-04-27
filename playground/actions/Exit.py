import base
class Exit(base.Action):
    ACTION_NAME = "exit"
    ACTION_DESCRIPTION = "Exit from a location"

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.location = self.character.location

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* The character must be in a location that has an exit
        
        if not self.location.has_exit():
            description = "There's no exit here."
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Moves the character to the exit location
        #* Describes the new location
        self.character.move_to(self.location.get_exit())
        description = "{name} exits to {location}.".format(
            name=self.character.name.capitalize(), location=self.character.location.name
        )
        self.parser.ok(description)