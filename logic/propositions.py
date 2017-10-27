#!/usr/bin/python3

"""

==== TD Log : TP 1 ===

Guillaume Desforges
Created on 2017/10/02

Logic module :
- true/false logic ( T and F instances from Value class )
- name logic variables
- create logic propositions by combining variables into logic gates
- read proposition from str
- print truth table of propositions
- search counter examples of propositions (where result is false)

"""

from abc import ABC, abstractmethod
from inspect import signature
from itertools import product, chain
from re import search


# Abstract class Proposition : abstract evaluate, priority management
class Proposition(ABC):
    def __init__(self):
        # defines which propositions have higher priority
        # higher priority means parenthesis aren't needed on __str__
        self._upper_priority_prop_class_list = []
        # representation on call of __str__
        # is formatted with self args, so you only need to write '{}' as many args there are
        # see following proposition definition for examples
        self._representation = ""
        self._ordered_args = False

    # evaluation will be recursive
    @abstractmethod
    def evaluate(self, variables):
        """Evaluate truth value of self with given values for its variables

        Parameters
        ----------
        variables : dict
            Description:
                * dict of truth values (True or False) for every named variable
                * every named variable in self should find a value in the dict thanks to its name
                * can contain unused variable names in keys, it won't be used
            Example:
                {'A': True, 'B': False}
        """
        pass

    # used in __str__ to enclose properly according to priority
    def enclose_priority(self, arg):
            if arg.__class__ in self._upper_priority_prop_class_list:
                return str(arg)
            else:
                return "({})".format(arg)

    # get all variable names in proposition recursively
    def list_var_names(self):
        if self.__class__ == Value:
            return []
        elif self.__class__ == Variable:
            # on a leaf it is a variable, get variable name
            return [str(self)]
        else:
            # list number of tree branches
            n_args = len(signature(self.__class__.__init__).parameters) - 1
            # get all subtrees
            args = (getattr(self, "arg"+str(i+1)) for i in range(n_args))
            # explore those subtrees, get results
            sub_var_names = [arg.list_var_names() for arg in args]
            # concatenation of those results into a 1D list
            merged_names = chain(*(sub_var_name for sub_var_name in sub_var_names))
            unique_names = list(set(list(merged_names)))
            return sorted(unique_names)

    def search_counter_example(self):
        var_names = self.list_var_names()
        # try all combinations until counter example is found
        for variables in variable_input_possibilities(var_names):
            test_result = self.evaluate(variables)
            if not test_result:
                return variables
        return None

    def check_theorem(self):
        print("Searching for a counter example for theorem ", str(self))
        counter_example_variables = self.search_counter_example()
        if counter_example_variables == None:
            print("No counter example, theorem is true.")
        else:
            bool_repr = lambda x : "T" if x else "F"
            variables_str = ("{}={}".format(var_name, bool_repr(var_val))
                             for (var_name, var_val)
                             in counter_example_variables.items())
            print("Found counter example, theorem is false.")
            print("False case input values :", *variables_str)

    # should NOT be overwritten
    def simplify(self):
        # Value and Variable can't be simplified, bottom reached
        if self.__class__ in [Value, Variable]:
            return self
        # Simplify args
        n_args = len(signature(self.__class__.__init__).parameters) - 1
        args_simplified = (getattr(self, "arg"+str(i+1)).simplify()
                           for i in range(n_args))
        # Make (potentially) simplified proposition
        self_simplified = self.__class__(*args_simplified)
        # Use proposition local simplification function
        self_simplified = self_simplified._local_simplify()
        # Return result
        return self_simplified

    # should be overwritten in Proposition derived classes definition
    # consider self args in this method are already simplified as much as possible
    def _local_simplify(self):
        print("WARNING : No local simplification defined for class", self.__class__.__name__)
        return self

    # returns CNF equivalent Proposition of self
    # must not be overwritten
    def to_cnf(self):
        # build CNF table as described before _build_cnf declaration above
        cnf_table = self._get_cnf_table()
        return from_cnf_table(cnf_table)

    # construct a 2 depth list : first layers for And, second layer for Or
    # describing cnf locally in the tree
    # this first allows for easier concatenations
    def _build_cnf(self):
        print("WARNING : No local CNF defined for class", self.__class__.__name__)
        return [[self]]

    # get cnf table without duplicates
    def _get_cnf_table(self):
        table = [list(set(t)) for t in self._build_cnf()]
        table_str = [sorted([str(p) for p in t]) for t in table]
        p_table, s_table = [], []
        for (t, s) in zip(table, table_str):
            if not s in s_table:
                p_table.append(t)
                s_table.append(s)
        return p_table

    # in most case, should NOT be overwritten
    def __str__(self):
        # count number of sub propositions of self
        n_args = len(signature(self.__class__.__init__).parameters) - 1
        # get str representation of sub propositions with good priorities
        args_str = [self.enclose_priority(getattr(self, "arg"+str(i+1)))
                    for i in range(n_args)]
        if not self._ordered_args:
            args_str = sorted(args_str)
        # return representation, filled with sub propositions' representations
        return self._representation.format(*tuple(args_str))

    def __eq__(self, other):
        return issubclass(other.__class__, Proposition) and str(self) == str(other)

    def __hash__(self):
        return hash((self.__class__, str(self)))

    def __lt__(self, other):
         return str(self) < str(other)

