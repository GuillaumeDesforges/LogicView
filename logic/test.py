#!/usr/bin/python3

"""

Unit testing for propositions module

"""

import unittest
from propositions import *

class TestProposition(unittest.TestCase):
    def test_T(self):
        # evaluation
        self.assertEqual(T.evaluate({}), True)
        self.assertEqual(T.evaluate({'A': True}), True)
        # str
        self.assertEqual(str(T), "T")
        # simplify
        self.assertEqual(T.simplify(), T)
        # to CNF
        self.assertEqual(T.to_cnf(), T)

    def test_F(self):
        # evaluation
        self.assertEqual(F.evaluate({}), False)
        self.assertEqual(F.evaluate({'A': True}), False)
        # str
        self.assertEqual(str(F), "F")
        # simplify
        self.assertEqual(F.simplify(), F)
        # to CNF
        self.assertEqual(F.to_cnf(), F)

    def test_variable(self):
        # evaluation
        A = Variable('A')
        test1 = {'A': True}
        test2 = {'A': False}
        self.assertEqual(A.evaluate(test1), True)
        self.assertEqual(A.evaluate(test2), False)
        # str
        self.assertEqual(str(A), "A")
        with self.assertRaises(Exception):
            A.evaluate({'B': True})
        # simplify
        self.assertEqual(A.simplify(), A)
        # to CNF
        self.assertEqual(A.to_cnf(), A)

    def test_not(self):
        A = Variable('A')
        # evaluation
        self.assertEqual(Not(T).evaluate({}), False)
        self.assertEqual(Not(F).evaluate({}), True)
        # str
        self.assertEqual(str(Not(T)), "-"+str(T))
        self.assertEqual(str(Not(Not(T))), "--"+str(T))
        # simplify
        self.assertEqual(Not(T).simplify(), F)
        self.assertEqual(Not(F).simplify(), T)
        self.assertEqual(Not(Not(A)).simplify(), A)
        self.assertEqual(Not(A).to_cnf(), Not(A))
        # to CNF
        self.assertEqual(Not(Not(A)).to_cnf(), A)


    def test_and(self):
        # evaluation
        self.assertEqual(And(T, T).evaluate({}), True)
        self.assertEqual(And(F, T).evaluate({}), False)
        self.assertEqual(And(T, F).evaluate({}), False)
        self.assertEqual(And(F, F).evaluate({}), False)
        # str
        self.assertEqual(str(And(T, F)), str(F)+" /\\ "+str(T))
        self.assertEqual(str(And(Not(T), F)), "-"+str(T)+" /\\ "+str(F))
        # simplify
        A = Variable("A")
        self.assertEqual(And(T, A).simplify(), A)
        self.assertEqual(And(A, T).simplify(), A)
        self.assertEqual(And(F, A).simplify(), F)
        self.assertEqual(And(A, F).simplify(), F)
        # to CNF
        B = Variable("B")
        self.assertEqual(And(A, B).to_cnf(), And(A, B))

    def test_or(self):
        # evaluation
        self.assertEqual(Or(T, T).evaluate({}), True)
        self.assertEqual(Or(F, T).evaluate({}), True)
        self.assertEqual(Or(T, F).evaluate({}), True)
        self.assertEqual(Or(F, F).evaluate({}), False)
        # str
        self.assertEqual(str(Or(T, F)), str(F)+" \\/ "+str(T))
        self.assertEqual(str(Or(Not(T), F)), "-"+str(T)+" \\/ "+str(F))
        # simplify
        A = Variable("A")
        self.assertEqual(Or(T, A).simplify(), T)
        self.assertEqual(Or(A, T).simplify(), T)
        self.assertEqual(Or(F, A).simplify(), A)
        self.assertEqual(Or(A, F).simplify(), A)
        # to CNF
        B = Variable("B")
        self.assertEqual(Or(A, B).to_cnf(), Or(A, B))

    def test_implies(self):
        # evaluation
        self.assertEqual(Implies(T, T).evaluate({}), True)
        self.assertEqual(Implies(F, T).evaluate({}), True)
        self.assertEqual(Implies(T, F).evaluate({}), False)
        self.assertEqual(Implies(F, F).evaluate({}), True)
        # str
        self.assertEqual(str(Implies(T, F)), str(T)+" => "+str(F))
        self.assertEqual(str(Implies(Not(T), F)), "-"+str(T)+" => "+str(F))
        # simplify
        A = Variable("A")
        self.assertEqual(Implies(T, A).simplify(), A)
        self.assertEqual(Implies(A, T).simplify(), T)
        self.assertEqual(Implies(F, A).simplify(), T)
        self.assertEqual(Implies(A, F).simplify(), Not(A))
        # to CNF
        B = Variable("B")
        self.assertEqual(Implies(A, B).to_cnf(), Or(Not(A), B))

    def test_equivalent(self):
        # evaluation
        self.assertEqual(Equivalent(T, T).evaluate({}), True)
        self.assertEqual(Equivalent(F, T).evaluate({}), False)
        self.assertEqual(Equivalent(T, F).evaluate({}), False)
        self.assertEqual(Equivalent(F, F).evaluate({}), True)
        self.assertEqual(str(Equivalent(T, F)), str(F)+" <=> "+str(T))
        self.assertEqual(str(Equivalent(Not(T), F)), "-"+str(T)+" <=> "+str(F))
        # simplify
        A = Variable("A")
        self.assertEqual(Equivalent(T, A).simplify(), A)
        self.assertEqual(Equivalent(A, T).simplify(), A)
        self.assertEqual(Equivalent(F, A).simplify(), Not(A))
        self.assertEqual(Equivalent(A, F).simplify(), Not(A))
        # to CNF
        B = Variable("B")
        self.assertEqual(Equivalent(A, B).to_cnf(), Or(And(A, B), And(Not(A), Not(B))).to_cnf())

    def test_search_counter_example(self):
        self.assertEqual(Variable("A").search_counter_example(), {'A': False})
        self.assertEqual(Not(Variable("A")).search_counter_example(), {'A': True})

    def test_decode_proposition_str(self):
        self.assertEqual(decode_proposition_str("A").__class__, Variable)
        self.assertEqual(decode_proposition_str("A")._name, "A")
        self.assertEqual(decode_proposition_str("Not(A)").__class__, Not)
        self.assertEqual(decode_proposition_str("And(A,A)").__class__, And)
        self.assertEqual(decode_proposition_str("Or(A,A)").__class__, Or)
        self.assertEqual(decode_proposition_str("Implies(A,A)").__class__, Implies)
        self.assertEqual(decode_proposition_str("Imply(A,A)").__class__, Implies)
        self.assertEqual(decode_proposition_str("Equivalent(A,A)").__class__, Equivalent)
        self.assertEqual(decode_proposition_str("Equiv(A,A)").__class__, Equivalent)

if __name__ == "__main__":
    unittest.main()
