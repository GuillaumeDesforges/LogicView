from logic.propositions import *

class Controller:
    def __init__(self, app):
        self.app = app
        self.prop = None

    def parseInput(self):
        input_str = self.app.propositionInput.text()
        try:
            input_prop = decode_proposition_str(input_str)
        except Exception as e:
            self.app.showError(e)
            return
        self.prop = input_prop.to_cnf().simplify()
        self.app.updatePropositionView(self.prop)

    def clear(self):
        self.app.clearMiddle(self.prop)

    def bind(self):
        self.app.buttonParse.clicked.connect(self.parseInput)
        self.app.buttonReset.clicked.connect(self.clear)
