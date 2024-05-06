class Constants:
    worldweaver_init = """
    class WorldWeaver(games.Game):
        def __init__(
            self,
            start_at: things.Location,
            player: things.Character,
            characters=None,
            #custom_actions=[Locate, Observe, Distract, Celebrate, Wait, Avoid, Exit, Create, Hide, Grab, Locate, Fly],
            custom_actions=None,
        ):
            super().__init__(start_at, player, characters, custom_actions)
    """
