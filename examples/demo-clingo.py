#!/usr/bin/env python

from clorm import monkey

monkey.patch()  # must call this before importing clingo

from clingo import Control

from clorm import ConstantField, FactBase, Predicate

ASP_PROGRAM = "etc/clingo/set_covering.lp"

# --------------------------------------------------------------------------
# Define a data model - we only care about defining the input and output
# predicates.
# --------------------------------------------------------------------------

# element(1..3).
# set(s1,1).
# select(S), set(S, E)


class Element(Predicate):
    name = ConstantField


class Set(Predicate):
    name = ConstantField
    element = ConstantField


class Select(Predicate):
    name = ConstantField



# --------------------------------------------------------------------------
#
# --------------------------------------------------------------------------


def main():
    # Create a Control object that will unify models against the appropriate
    # predicates. Then load the asp file that encodes the problem domain.
    ctrl = Control(unifier=[Element, Set, Select])
    ctrl.load(ASP_PROGRAM)

    # Dynamically generate the instance data
    elements = [Element(str(i)) for i in range(1, 3 + 1)]
    sets = [ Set('s1', str(c)) for c in [1] ] +\
      [ Set('s2', str(c)) for c in [1, 2] ] +\
      [ Set('s3', str(c)) for c in [2, 3] ]
    instance = FactBase(elements + sets)

    # Add the instance data and ground the ASP program
    ctrl.add_facts(instance)
    ctrl.ground([("base", [])])

    # Generate a solution - use a call back that saves the solution
    solution = None

    def on_model(model):
        nonlocal solution
        solution = model.facts(atoms=True)

    ctrl.solve(on_model=on_model)
    if not solution:
        raise ValueError("No solution found")

    # Do something with the solution - create a query so we can print out the
    for c in solution.query(Select).all():
        print(c.name)

# main
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    main()