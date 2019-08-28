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

"""_pubo.py.

Contains the PUBO class. See ``help(qubovert.PUBO)``.

"""

from .utils import BO, PUBOMatrix, QUBOMatrix, solve_pubo_bruteforce


__all__ = 'PUBO',


def _constraint_xy_eq_z(x, y, z, lam=1):
    """_constraint_xy_eq_z.

    Find the penalty dictionary enforcing ``xy = z``.

    Parameters
    ----------
    x : hashable object.
        Label of the ``x`` variable.
    y : hashable object.
        Label of the ``y`` variable.
    z : hashable object.
        Label of the ``z`` variable.
    lam : float > 0 (optional, default to 1).
        The penalty factor, how much to penalize violations of ``xy = z``.

    Returns
    -------
    D : dict.
        QUBO representing the constraint ``xy = z`` weighted by ``lam``.

    References
    ----------
    https://arxiv.org/pdf/1307.8041.pdf equation 6.

    """
    return {(z,): 3 * lam, (x, y): lam, (x, z): -2 * lam, (y, z): -2 * lam}


class PUBO(BO, PUBOMatrix):
    """PUBO.

    Class to manage converting general PUBO problems to and from their
    PUBO, HIsing, QUBO, and Ising formluations. In general, this class
    deals with unconstrained optimization problems that have arbitrary degree.
    To convert this to a QUBO (see ``to_qubo``) or Ising (``to_ising``) we have
    to introduce ancilla variables. The ``convert_solution`` method deals with
    converting a solution to the problem with ancilla variables back to the
    solution to the original problem.

    This class deals with PUBOs that have binary labels that do not range from
    0 to n-1. Note that it is generally
    more efficient to initialize an empty PUBO object and then build the
    PUBO, rather than initialize a PUBO object with an already built dict.

    PUBO inherits some methods and attributes from the ``PUBOMatrix`` class.
    See ``help(qubovert.utils.PUBOMatrix)``.

    PUBO inherits some methods and attributes the ``BO`` class. See
    ``help(qubovert.utils.BO)``.

    Example usage
    -------------
    >>> pubo = PUBO()
    >>> pubo[('a',)] += 5
    >>> pubo[(0, 'a', 1)] -= 2
    >>> pubo -= 1.5
    >>> pubo
    {('a',): 5, ('a', 0, 1): -2, (): -1.5}

    >>> pubo = PUBO({('a',): 5, (0, 'a', 1): -2, (): -1.5})
    >>> pubo
    {('a',): 5, ('a', 0, 1): -2, (): -1.5}
    >>> P = pubo.to_pubo()
    >>> P
    {(0,): 5, (0, 1): -2, (): -1.5}
    >>> pubo.convert_solution({0: 1, 1: 0, 2: 1})
    {'a': 1, 0: 0, 1: 1}

    In the next example, notice that we introduce ancilla variables to
    represent that ```(0, 1)`` term. See the ``to_qubo`` method for more info.

    >>> pubo = PUBO({('a',): 5, (0, 'a', 1): -2, (): -1.5})
    >>> pubo.mapping
    {'a': 0, 0: 1, 1: 2}
    >>> Q = pubo.to_qubo(3)
    >>> Q
    {(0,): 5, (0, 3): -2, (): -1.5, (1, 2): 3, (3,): 3, (1, 3): 3, (2, 3): 3}
    >>> pubo.convert_solution({0: 1, 1: 0, 2: 1, 2: 0})
    {'a': 1, 0: 0, 1: 1}

    Notes
    -----
    Note that keys will end up sorted by their hash. Hashes will not be
    consistent across Python sessions (unless they are integers)! For example,
    both of the following can happen:

    >>> print(PUBO({('a', 0): 1, (0, 1): -1}))
    {('a', 0): 1, (0, 1): -1}

    or

    >>> print(PUBO({('a', 0): 1, (0, 1): -1}))
    {(0, 'a'): 1, (0, 1): -1}

    But the following will never happen:

    >>> print(PUBO({('a', 0): 1, (0, 1): -1}))
    {('a', 0): 1, (1, 0): -1}

    Ie integers will always be correctly sorted.

    """

    def __init__(self, *args, **kwargs):
        """__init__.

        This class deals with PUBOs that have binary labels that do not range
        from 0 to n-1. Note that it is generally more efficient
        to initialize an empty PUBO object and then build the PUBO, rather than
        initialize a PUBO object with an already built dict.

        Parameters
        ----------
        args and kwargs define a dictionary. The dictionary will be initialized
        to follow all the convensions of the class.

        Examples
        -------
        >>> pubo = PUBO()
        >>> pubo[('a',)] += 5
        >>> pubo[(0, 'a')] -= 2
        >>> pubo -= 1.5
        >>> pubo
        {('a',): 5, ('a', 0): -2, (): -1.5}

        >>> pubo = PUBO({('a',): 5, (0, 'a', 1): -2, (): -1.5})
        >>> pubo
        {('a',): 5, ('a', 0, 1): -2, (): -1.5}

        """
        # Call PUBOMatrix.__init__.  We include a method here just so we can
        # update the docstring.
        super().__init__(*args, **kwargs)

    def to_pubo(self):
        """to_pubo.

        Create and return upper triangular PUBO representing the problem.
        The labels will be integers from 0 to n-1.

        Return
        -------
        P : qubovert.utils.PUBOMatrix object.
            The upper triangular PUBO matrix, a PUBOMatrix object.
            For most practical purposes, you can use PUBOMatrix in the
            same way as an ordinary dictionary. For more information,
            see ``help(qubovert.utils.PUBOMatrix)``.

        """
        P = PUBOMatrix()

        for k, v in self.items():
            key = tuple(self._mapping[i] for i in k)
            P[key] += v

        return P

    @staticmethod
    def default_lam(v):
        """default_lam.

        This is the default function used in ``to_qubo``. It returns
        ``1 + abs(v)``. It weights the penalties used to enforce the constraint
        ``xy = z``. See the ``to_qubo`` method.

        Parameters
        ----------
        v : float.

        Return
        ------
        res : float.
            Penalty weight.

        """
        return 1 + abs(v)

    def to_qubo(self, lam=None):
        """to_qubo.

        Create and return upper triangular QUBO representing the problem.
        The labels will be integers from 0 to n-1. We introduce ancilla
        variables in order to reduce the degree of the PUBO to a QUBO. The
        solution to the PUBO can be read from the solution to the QUBO by
        using the ``convert_solution`` method.

        Parameters
        ----------
        lam : function (optional, defaults to None).
            If ``lam`` is None, the function ``PUBO.default_lam`` will be used.
            ``lam`` is the penalty factor to introduce in order to enforce the
            ancilla constraints. When we reduce the degree of the PUBO to a
            QUBO, we add penalties to the QUBO in order to enforce ancilla
            variable constraints. These constraints will be multiplied by
            ``lam(v)``, where ``v`` is the value associated with the term that
            it is reducing. For example, a term ``(0, 1, 2): 3`` in the PUBO
            may be reduced to a term ``(0, 3): 3`` for the QUBO, and then the
            fact that ``3`` should be the product of ``1`` and ``2`` will be
            enforced with a penalty weight ``lam(3)``.

        Return
        -------
        Q : qubovert.utils.QUBOMatrix object.
            The upper triangular QUBO matrix, a QUBOMatrix object.
            For most practical purposes, you can use QUBOMatrix in the
            same way as an ordinary dictionary. For more information,
            see ``help(qubovert.utils.QUBOMatrix)``.

        """
        if lam is None:
            lam = PUBO.default_lam

        Q = QUBOMatrix()

        # next available label
        ancilla = self.num_binary_variables
        reductions = {}

        # we could use self.pubo().items() so we don't have to explicitly make
        # the key below, but this wastes a lot of time.
        for kp, v in self.items():
            key = tuple(sorted(self._mapping[i] for i in kp))
            if key in reductions:
                Q[reductions[key]] += v
            else:
                # find a reduction if len(key) > 2
                k = key
                while len(k) > 2:

                    # find a variable pair in k that has already been reduced.
                    found = False
                    for i, x in enumerate(k[:-1]):
                        for y in k[i+1:]:
                            if (x, y) in reductions:
                                found = True
                                break
                        if found:
                            break

                    if found:
                        # z is the ancilla variable for this reduction
                        z = reductions[(x, y)]
                    else:
                        # found is False so we haven't already reduced the
                        # variable pair (x, y), so just take the first two and
                        # reduce them.
                        # TODO: come up with a better way to choose x, y here.
                        x, y, z = k[0], k[1], ancilla
                        reductions[(x, y)] = z
                        ancilla += 1

                    # note we add the constraint even if we've already added
                    # it before (if found is True). This is because if we use
                    # the reduction multiple times, we need to enforce it
                    # multiple times.
                    Q += _constraint_xy_eq_z(x, y, z, lam(v))
                    k = tuple(sorted(
                            tuple(i for i in k if i not in (x, y)) + (z,)
                        ))
                Q[k] += v

        return Q

    def convert_solution(self, solution):
        """convert_solution.

        Convert the solution to the integer labeled PUBO to the solution to
        the originally labeled PUBO.

        Parameters
        ----------
        solution : iterable or dict.
            The PUBO, HIsing, QUBO, or Ising solution output. The PUBO solution
            output is either a list or tuple where indices specify the label of
            the variable and the element specifies whether it's 0 or 1 for PUBO
            (or -1 or 1 for Ising), or it can be a dictionary that maps the
            label of the variable to is value. The QUBO/Ising solution output
            includes the assignment for the ancilla variables used to reduce
            the degree of the PUBO.

        Return
        -------
        res : dict.
            Maps binary variable labels to their PUBO solutions values {0, 1}.

        Example
        -------
        >>> pubo = PUBO({('a',): 5, (0, 'a', 1): -2, (): -1.5})
        >>> pubo
        {('a',): 5, ('a', 0, 1): -2, (): -1.5}
        >>> P = pubo.to_pubo()
        >>> P
        {(0,): 5, (0, 1): -2, (): -1.5}
        >>> pubo.convert_solution({0: 1, 1: 0, 2: 1})
        {'a': 1, 0: 0, 1: 1}

        In the next example, notice that we introduce ancilla variables to
        represent that ```(0, 1)`` term. See the ``to_qubo`` method for more
        info.

        >>> pubo = PUBO({('a',): 5, (0, 'a', 1): -2, (): -1.5})
        >>> pubo.mapping
        {'a': 0, 0: 1, 1: 2}
        >>> Q = pubo.to_qubo(3)
        >>> Q
        {(0,): 5, (0, 3):-2, ():-1.5, (1, 2): 3, (3,): 3, (1, 3): 3, (2, 3): 3}
        >>> pubo.convert_solution({0: 1, 1: 0, 2: 1, 2: 0})
        {'a': 1, 0: 0, 1: 1}

        Notes
        -----
        We take ignore the ancilla variable assignments when we convert the
        solution. For example if the conversion from PUBO to QUBO introduced
        an ancilla varable ``z = xy`` where ``x`` and ``y`` are variables of
        the PUBO, then ``solution`` must have values for ``x``, ``y``, and
        ``z``. If the QUBO solver found that ``x = 1``, ``y = 0``, and
        ``z = 1``, then the constraint that ``z = xy`` is not satisfied (one
        possible cause for this is if the ``lam`` argument in ``to_qubo`` is
        too small). ``convert_solution`` will return that ``x = 1`` and
        ``y = 0`` and ignore the value of ``z``.

        """
        # this works for converting a solution to the pubo, qubo, hising, or
        # ising formulations, since in the to_qubo function all ancilla
        # variables are labeled with integers >= self.num_binary_variables.
        return {
            self._reverse_mapping[i]: 1 if solution[i] == 1 else 0
            for i in range(self.num_binary_variables)
        }

    @staticmethod
    def _check_key_valid(key):
        """_check_key_valid.

        Internal method to check if an input key to the dictionary is valid.
        Checks to see if ``key`` is a tuple.

        Parameters
        ---------
        key : anything, but must be a tuple to be valid.

        Returns
        -------
        None.

        Raises
        ------
        KeyError if the key is invalid.

        """
        # override PUBOMatrix._check_key_valid to allow for noninteger keys.
        if not isinstance(key, tuple):
            raise KeyError(
                "Key formatted incorrectly, must be tuple")

    def solve_bruteforce(self, *args, **kwargs):
        """solve_bruteforce.

        Solve the problem bruteforce. THIS SHOULD NOT BE USED FOR LARGE
        PROBLEMS! It converts the problem to PUBO, solves it with
        ``qubovert.utils.solve_pubo_bruteforce``, and then calls and returns
        ``convert_solution``.

        Parameters
        ----------
        *args and **kwargs : arguments and keyword arguments.
            Contains args and kwargs for the ``to_pubo`` method. Also contains
            a ``all_solutions`` boolean flag, which indicates whether or not
            to return all the solutions, or just the best one found.
            ``all_solutions`` defaults to False.

        Return
        ------
        res : the output or outputs of the ``convert_solution`` method.
            If ``all_solutions`` is False, then ``res`` is just the output
            of the ``convert_solution`` method.
            If ``all_solutions`` is True, then ``res`` is a list of outputs
            of the ``convert_solution`` method, e.g. a converted solution
            for each solution that the bruteforce solver returns.

        """
        kwargs = kwargs.copy()
        all_solutions = kwargs.pop("all_solutions", False)
        pubo = self.to_pubo(*args, **kwargs)
        _, sol = solve_pubo_bruteforce(pubo, all_solutions=all_solutions)
        if all_solutions:
            return [self.convert_solution(x) for x in sol]
        return self.convert_solution(sol)
