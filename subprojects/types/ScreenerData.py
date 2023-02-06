

class ScreenerOutputData:
    def __init__(self):
        self.datetime = ''
        self.symbols = []

    def set_data(self, datetime, symbols):
        self.datetime = datetime
        self.symbols = symbols

    def print_header(self):
        header = "      Date  Symbols\n"
        return header

    def print_data(self):
        data = ''
        if not self.datetime == '':
            data = self.datetime.strftime("%m/%d/%Y")

        for symbol in self.symbols:
            data += " " + symbol

        data += '\n'

        return data

    def clear(self):
        self.datetime = ''
        self.symbols = []

