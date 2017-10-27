from logic.propositions import *
from app.lang import *

# application controller
class Controller:
    def __init__(self, app):
        self.app = app
        # not much in the model, so we store it here
        self.prop_history = []

    # 'parse' button handler
    # parse top input field to a CNF proposition object
    def parseInput(self):
        # get text input from field
        input_str = self.app.propositionInput.text()
        # check input is not empty
        if input_str == "":
            self.app.showError(lang_error['input_empty'])
            return
        # try to parse input to proposition
        try:
            input_prop = decode_proposition_str(input_str)
        except Exception as e:
            self.app.showError(e)
            return
        # update Model
        # to CNF and simplify it
        self.prop_history = [input_prop.to_cnf().simplify()]
        # UI update
        self.app.clearMiddle()
        self.app.updatePropositionView(self.prop_history[0])

    # 'clear' button handler
    def clear(self):
        if len(self.prop_history) > 1:
            # update Model
            self.prop_history = self.prop_history[:-1]
            # UI update
            self.app.updatePropositionView(self.prop_history[-1])
        else:
            self.app.showError(lang_error['history_empty'])

    # 'apply' button handler
    def apply(self):
        # get last proposition
        prop = self.prop_history[-1]
        # operation querried
        operation = self.app.listOperations.currentText()
        # variable querried
        variable = Variable(self.app.listVariables.currentText())
        # CNF table ands(ors)
        cnf_table = prop._get_cnf_table()
        # tautology operation
        if operation == lang_operations['tautology']:
            cnf_table = [k for k in cnf_table if not (variable in k and Not(variable) in k)]
            prop = from_cnf_table(cnf_table).simplify()
        # unit propagation operation
        if operation == lang_operations['unitpropagation']:
            var_prop, var_val = None, None
            if [variable] in cnf_table:
                var_prop, var_val = variable, T
            elif [Not(variable)] in cnf_table:
                var_prop, var_val = Not(variable), F
            if var_prop != None:
                cnf_table = [[p if p != var_prop else var_val for p in t] for t in cnf_table if t != [var_prop]]
                prop = from_cnf_table(cnf_table).simplify()
        # pur litteral elimination operation
        if operation == lang_operations['purlitteralelimination']:
            var_prop, var_val = None, None
            if True in [variable in t for t in cnf_table] and not (True in [Not(variable) in t for t in cnf_table]):
                var_prop, var_val = variable, T
            elif not (True in [variable in t for t in cnf_table]) and True in [Not(variable) in t for t in cnf_table]:
                var_prop, var_val = Not(variable), F
            if var_prop != None:
                cnf_table = [[p if p != var_prop else var_val for p in t] for t in cnf_table if t != [var_prop]]
                prop = from_cnf_table(cnf_table).simplify()
        # assign true operation
        if operation == lang_operations['assigntrue']:
            cnf_table = [t for t in cnf_table if not variable in t]
            prop = from_cnf_table(cnf_table)
        # assign false operation
        if operation == lang_operations['assignfalse']:
            cnf_table = [t for t in cnf_table if not Not(variable) in t]
            prop = from_cnf_table(cnf_table)
        # update Model
        self.prop_history.append(prop)
        # update UI
        self.app.updatePropositionView(prop)

    # bind event handlers to UI
    def bind(self):
        self.app.buttonParse.clicked.connect(self.parseInput)
        self.app.buttonReset.clicked.connect(self.clear)
        self.app.buttonApply.clicked.connect(self.apply)
