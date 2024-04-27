import base
class Rescue(base.Action):
    ACTION_NAME = "rescue"
    ACTION_DESCRIPTION = "Rescue a character"

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)
        self.target = self.parser.match_character(
            command, self.parser.get_characters_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        
        #Preconditions:
        #* There must be a matched character
        #* The target character must be in danger
        
        if not self.was_matched(self.target):
            return False
        if not self.target.get_property("is_in_danger"):
            description = "{name} is not in danger.".format(name=self.target.name)
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        
        #Effects:
        #* Rescues the target character
        #* Describes the rescue
        self.target.set_property("is_in_danger", False)
        description = "{name} rescues {target}.".format(
            name=self.character.name.capitalize(), target=self.target.name
        )
        self.parser.ok(description)