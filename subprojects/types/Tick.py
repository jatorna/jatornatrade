
class Tick:
    def __init__(self):
        self.name = 0
        self.symbol = ''
        self.price = 0
        self.volume = 0

    def __eq__(self, other):
        if self.symbol == other.symbol and self.price == other.price and self.volume == other.volume:
            return True
        else:
            return False
