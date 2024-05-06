class CostcoEntranceEastBlock(blocks.Block):
        def __init__(self, location: things.Location, chester_the_sample_giver: things.Character, connection: str):
            super().__init__('Chester the Sample Giver is blocking the way', 'You need to distract Chester the Sample Giver to proceed to the Bakery Aisle.')
            self.chester_the_sample_giver = chester_the_sample_giver
            self.location = location
            self.connection = connection  # This parameter reflects the destination name

        def is_blocked(self) -> bool:
            return self.location.here(self.chester_the_sample_giver)

class ProduceAisleOutBlock(blocks.Block):
        def __init__(self, location: things.Location, bobby_the_shopper: things.Character, connection: str):
            super().__init__('Bobby the Shopper is blocking the way', 'You need to distract Bobby the Shopper to proceed to the Costco Parking Lot.')
            self.bobby_the_shopper = bobby_the_shopper
            self.location = location
            self.connection = connection  # This parameter reflects the destination name

        def is_blocked(self) -> bool:
            return self.location.here(self.bobby_the_shopper)

class SecurityGuardStationEastBlock(blocks.Block):
        def __init__(self, location: things.Location, ranger_feline: things.Character, connection: str):
            super().__init__('Ranger Feline is blocking the way', 'You need to distract Ranger Feline to proceed to the Costco Parking Lot.')
            self.ranger_feline = ranger_feline
            self.location = location
            self.connection = connection  # This parameter reflects the destination name

        def is_blocked(self) -> bool:
            return self.location.here(self.ranger_feline)

class BakeryAisleWestBlock(blocks.Block):
        def __init__(self, location: things.Location, mrs_crumble: things.Character, connection: str):
            super().__init__('Mrs. Crumble is blocking the way', 'You need to distract Mrs. Crumble to proceed to the Costco Entrance.')
            self.mrs_crumble = mrs_crumble
            self.location = location
            self.connection = connection  # This parameter reflects the destination name

        def is_blocked(self) -> bool:
            return self.location.here(self.mrs_crumble)

class CheckoutLaneEastBlock(blocks.Block):
        def __init__(self, location: things.Location, rusty_the_security_guard: things.Character, connection: str):
            super().__init__('Rusty the Security Guard is blocking the way', 'You need to distract Rusty the Security Guard to proceed to the Costco Entrance.')
            self.rusty_the_security_guard = rusty_the_security_guard
            self.location = location
            self.connection = connection  # This parameter reflects the destination name

        def is_blocked(self) -> bool:
            return self.location.here(self.rusty_the_security_guard)

class CostcoExitSouthBlock(blocks.Block):
        def __init__(self, location: things.Location, shelly_the_shopper: things.Character, connection: str):
            super().__init__('Shelly the Shopper is blocking the way', 'You need to distract Shelly the Shopper to proceed to the Costco Entrance.')
            self.shelly_the_shopper = shelly_the_shopper
            self.location = location
            self.connection = connection  # This parameter reflects the destination name

        def is_blocked(self) -> bool:
            return self.location.here(self.shelly_the_shopper)