# Specific, do not reproduce
class Value(Proposition):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def evaluate(self, variables):
        return self.value

    def _build_cnf(self):
        return [[self]]

    def __str__(self):
        return "T" if self.value else "F"

T = Value(True)
F = Value(False)

# Specific, do not reproduce
# "Variable" class : inputs of any proposition
class Variable(Proposition):
    def __init__(self, name):
        super().__init__()
        self._name = name

    def evaluate(self, variables):
        # check if variable value was set in input for evaluation
        if(not self._name in variables):
            str_varlist = str(list(variables)).strip('[]').replace('\'', '')
            raise Exception("Variable value not defined : {} \n" +
                "List of defined variables : {}".format(self._name,
                                                        str_varlist))
        return variables[self._name]

    def _local_simplify(self):
        return self

    def _build_cnf(self):
        return [[self]]

    # only exception
    def __str__(self):
        return self._name


# Starting here, some examples of Proposition creation
# Use it as examples

# "Not" class : classic 'not' gate, basic example of proposition building
class Not(Proposition):
    def __init__(self, arg1):
        super().__init__()
        self.arg1 = arg1
        self._representation = "-{}"
        self._upper_priority_prop_class_list = [Value, Variable, Not]

    def evaluate(self, variables):
        return not self.arg1.evaluate(variables)

    def _local_simplify(self):
        arg1_simplified = self.arg1.simplify()
        if arg1_simplified == T:
            return F
        elif arg1_simplified == F:
            return T
        elif arg1_simplified.__class__ == Not:
            return arg1_simplified.arg1.simplify()
        else:
            return self

    def _build_cnf(self):
        if self.arg1.__class__ == Not:
            return self.arg1.arg1._build_cnf()
        p = self.arg1.to_cnf()
        if p.__class__ == Variable:
            return [[self]]
        if p.__class__ == And:
            return Or(Not(self.arg1.arg1.to_cnf()), Not(self.arg1.arg2.to_cnf()))._build_cnf()
        if p.__class__ == Or:
            return And(Not(self.arg1.arg1.to_cnf()), Not(self.arg1.arg2.to_cnf()))._build_cnf()

# "And" class and following classes follow "Not" class example
class And(Proposition):
    def __init__(self, arg1, arg2):
        super().__init__()
        self.arg1 = arg1
        self.arg2 = arg2
        self._representation = "{} /\\ {}"
        self._upper_priority_prop_class_list = [Value, Variable, Not, And]

    def evaluate(self, variables):
        return self.arg1.evaluate(variables) and self.arg2.evaluate(variables)

    def _local_simplify(self):
        if self.arg1 == T:
            return self.arg2
        elif self.arg2 == T:
            return self.arg1
        elif self.arg1 == F or self.arg2 == F:
            return F
        else:
            return self

    def _build_cnf(self):
        p = self.arg1._build_cnf()
        q = self.arg2._build_cnf()
        return p + q


class Or(Proposition):
    def __init__(self, arg1, arg2):
        super().__init__()
        self.arg1 = arg1
        self.arg2 = arg2
        self._representation = "{} \\/ {}"
        self._upper_priority_prop_class_list = [Value, Variable, Not, And, Or]

    def evaluate(self, variables):
        return self.arg1.evaluate(variables) or self.arg2.evaluate(variables)

    def _local_simplify(self):
        if self.arg1 == F:
            return self.arg2
        elif self.arg2 == F:
            return self.arg1
        elif self.arg1 == T or self.arg2 == T:
            return T
        else:
            return self

    def _build_cnf(self):
        p = self.arg1._build_cnf()
        q = self.arg2._build_cnf()
        return [pi+qi for pi in p for qi in q]


