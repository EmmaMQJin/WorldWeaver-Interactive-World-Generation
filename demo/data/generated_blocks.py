('Costco Roof', 'up', 'Pigeon Nest', 
'''
class CostcoRoofUpBlock(blocks.Block):
    def __init__(self, location: things.Location, chopper_the_crow: things.Character, connection: str):
        super().__init__('Chopper the Crow is blocking the way', 'You need to distract Chopper the Crow to proceed to the Pigeon Nest.')
        self.chopper_the_crow = chopper_the_crow
        self.location = location
        self.connection = connection  # This parameter reflects the destination name

    def is_blocked(self) -> bool:
        return self.location.here(self.chopper_the_crow)
'''),

('Costco Food Court', 'east', 'Pigeon Nest', 
'''
class CostcoFoodCourtEastBlock(blocks.Block):
    def __init__(self, location: things.Location, watcher_willis: things.Character, connection: str):
        super().__init__('Watcher Willis is blocking the way', 'You need to distract Watcher Willis to proceed to the Pigeon Nest.')
        self.watcher_willis = watcher_willis
        self.location = location
        self.connection = connection  # This parameter reflects the destination name

    def is_blocked(self) -> bool:
        return self.location.here(self.watcher_willis)
'''),

('Pizza Stand', 'west', 'Costco Parking Lot', 
'''
class PizzaStandWestBlock(blocks.Block):
    def __init__(self, location: things.Location, cheesy_the_cashier: things.Character, connection: str):
        super().__init__('Cheesy the Cashier is blocking the way', 'You need to distract Cheesy the Cashier to proceed to the Costco Parking Lot.')
        self.cheesy_the_cashier = cheesy_the_cashier
        self.location = location
        self.connection = connection  # This parameter reflects the destination name

    def is_blocked(self) -> bool:
        return self.location.here(self.cheesy_the_cashier)
'''),

('Territory of the Seagulls', 'east', 'Costco Parking Lot', 
'''
class TerritoryOfTheSeagullsEastBlock(blocks.Block):
    def __init__(self, location: things.Location, swooper_the_scout: things.Character, connection: str):
        super().__init__('Swooper the Scout is blocking the way', 'You need to distract Swooper the Scout to proceed to the Costco Parking Lot.')
        self.swooper_the_scout = swooper_the_scout
        self.location = location
        self.connection = connection  # This parameter reflects the destination name

    def is_blocked(self) -> bool:
        return self.location.here(self.swooper_the_scout)
''')