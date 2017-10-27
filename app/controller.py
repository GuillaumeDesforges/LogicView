from logic.propositions import *
from app.lang import *

class Controller:
    def __init__(self, app):
        self.app = app
        self.prop_previous = None
        self.prop = None

    def parseInput(self):
        input_str = self.app.propositionInput.text()
        try:
            input_prop = decode_proposition_str(input_str)
        except Exception as e:
            self.app.showError(e)
            return
        self.prop_previous = input_prop.to_cnf().simplify()
        self.prop = self.prop_previous
        self.app.clearMiddle()
        self.app.updatePropositionView(self.prop)

    def clear(self):
        self.prop = self.prop_previous
        self.app.updatePropositionView(self.prop)

    def apply(self):
        operation = self.app.listOperations.currentText()
        variable = Variable(self.app.listVariables.currentText())
        cnf_table = self.prop._get_cnf_table()
        if operation == lang_operations['tautology']:
            cnf_table = [k for k in cnf_table if not (variable in k and Not(variable) in k)]
            self.prop = from_cnf_table(cnf_table).simplify()
        if operation == lang_operations['unitpropagation']:
            var_prop, var_val = None, None
            if [variable] in cnf_table:
                var_prop, var_val = variable, T
            elif [Not(variable)] in cnf_table:
                var_prop, var_val = Not(variable), F
            if var_prop != None:
                cnf_table = [[p if p != var_prop else var_val for p in t] for t in cnf_table if t != [var_prop]]
                self.prop = from_cnf_table(cnf_table).simplify()
        if operation == lang_operations['purlitteralelimination']:
            var_prop, var_val = None, None
            if True in [variable in t for t in cnf_table] and not (True in [Not(variable) in t for t in cnf_table]):
                var_prop, var_val = variable, T
            elif not (True in [variable in t for t in cnf_table]) and True in [Not(variable) in t for t in cnf_table]:
                var_prop, var_val = Not(variable), F
            if var_prop != None:
                cnf_table = [[p if p != var_prop else var_val for p in t] for t in cnf_table if t != [var_prop]]
                self.prop = from_cnf_table(cnf_table).simplify()
        if operation == lang_operations['assigntrue']:
            cnf_table = [t for t in cnf_table if not variable in t]
            self.prop = from_cnf_table(cnf_table)
        if operation == lang_operations['assignfalse']:
            cnf_table = [t for t in cnf_table if not Not(variable) in t]
            self.prop = from_cnf_table(cnf_table)
        self.app.updatePropositionView(self.prop)

    def bind(self):
        self.app.buttonParse.clicked.connect(self.parseInput)
        self.app.buttonReset.clicked.connect(self.clear)
        self.app.buttonApply.clicked.connect(self.apply)