class Implies(Proposition):
    def __init__(self, arg1, arg2):
        super().__init__()
        self.arg1 = arg1
        self.arg2 = arg2
        self._representation = "{} => {}"
        self._upper_priority_prop_class_list = [Value, Variable, Not, And, Or]
        self._ordered_args = True

    def evaluate(self, variables):
        return (not self.arg1.evaluate(variables)) or self.arg2.evaluate(variables)

    def _local_simplify(self):
        if self.arg2 == T:
            return T
        elif self.arg1 == T:
            return self.arg2.simplify()
        elif self.arg2 == F:
            return Not(self.arg1).simplify()
        elif self.arg1 == F:
            return T
        else:
            return self

    def _build_cnf(self):
        return Or(Not(self.arg1), self.arg2)._build_cnf()


class Equivalent(Proposition):
    def __init__(self, arg1, arg2):
        super().__init__()
        self.arg1 = arg1
        self.arg2 = arg2
        self._representation = "{} <=> {}"
        self._upper_priority_prop_class_list = [Value, Variable, Not, And, Or,
                                                Implies, Equivalent]

    def evaluate(self, variables):
        vA = self.arg1.evaluate(variables)
        vB = self.arg2.evaluate(variables)
        return (vA and vB) or ((not vA) and (not vB))

    def _local_simplify(self):
        if self.arg2 == T:
            return self.arg1
        elif self.arg1 == T:
            return self.arg2
        elif self.arg2 == F:
            return Not(self.arg1)
        elif self.arg1 == F:
            return Not(self.arg2)
        else:
            return self

    def _build_cnf(self):
        return Or(And(self.arg1, self.arg2), And(Not(self.arg1), Not(self.arg2)))._build_cnf()


# build all (variable, True or False) dict for proposition testing
def variable_input_possibilities(var_names):
    for var_vals in product([True, False], repeat=len(var_names)):
        yield dict((var_names[i], var_val)
                   for i, var_val in enumerate(var_vals))


def print_truth_table(prop_class):
    # number of parameters of the operator (self excluded)
    n_args = len(signature(prop_class.__init__).parameters) - 1
    # generate enough Variable instances
    var_test = (Variable("arg"+str(i)) for i in range(n_args))
    # create instance of operator
    prop_inst = prop_class(*var_test)
    # pretty print
    print("--- " + prop_class.__name__ + " : " + str(prop_inst))
    print(*("arg"+str(i) for i in range(n_args)), "Result")
    # iterate possibilities
    for variables in variable_input_possibilities(['arg'+str(i)
                                                   for i in range(n_args)]):
        # print : list of arg values, then truth value with such inputs
        print(*(val for (key, val) in variables.items()),
              prop_inst.evaluate(variables))


# "One does not simply 'eval' a user input"
def decode_proposition_str(theorem_str):
    # remove spaces and newlines
    theorem_str = theorem_str.replace(" ", "")
    theorem_str = theorem_str.replace("\n", "")
    # if line is given in the form "(variable,?)+:theorem", only take theorem
    # maybe check that all variables in theorem were declared? meh.
    if ':' in theorem_str:
        theorem_str = theorem_str.split(":")[1]
    # check theorem parenthesis count
    if theorem_str.count("(") > theorem_str.count(")"):
        raise Exception("Unexpected end of line, expression: {}".format(theorem_str))
    if theorem_str.count("(") < theorem_str.count(")"):
        raise Exception("Parse error, unexpected ')', expression: {}".format(theorem_str))
    # look for a proposition definition at the beginning
    search_regex = r"^(Variable|Not|And|Or|Implies|Imply|Equivalent|Equiv)"
    search_result = search(search_regex, theorem_str)
    # if not found, try to parse T, F or a variable name (alphanumeric)
    if search_result == None:
        if theorem_str == "T":
            return T
        if theorem_str == "F":
            return F
        if theorem_str.isalnum():
            return Variable(theorem_str)
        raise Exception("Not an alphanumeric variable name: {}".format(theorem_str))
    # if found, instanciate correct proposition parsing str args to propositions
    else:
        # proposition class name querried
        prop_class_name = search_result.group(0)
        # link names to class objects
        class_choices = {
            "Variable": Variable,
            "Not": Not,
            "And": And,
            "Or": Or,
            "Implies": Implies,
            "Imply": Implies,
            "Equivalent": Equivalent,
            "Equiv": Equivalent
        }
        # pick querried class object
        prop_class = class_choices[prop_class_name]
        # get str between first '(' and last ')'
        prop_args_str = theorem_str[len(prop_class_name)+1:-1]
        # get current proposition args' str
        ## this is a custom slicing, to slice only at commas at root level
        prop_args_str_stops = []
        level = 0
        previous = 0
        for i, c in enumerate(prop_args_str):
            if c == '(':
                level += 1
            elif c == ')':
                level -= 1
            elif c == ',' and level == 0:
                prop_args_str_stops.append((previous, i))
                previous = i + 1
        prop_args_str_stops.append((previous, len(prop_args_str)))
        prop_args_str_list = [prop_args_str[i:j] for (i, j) in prop_args_str_stops]
        ## end of custom slicing
        # number of required args for querried class
        prop_class_n_args = len(signature(prop_class.__init__).parameters) - 1
        # check querried args number = expected args number in querried class definition
        if prop_class_n_args != len(prop_args_str_list):
            raise Exception("Parsing error, wrong number {} of arguments"+
                            " for {}, expression: {}"
                            .format(len(prop_args_str_list),
                                    prop_class_name,
                                    theorem_str))
        # build args recursively
        args = (decode_proposition_str(prop_arg_str)
                for prop_arg_str in prop_args_str_list)
        # return proposition
        return prop_class(*args)

