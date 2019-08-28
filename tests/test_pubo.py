#   Copyright 2019 Joseph T. Iosue
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
Contains tests for the PUBO class.
"""

from qubovert import PUBO
from qubovert.utils import (
    solve_qubo_bruteforce, solve_ising_bruteforce,
    solve_pubo_bruteforce, solve_hising_bruteforce
)
from numpy import allclose


# Testing PUBO on a QUBO

qubo_problem = PUBO({
    ('a',): -1, ('b',): 2, ('a', 'b'): -3, ('b', 'c'): -4, (): -2
})
qubo_solution = {'c': 1, 'b': 1, 'a': 1}
qubo_obj = -8


def _qubo_problem_is_valid(e, solution):

    sol = qubo_problem.convert_solution(solution)
    return all((
        qubo_problem.is_solution_valid(sol),
        sol == qubo_solution,
        allclose(e, qubo_obj)
    ))


def test_pubo_pubo_solve_qubo_problem():

    e, sol = solve_pubo_bruteforce(qubo_problem.to_pubo())
    assert _qubo_problem_is_valid(e, sol)


def test_pubo_hising_solve_qubo_problem():

    e, sol = solve_hising_bruteforce(qubo_problem.to_hising())
    assert _qubo_problem_is_valid(e, sol)


def test_pubo_qubo_solve_qubo_problem():

    e, sol = solve_qubo_bruteforce(qubo_problem.to_qubo())
    assert _qubo_problem_is_valid(e, sol)


def test_pubo_ising_solve_qubo_problem():

    e, sol = solve_ising_bruteforce(qubo_problem.to_ising())
    assert _qubo_problem_is_valid(e, sol)


def test_pubo_bruteforce_solve_qubo_problem():

    assert qubo_problem.solve_bruteforce() == qubo_solution


# Testing PUBO on a PUBO

pubo_problem = PUBO({
    ('a',): -1, ('b',): 2, ('a', 'b'): -3, ('b', 'c'): -4, (): -2,
    (0, 1, 2): 1, (0,): -1, (1,): -2, (2,): 1
})
pubo_solution = {'c': 1, 'b': 1, 'a': 1, 0: 1, 1: 1, 2: 0}
pubo_obj = -11


def _pubo_problem_is_valid(e, solution):

    sol = pubo_problem.convert_solution(solution)
    return all((
        pubo_problem.is_solution_valid(sol),
        sol == pubo_solution,
        allclose(e, pubo_obj)
    ))


def test_pubo_pubo_solve_pubo_problem():

    e, sol = solve_pubo_bruteforce(pubo_problem.to_pubo())
    assert _pubo_problem_is_valid(e, sol)


def test_pubo_hising_solve_pubo_problem():

    e, sol = solve_hising_bruteforce(pubo_problem.to_hising())
    assert _pubo_problem_is_valid(e, sol)


def test_pubo_qubo_solve_pubo_problem():

    e, sol = solve_qubo_bruteforce(pubo_problem.to_qubo())
    assert _pubo_problem_is_valid(e, sol)


def test_pubo_ising_solve_pubo_problem():

    e, sol = solve_ising_bruteforce(pubo_problem.to_ising())
    assert _pubo_problem_is_valid(e, sol)


def test_pubo_bruteforce_solve_pubo_problem():

    assert pubo_problem.solve_bruteforce() == pubo_solution


# testing methods

def test_pubo_default_valid():

    d = PUBO()
    assert d[(0, 0)] == 0
    d[(0, 0)] += 1
    assert d == {(0,): 1}


def test_pubo_remove_value_when_zero():

    d = PUBO()
    d[(0, 0, 1, 2)] += 1
    d[(0, 1, 2)] -= 1
    assert d == {}


def test_pubo_reinitialize_dictionary():

    d = PUBO({(0, 0): 1, ('1', 0): 2, (2, 0): 0, (0, '1'): 1})
    assert d in ({(0,): 1, ('1', 0): 3}, {(0,): 1, (0, '1'): 3})


def test_pubo_update():

    d = PUBO({('0',): 1, ('0', 1): 2})
    d.update({('0', '0'): 0, (1, '0'): 1, (1, 1): -1})
    assert d in ({(1, '0'): 1, (1,): -1}, {('0', 1): 1, (1,): -1})

    d = PUBO({(0, 0): 1, (0, 1): 2})
    d.update(PUBO({(1, 0): 1, (1, 1): -1}))
    d -= 1
    assert d == PUBO({(0,): 1, (0, 1): 1, (1,): -1, (): -1})

    assert d.offset == -1


def test_pubo_num_binary_variables():

    d = PUBO({(0, 0): 1, (0, 1, 2, 3, 5): 2})
    assert d.num_binary_variables == 5
    assert d.max_index == 4


def test_pubo_addition():

    temp = PUBO({('0', '0'): 1, ('0', 1): 2})
    temp1 = {('0',): -1, (1, '0'): 3}
    temp2 = {(1, '0'): 5}, {('0', 1): 5}
    temp3 = {('0',): 2, (1, '0'): -1}, {('0',): 2, ('0', 1): -1}

    # constant
    d = temp.copy()
    d += 5
    assert d in ({('0',): 1, (1, '0'): 2, (): 5},
                 {('0',): 1, ('0', 1): 2, (): 5})

    # __add__
    d = temp.copy()
    g = d + temp1
    assert g in temp2

    # __iadd__
    d = temp.copy()
    d += temp1
    assert d in temp2

    # __radd__
    d = temp.copy()
    g = temp1 + d
    assert g in temp2

    # __sub__
    d = temp.copy()
    g = d - temp1
    assert g in temp3

    # __isub__
    d = temp.copy()
    d -= temp1
    assert d in temp3

    # __rsub__
    d = temp.copy()
    g = temp1 - d
    assert g == PUBO(temp3[0])*-1


def test_pubo_multiplication():

    temp = PUBO({('0', '0'): 1, ('0', 1): 2})
    temp1 = {('0',): 3, (1, '0'): 6}, {('0',): 3, ('0', 1): 6}
    temp2 = {('0',): .5, (1, '0'): 1}, {('0',): .5, ('0', 1): 1}

    # constant
    d = temp.copy()
    d += 3
    d *= -2
    assert d in ({('0',): -2, (1, '0'): -4, (): -6},
                 {('0',): -2, ('0', 1): -4, (): -6})

    # __mul__
    d = temp.copy()
    g = d * 3
    assert g in temp1

    d = temp.copy()
    g = d * 0
    assert g == {}

    # __imul__
    d = temp.copy()
    d *= 3
    assert d in temp1

    d = temp.copy()
    d *= 0
    assert d == {}

    # __rmul__
    d = temp.copy()
    g = 3 * d
    assert g in temp1

    d = temp.copy()
    g = 0 * d
    assert g == {}

    # __truediv__
    d = temp.copy()
    g = d / 2
    assert g in temp2

    # __itruediv__
    d = temp.copy()
    d /= 2
    assert d in temp2

    # __floordiv__
    d = temp.copy()
    g = d // 2
    assert g in ({(1, '0'): 1}, {('0', 1): 1})

    # __ifloordiv__
    d = temp.copy()
    d //= 2
    assert d in ({(1, '0'): 1}, {('0', 1): 1})

    # __mul__ but with dict
    d = temp.copy()
    d *= {(1,): 2, ('0', '0'): -1}
    assert d in ({('0',): -1, (1, '0'): 4}, {('0',): -1, ('0', 1): 4})

    # __pow__
    d = temp.copy()
    d -= 2
    d **= 2
    assert d == {('0',): -3, (): 4}

    d = temp.copy()
    assert d ** 3 == d * d * d


def test_properties():

    temp = PUBO({('0', '0'): 1, ('0', 1): 2})
    temp.offset
    temp.mapping
    temp.reverse_mapping
