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
        self.app.clearMiddle()
        self.app.updatePropositionView(self.prop)

    def clear(self):
        self.app.clearMiddle()
        self.app.updatePropositionView(self.prop)

    def apply(self):
        if self.app.listOperations.currentText() == self.app.listOperationsOptions['tautology']:
            variables = [Variable(var_name) for var_name in self.prop.list_var_names()]
            cnf_table = self.prop._get_cnf_table()
            for variable in variables:
                cnf_table = [k for k in cnf_table if not variable in k or not Not(variable) in k]
            self.prop = Proposition._from_cnf_table(cnf_table)
        self.app.updatePropositionView(self.prop)

    def bind(self):
        self.app.buttonParse.clicked.connect(self.parseInput)
        self.app.buttonReset.clicked.connect(self.clear)
        self.app.buttonApply.clicked.connect(self.apply)