def test_theorem_file(path):
    with open(path, 'r') as f:
        # iterate lines
        for i, l in enumerate(f):
            try:
                l = l.replace("\n", "")
                print("{}) Decoding : ".format(i), l)
                theorem = decode_proposition_str(l)
                print("Theorem : ", theorem)
                check_theorem(theorem)
            except Exception as e:
                print(e)
            print()

def from_cnf_table(cnf_table):
    # little helper for merging (merge Ors then Ands the same way...)
    def merge_to_prop_helper(t, c):
        prop = t.pop()
        for k in t:
            prop = c(prop, k)
        return prop
    # merges
    ors_list = set([merge_to_prop_helper(t, Or) for t in cnf_table if len(t) > 0])
    prop = merge_to_prop_helper(ors_list, And) if len(ors_list) > 0 else T
    # return result
    return prop

# Main script for demo purpose
if __name__ == "__main__":
    # Modify any key name to check evaluation error
    print("=== Test some formulas with ===")
    test = {
        "A": True,
        "B": False
    }
    print(test, end="\n\n")
    print("Formula", "Expected", "Evaluated")

    A = Variable("A")
    print(A, True, A.evaluate(test)) # ok

    notA = Not(A)
    print(notA, False, notA.evaluate(test)) # ok

    B = Variable("B")
    AandB = And(A, B)
    print(AandB, False, AandB.evaluate(test)) # ok

    AorB = Or(A, B)
    print(AorB, True, AorB.evaluate(test)) # ok

    not_AandB = Not(AandB)
    print(not_AandB, True, not_A2andB.evaluate(test)) # ok

    prop1 = Not(And(A, Not(B)))
    print(prop1, False, prop1.evaluate(test)) # ok

    prop2 = And(Not(A), Or(A, Not(B)))
    print(prop2, False, prop2.evaluate(test)) # ok

    print("Done", end="\n\n")

    print("=== Test truth table ===")
    print_truth_table(And) # ok
    print("Done", end="\n\n")

    print("=== Test check_theorem ===")
    prop3 = Equivalent(Not(And(A, B)), Or(Not(A), Not(B)))
    prop3.check_theorem()
    print()
    prop4 = Implies(A, Not(A))
    prop4.check_theorem()
    print("Done", end="\n\n")

    print("=== Test test_theorem_file ===")
    test_theorem_file("theorems.txt")
    print("Done", end="\n\n")

    print("=== Test simplify ===")
    prop5 = And(Not(Not(A)), A)
    prop5_s = prop5.simplify()
    print(prop5, "~>", prop5_s)
    prop6 = And(A, T)
    prop6_s = prop6.simplify()
    print(prop6, "~>", prop6_s)
    prop7 = Equivalent(A, F())
    prop7_s = prop7.simplify()
    print(prop7, "~>", prop7_s)
    print("Done", end="\n\n")

    print("=== Test to_cnf ===")
    C = Variable("C")
    prop8 = Or(And(A, B), C)
    prop8_cnf = prop8.to_cnf()
    print(prop8, "~>", prop8_cnf)
    print("Variables, proposition value, CNF value")
    for variables in variable_input_possibilities(prop8.list_var_names()):
        print([val for (k, val) in variables.items()], prop8.evaluate(variables), prop8_cnf.evaluate(variables))
