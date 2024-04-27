import base
class Celebrate(base.Action):
    ACTION_NAME = "celebrate"
    ACTION_DESCRIPTION = "Celebrate a victory or achievement"

    def __init__(self, game, command: str):
        super().__init__(game)
        self.character = self.parser.get_character(command)

    def check_preconditions(self) -> bool:
        #Preconditions:
        #* The character must be alive
        if not self.character.get_property("is_alive"):
            description = "{name} is not alive to celebrate.".format(
                name=self.character.name.capitalize()
            )
            self.parser.fail(description)
            return False
        return True

    def apply_effects(self):
        #Effects:
        #* Describes the celebration
        description = "{name} celebrates with joy.".format(
            name=self.character.name.capitalize()
        )
        self.parser.ok(description)