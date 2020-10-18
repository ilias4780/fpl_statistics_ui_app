#! /usr/bin/env python
# PuLP : Python LP Modeler


# Copyright (c) 2002-2005, Jean-Sebastien Roy (js@jeannot.org)
# Modifications Copyright (c) 2007- Stuart Anthony Mitchell (s.mitchell@auckland.ac.nz)
# $Id: pulp.py 1791 2008-04-23 22:54:34Z smit023 $

# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
PuLP is an LP modeler written in python. PuLP can generate MPS or LP files
and call GLPK[1], COIN CLP/CBC[2], CPLEX[3], and GUROBI[4] to solve linear
problems.

See the examples directory for examples.

The examples require at least a solver in your PATH or a shared library file.

Documentation is found on https://www.coin-or.org/PuLP/.
A comprehensive wiki can be found at https://www.coin-or.org/PuLP/

Use LpVariable() to create new variables. To create a variable 0 <= x <= 3
>>> x = LpVariable("x", 0, 3)

To create a variable 0 <= y <= 1
>>> y = LpVariable("y", 0, 1)

Use LpProblem() to create new problems. Create "myProblem"
>>> prob = LpProblem("myProblem", const.LpMinimize)

Combine variables to create expressions and constraints and add them to the
problem.
>>> prob += x + y <= 2

If you add an expression (not a constraint), it will
become the objective.
>>> prob += -4 * x + y

Choose a solver and solve the problem. ex:
>>> status = prob.solve(PULP_CBC_CMD(msg = 0))

Display the status of the solution
>>> const.LpStatus[status]
'Optimal'

You can get the value of the variables using value(). ex:
>>> value(x)
2.0

Exported Classes:
    - LpProblem -- Container class for a Linear programming problem
    - LpVariable -- Variables that are added to constraints in the LP
    - LpConstraint -- A constraint of the general form
      a1x1+a2x2 ...anxn (<=, =, >=) b
    - LpConstraintVar -- Used to construct a column of the model in column-wise
      modelling

Exported Functions:
    - value() -- Finds the value of a variable or expression
    - lpSum() -- given a list of the form [a1*x1, a2x2, ..., anxn] will construct
      a linear expression to be used as a constraint or variable
    - lpDot() --given two lists of the form [a1, a2, ..., an] and
      [ x1, x2, ..., xn] will construct a linear epression to be used
      as a constraint or variable

Comments, bug reports, patches and suggestions are welcome.
pulp-or-discuss@googlegroups.com

References:
[1] http://www.gnu.org/software/glpk/glpk.html
[2] http://www.coin-or.org/
[3] http://www.cplex.com/
[4] http://www.gurobi.com/
"""

import sys
import warnings

from .apis import LpSolverDefault, PULP_CBC_CMD
from .apis.core import clock
from .utilities import value
from . import constants as const

try:
    from collections.abc import Iterable
except ImportError:
    # python 2.7 compatible 
    from collections import Iterable

import logging
log = logging.getLogger(__name__)

try:  # allow Python 2/3 compatibility
    maketrans = str.maketrans
except AttributeError:
    from string import maketrans

_DICT_TYPE = dict

if sys.platform not in ['cli']:
    # iron python does not like an OrderedDict
    try:
        from odict import OrderedDict
        _DICT_TYPE = OrderedDict
    except ImportError:
        pass
    try:
        #python 2.7 or 3.1
        from collections import OrderedDict
        _DICT_TYPE = OrderedDict
    except ImportError:
        pass

try:
    import ujson as json
except ImportError:
    import json

import re

class LpElement(object):
    """Base class for LpVariable and LpConstraintVar
    """
    #to remove illegal characters from the names
    illegal_chars = "-+[] ->/"
    expression = re.compile("[{}]".format(re.escape(illegal_chars)))
    trans = maketrans(illegal_chars, "________")
    def setName(self, name):
        if name:
            if self.expression.match(name):
                warnings.warn("The name {} has illegal characters that will be replaced by _".format(name))
            self.__name = str(name).translate(self.trans)
        else:
            self.__name = None
    def getName(self):
        return self.__name
    name = property(fget = getName,fset = setName)

    def __init__(self, name):
        self.name = name
         # self.hash MUST be different for each variable
        # else dict() will call the comparison operators that are overloaded
        self.hash = id(self)
        self.modified = True

    def __hash__(self):
        return self.hash

    def __str__(self):
        return self.name
    def __repr__(self):
        return self.name

    def __neg__(self):
        return - LpAffineExpression(self)

    def __pos__(self):
        return self

    def __bool__(self):
        return 1

    def __add__(self, other):
        return LpAffineExpression(self) + other

    def __radd__(self, other):
        return LpAffineExpression(self) + other

    def __sub__(self, other):
        return LpAffineExpression(self) - other

    def __rsub__(self, other):
        return other - LpAffineExpression(self)

    def __mul__(self, other):
        return LpAffineExpression(self) * other

    def __rmul__(self, other):
        return LpAffineExpression(self) * other

    def __div__(self, other):
        return LpAffineExpression(self)/other

    def __rdiv__(self, other):
        raise TypeError("Expressions cannot be divided by a variable")

    def __le__(self, other):
        return LpAffineExpression(self) <= other

    def __ge__(self, other):
        return LpAffineExpression(self) >= other

    def __eq__(self, other):
        return LpAffineExpression(self) == other

    def __ne__(self, other):
        if isinstance(other, LpVariable):
            return self.name is not other.name
        elif isinstance(other, LpAffineExpression):
            if other.isAtomic():
                return self is not other.atom()
            else:
                return 1
        else:
            return 1


class LpVariable(LpElement):
    """
    This class models an LP Variable with the specified associated parameters

    :param name: The name of the variable used in the output .lp file
    :param lowBound: The lower bound on this variable's range.
        Default is negative infinity
    :param upBound: The upper bound on this variable's range.
        Default is positive infinity
    :param cat: The category this variable is in, Integer, Binary or
        Continuous(default)
    :param e: Used for column based modelling: relates to the variable's
        existence in the objective function and constraints
    """
    def __init__(self, name, lowBound = None, upBound = None,
                  cat = const.LpContinuous, e = None):
        LpElement.__init__(self,name)
        self._lowbound_original = self.lowBound = lowBound
        self._upbound_original = self.upBound = upBound
        self.cat = cat
        self.varValue = None
        self.dj = None
        if cat == const.LpBinary:
            self.lowBound = 0
            self.upBound = 1
            self.cat = const.LpInteger
        #code to add a variable to constraints for column based
        # modelling
        if e:
            self.add_expression(e)

    def to_dict(self):
        """
        Exports a variable into a dictionary with its relevant information

        :return: a dictionary with the variable information
        :rtype: dict
        """
        return dict(lowBound=self.lowBound, upBound=self.upBound, cat=self.cat,
                    varValue=self.varValue, dj=self.dj, name=self.name)

    @classmethod
    def from_dict(cls, dj=None, varValue=None, **kwargs):
        """
        Initializes a variable object from information that comes from a dictionary (kwargs)

        :param dj: shadow price of the variable
        :param float varValue: the value to set the variable
        :param kwargs: arguments to initialize the variable
        :return: a :py:class:`LpVariable`
        :rtype: :LpVariable
        """
        var = cls(**kwargs)
        var.dj = dj
        var.varValue = varValue
        return var

    def add_expression(self,e):
        self.expression = e
        self.addVariableToConstraints(e)

    def matrix(self, name, indexs, lowBound = None, upBound = None, cat = const.LpContinuous,
            indexStart = []):
        if not isinstance(indexs, tuple): indexs = (indexs,)
        if "%" not in name: name += "_%s" * len(indexs)

        index = indexs[0]
        indexs = indexs[1:]
        if len(indexs) == 0:
            return [LpVariable(name % tuple(indexStart + [i]),
                                            lowBound, upBound, cat)
                        for i in index]
        else:
            return [LpVariable.matrix(name, indexs, lowBound,
                                        upBound, cat, indexStart + [i])
                       for i in index]
    matrix = classmethod(matrix)

    def dicts(self, name, indexs, lowBound = None, upBound = None, cat = const.LpContinuous,
        indexStart = []):
        """
        This function creates a dictionary of :py:class:`LpVariable` with the specified associated parameters.

        :param name: The prefix to the name of each LP variable created
        :param indexs: A list of strings of the keys to the dictionary of LP
            variables, and the main part of the variable name itself
        :param lowBound: The lower bound on these variables' range. Default is
            negative infinity
        :param upBound: The upper bound on these variables' range. Default is
            positive infinity
        :param cat: The category these variables are in, Integer or
            Continuous(default)

        :return: A dictionary of :py:class:`LpVariable`
        """
        if not isinstance(indexs, tuple): indexs = (indexs,)
        if "%" not in name: name += "_%s" * len(indexs)

        index = indexs[0]
        indexs = indexs[1:]
        d = {}
        if len(indexs) == 0:
            for i in index:
                d[i] = LpVariable(name % tuple(indexStart + [str(i)]), lowBound, upBound, cat)
        else:
            for i in index:
                d[i] = LpVariable.dicts(name, indexs, lowBound, upBound, cat, indexStart + [i])
        return d
    dicts = classmethod(dicts)

    def dict(self, name, indexs, lowBound = None, upBound = None, cat = const.LpContinuous):
        if not isinstance(indexs, tuple): indexs = (indexs,)
        if "%" not in name: name += "_%s" * len(indexs)

        lists = indexs

        if len(indexs)>1:
            # Cartesian product
            res = []
            while len(lists):
                first = lists[-1]
                nres = []
                if res:
                    if first:
                        for f in first:
                            nres.extend([[f]+r for r in res])
                    else:
                        nres = res
                    res = nres
                else:
                    res = [[f] for f in first]
                lists = lists[:-1]
            index = [tuple(r) for r in res]
        elif len(indexs) == 1:
            index = indexs[0]
        else:
            return {}

        d = {}
        for i in index:
         d[i] = self(name % i, lowBound, upBound, cat)
        return d
    dict = classmethod(dict)

    def getLb(self):
        return self.lowBound

    def getUb(self):
        return self.upBound

    def bounds(self, low, up):
        self.lowBound = low
        self.upBound = up
        self.modified = True

    def positive(self):
        self.bounds(0, None)

    def value(self):
        return self.varValue

    def round(self, epsInt = 1e-5, eps = 1e-7):
        if self.varValue is not None:
            if self.upBound != None and self.varValue > self.upBound and self.varValue <= self.upBound + eps:
                self.varValue = self.upBound
            elif self.lowBound != None and self.varValue < self.lowBound and self.varValue >= self.lowBound - eps:
                self.varValue = self.lowBound
            if self.cat == const.LpInteger and abs(round(self.varValue) - self.varValue) <= epsInt:
                self.varValue = round(self.varValue)

    def roundedValue(self, eps = 1e-5):
        if self.cat == const.LpInteger and self.varValue != None \
            and abs(self.varValue - round(self.varValue)) <= eps:
            return round(self.varValue)
        else:
            return self.varValue

    def valueOrDefault(self):
        if self.varValue != None:
            return self.varValue
        elif self.lowBound != None:
            if self.upBound != None:
                if 0 >= self.lowBound and 0 <= self.upBound:
                    return 0
                else:
                    if self.lowBound >= 0:
                        return self.lowBound
                    else:
                        return self.upBound
            else:
                if 0 >= self.lowBound:
                    return 0
                else:
                    return self.lowBound
        elif self.upBound != None:
            if 0 <= self.upBound:
                return 0
            else:
                return self.upBound
        else:
            return 0

    def valid(self, eps):
        if self.varValue is None: return False
        if self.upBound is not None and self.varValue > self.upBound + eps:
            return False
        if self.lowBound is not None and self.varValue < self.lowBound - eps:
            return False
        if self.cat == const.LpInteger and abs(round(self.varValue) - self.varValue) > eps:
            return False
        return True

    def infeasibilityGap(self, mip = 1):
        if self.varValue == None: raise ValueError("variable value is None")
        if self.upBound != None and self.varValue > self.upBound:
            return self.varValue - self.upBound
        if self.lowBound != None and self.varValue < self.lowBound:
            return self.varValue - self.lowBound
        if mip and self.cat == const.LpInteger and round(self.varValue) - self.varValue != 0:
            return round(self.varValue) - self.varValue
        return 0

    def isBinary(self):
        return self.cat == const.LpInteger and self.lowBound == 0 and self.upBound == 1

    def isInteger(self):
        return self.cat == const.LpInteger

    def isFree(self):
        return self.lowBound is None and self.upBound is None

    def isConstant(self):
        return self.lowBound is not None and self.upBound == self.lowBound

    def isPositive(self):
        return self.lowBound == 0 and self.upBound is None

    def asCplexLpVariable(self):
        if self.isFree(): return self.name + " free"
        if self.isConstant(): return self.name + " = %.12g" % self.lowBound
        if self.lowBound == None:
            s= "-inf <= "
        # Note: XPRESS and CPLEX do not interpret integer variables without
        # explicit bounds
        elif (self.lowBound == 0 and self.cat == const.LpContinuous):
            s = ""
        else:
            s= "%.12g <= " % self.lowBound
        s += self.name
        if self.upBound is not None:
            s += " <= %.12g" % self.upBound
        return s

    def asCplexLpAffineExpression(self, name, constant = 1):
        return LpAffineExpression(self).asCplexLpAffineExpression(name, constant)

    def __ne__(self, other):
        if isinstance(other, LpElement):
            return self.name is not other.name
        elif isinstance(other, LpAffineExpression):
            if other.isAtomic():
                return self is not other.atom()
            else:
                return 1
        else:
            return 1

    def addVariableToConstraints(self,e):
        """adds a variable to the constraints indicated by
        the LpConstraintVars in e
        """
        for constraint, coeff in e.items():
            constraint.addVariable(self,coeff)

    def setInitialValue(self, val, check=True):
        """
        sets the initial value of the variable to `val`
        May be used for warmStart a solver, if supported by the solver

        :param float val: value to set to variable
        :param bool check: if True, we check if the value fits inside the variable bounds
        :return: True if the value was set
        :raises ValueError: if check=True and the value does not fit inside the bounds
        """
        lb = self.lowBound
        ub = self.upBound
        config = [('smaller', 'lowBound', lb, lambda: val < lb),
                  ('greater', 'upBound', ub, lambda: val > ub)]

        for rel, bound_name, bound_value, condition in config:
            if bound_value is not None and condition():
                if not check:
                    return False
                raise ValueError('In variable {}, initial value {} is {} than {} {}'.
                                 format(self.name, val, rel, bound_name, bound_value))
        self.varValue = val
        return True

    def fixValue(self):
        """
        changes lower bound and upper bound to the initial value if exists.
        :return: None
        """
        self._lowbound_unfix = self.lowBound
        self._upbound_unfix = self.upBound
        val = self.varValue
        if val is not None:
            self.bounds(val, val)

    def isFixed(self):
        """

        :return: True if upBound and lowBound are the same
        :rtype: bool
        """
        return self.isConstant()

    def unfixValue(self):
        self.bounds(self._lowbound_original, self._upbound_original)


class LpAffineExpression(_DICT_TYPE):
    """
    A linear combination of :class:`LpVariables<LpVariable>`.
    Can be initialised with the following:

    #.   e = None: an empty Expression
    #.   e = dict: gives an expression with the values being the coefficients of the keys (order of terms is undetermined)
    #.   e = list or generator of 2-tuples: equivalent to dict.items()
    #.   e = LpElement: an expression of length 1 with the coefficient 1
    #.   e = other: the constant is initialised as e

    Examples:

       >>> f=LpAffineExpression(LpElement('x'))
       >>> f
       1*x + 0
       >>> x_name = ['x_0', 'x_1', 'x_2']
       >>> x = [LpVariable(x_name[i], lowBound = 0, upBound = 10) for i in range(3) ]
       >>> c = LpAffineExpression([ (x[0],1), (x[1],-3), (x[2],4)])
       >>> c
       1*x_0 + -3*x_1 + 4*x_2 + 0
    """
    #to remove illegal characters from the names
    trans = maketrans("-+[] ","_____")
    def setName(self,name):
        if name:
            self.__name = str(name).translate(self.trans)
        else:
            self.__name = None

    def getName(self):
        return self.__name

    name = property(fget=getName, fset=setName)

    def __init__(self, e = None, constant = 0, name = None):
        self.name = name
        # TODO remove isinstance usage
        if e is None:
            e = {}
        if isinstance(e, LpAffineExpression):
            # Will not copy the name
            self.constant = e.constant
            super(LpAffineExpression, self).__init__(list(e.items()))
        elif isinstance(e, dict):
            self.constant = constant
            super(LpAffineExpression, self).__init__(list(e.items()))
        elif isinstance(e, Iterable):
            self.constant = constant
            super(LpAffineExpression, self).__init__(e)
        elif isinstance(e, LpElement):
            self.constant = 0
            super(LpAffineExpression, self).__init__( [(e, 1)])
        else:
            self.constant = e
            super(LpAffineExpression, self).__init__()

    # Proxy functions for variables

    def isAtomic(self):
        return len(self) == 1 and self.constant == 0 and list(self.values())[0] == 1

    def isNumericalConstant(self):
        return len(self) == 0

    def atom(self):
        return list(self.keys())[0]

    # Functions on expressions

    def __bool__(self):
        return (float(self.constant) != 0.0) or (len(self) > 0)

    def value(self):
        s = self.constant
        for v,x in self.items():
            if v.varValue is None:
                return None
            s += v.varValue * x
        return s

    def valueOrDefault(self):
        s = self.constant
        for v,x in self.items():
            s += v.valueOrDefault() * x
        return s

    def addterm(self, key, value):
            y = self.get(key, 0)
            if y:
                y += value
                self[key] = y
            else:
                self[key] = value

    def emptyCopy(self):
        return LpAffineExpression()

    def copy(self):
        """Make a copy of self except the name which is reset"""
        # Will not copy the name
        return LpAffineExpression(self)

    def __str__(self, constant = 1):
        s = ""
        for v in self.sorted_keys():
            val = self[v]
            if val<0:
                if s != "": s += " - "
                else: s += "-"
                val = -val
            elif s != "": s += " + "
            if val == 1: s += str(v)
            else: s += str(val) + "*" + str(v)
        if constant:
            if s == "":
                s = str(self.constant)
            else:
                if self.constant < 0: s += " - " + str(-self.constant)
                elif self.constant > 0: s += " + " + str(self.constant)
        elif s == "":
            s = "0"
        return s

    def sorted_keys(self):
        """
        returns the list of keys sorted by name
        """
        result = [(v.name, v) for v in self.keys()]
        result.sort()
        result = [v for _, v in result]
        return result

    def __repr__(self):
        l = [str(self[v]) + "*" + str(v)
                        for v in self.sorted_keys()]
        l.append(str(self.constant))
        s = " + ".join(l)
        return s

    @staticmethod
    def _count_characters(line):
        #counts the characters in a list of strings
        return sum(len(t) for t in line)

    def asCplexVariablesOnly(self, name):
        """
        helper for asCplexLpAffineExpression
        """
        result = []
        line = ["%s:" % name]
        notFirst = 0
        variables = self.sorted_keys()
        for v in variables:
            val = self[v]
            if val < 0:
                sign = " -"
                val = -val
            elif notFirst:
                sign = " +"
            else:
                sign = ""
            notFirst = 1
            if val == 1:
                term = "%s %s" %(sign, v.name)
            else:
                #adding zero to val to remove instances of negative zero
                term = "%s %.12g %s" % (sign, val + 0, v.name)

            if self._count_characters(line) + len(term) > const.LpCplexLPLineSize:
                result += ["".join(line)]
                line = [term]
            else:
                line += [term]
        return result, line

    def asCplexLpAffineExpression(self, name, constant = 1):
        """
        returns a string that represents the Affine Expression in lp format
        """
        #refactored to use a list for speed in iron python
        result, line = self.asCplexVariablesOnly(name)
        if not self:
            term = " %s" % self.constant
        else:
            term = ""
            if constant:
                if self.constant < 0:
                    term = " - %s" % (-self.constant)
                elif self.constant > 0:
                    term = " + %s" % self.constant
        if self._count_characters(line) + len(term) > const.LpCplexLPLineSize:
            result += ["".join(line)]
            line = [term]
        else:
            line += [term]
        result += ["".join(line)]
        result = "%s\n" % "\n".join(result)
        return result

    def addInPlace(self, other):
        if isinstance(other,int) and (other == 0): 
            return self
        if other is None: return self
        if isinstance(other,LpElement):
            self.addterm(other, 1)
        elif isinstance(other,LpAffineExpression):
            self.constant += other.constant
            for v,x in other.items():
                self.addterm(v, x)
        elif isinstance(other,dict):
            for e in other.values():
                self.addInPlace(e)
        elif (isinstance(other,list)
              or isinstance(other, Iterable)):
           for e in other:
                self.addInPlace(e)
        else:
            self.constant += other
        return self

    def subInPlace(self, other):
        if isinstance(other,int) and (other == 0): 
            return self
        if other is None: return self
        if isinstance(other,LpElement):
            self.addterm(other, -1)
        elif isinstance(other,LpAffineExpression):
            self.constant -= other.constant
            for v,x in other.items():
                self.addterm(v, -x)
        elif isinstance(other,dict):
            for e in other.values():
                self.subInPlace(e)
        elif (isinstance(other,list)
              or isinstance(other, Iterable)):
            for e in other:
                self.subInPlace(e)
        else:
            self.constant -= other
        return self

    def __neg__(self):
        e = self.emptyCopy()
        e.constant = - self.constant
        for v,x in self.items():
            e[v] = - x
        return e

    def __pos__(self):
        return self

    def __add__(self, other):
        return self.copy().addInPlace(other)

    def __radd__(self, other):
        return self.copy().addInPlace(other)

    def __iadd__(self, other):
        return self.addInPlace(other)

    def __sub__(self, other):
        return self.copy().subInPlace(other)

    def __rsub__(self, other):
        return (-self).addInPlace(other)

    def __isub__(self, other):
        return (self).subInPlace(other)

    def __mul__(self, other):
        e = self.emptyCopy()
        if isinstance(other, LpAffineExpression):
            e.constant = self.constant * other.constant
            if len(other):
                if len(self):
                    raise TypeError("Non-constant expressions cannot be multiplied")
                else:
                    c = self.constant
                    if c != 0:
                        for v,x in other.items():
                            e[v] = c * x
            else:
                c = other.constant
                if c != 0:
                    for v,x in self.items():
                        e[v] = c * x
        elif isinstance(other,LpVariable):
            return self * LpAffineExpression(other)
        else:
            if other != 0:
                e.constant = self.constant * other
                for v,x in self.items():
                    e[v] = other * x
        return e

    def __rmul__(self, other):
        return self * other

    def __div__(self, other):
        if isinstance(other,LpAffineExpression) or isinstance(other,LpVariable):
            if len(other):
                raise TypeError("Expressions cannot be divided by a non-constant expression")
            other = other.constant
        e = self.emptyCopy()
        e.constant = self.constant / other
        for v,x in self.items():
            e[v] = x / other
        return e

    def __truediv__(self, other):
        if isinstance(other,LpAffineExpression) or isinstance(other,LpVariable):
            if len(other):
                raise TypeError("Expressions cannot be divided by a non-constant expression")
            other = other.constant
        e = self.emptyCopy()
        e.constant = self.constant / other
        for v,x in self.items():
            e[v] = x / other
        return e

    def __rdiv__(self, other):
        e = self.emptyCopy()
        if len(self):
            raise TypeError("Expressions cannot be divided by a non-constant expression")
        c = self.constant
        if isinstance(other,LpAffineExpression):
            e.constant = other.constant / c
            for v,x in other.items():
                e[v] = x / c
        else:
            e.constant = other / c
        return e

    def __le__(self, other):
        return LpConstraint(self - other, const.LpConstraintLE)

    def __ge__(self, other):
        return LpConstraint(self - other, const.LpConstraintGE)

    def __eq__(self, other):
        return LpConstraint(self - other, const.LpConstraintEQ)

    def to_dict(self):
        """
        exports the :py:class:`LpAffineExpression` into a list of dictionaries with the coefficients
        it does not export the constant

        :return: list of dictionaries with the coefficients
        :rtype: list
        """
        return [dict(name=k.name, value=v) for k, v in self.items()]


class LpConstraint(LpAffineExpression):
    """An LP constraint"""
    def __init__(self, e = None, sense = const.LpConstraintEQ,
                  name = None, rhs = None):
        """
        :param e: an instance of :class:`LpAffineExpression`
        :param sense: one of :data:`~pulp.const.LpConstraintEQ`, :data:`~pulp.const.LpConstraintGE`, :data:`~pulp.const.LpConstraintLE` (0, 1, -1 respectively)
        :param name: identifying string
        :param rhs: numerical value of constraint target
        """
        LpAffineExpression.__init__(self, e, name = name)
        if rhs is not None:
            self.constant -= rhs
        self.sense = sense
        self.pi = None
        self.slack = None
        self.modified = True

    def getLb(self):
        if ( (self.sense == const.LpConstraintGE) or
             (self.sense == const.LpConstraintEQ) ):
            return -self.constant
        else:
            return None

    def getUb(self):
        if ( (self.sense == const.LpConstraintLE) or
             (self.sense == const.LpConstraintEQ) ):
            return -self.constant
        else:
            return None

    def __str__(self):
        s = LpAffineExpression.__str__(self, 0)
        if self.sense is not None:
            s += " " + const.LpConstraintSenses[self.sense] + " " + str(-self.constant)
        return s

    def asCplexLpConstraint(self, name):
        """
        Returns a constraint as a string
        """
        result, line = self.asCplexVariablesOnly(name)
        if not list(self.keys()):
            line += ["0"]
        c = -self.constant
        if c == 0:
            c = 0 # Supress sign
        term = " %s %.12g" % (const.LpConstraintSenses[self.sense], c)
        if self._count_characters(line)+len(term) > const.LpCplexLPLineSize:
            result += ["".join(line)]
            line = [term]
        else:
            line += [term]
        result += ["".join(line)]
        result = "%s\n" % "\n".join(result)
        return result

    def changeRHS(self, RHS):
        """
        alters the RHS of a constraint so that it can be modified in a resolve
        """
        self.constant = -RHS
        self.modified = True

    def __repr__(self):
        s = LpAffineExpression.__repr__(self)
        if self.sense is not None:
            s += " " + const.LpConstraintSenses[self.sense] + " 0"
        return s

    def copy(self):
        """Make a copy of self"""
        return LpConstraint(self, self.sense)

    def emptyCopy(self):
        return LpConstraint(sense = self.sense)

    def addInPlace(self, other):
        if isinstance(other,LpConstraint):
            if self.sense * other.sense >= 0:
                LpAffineExpression.addInPlace(self, other)
                self.sense |= other.sense
            else:
                LpAffineExpression.subInPlace(self, other)
                self.sense |= - other.sense
        elif isinstance(other,list):
            for e in other:
                self.addInPlace(e)
        else:
            LpAffineExpression.addInPlace(self, other)
            #raise TypeError, "Constraints and Expressions cannot be added"
        return self

    def subInPlace(self, other):
        if isinstance(other,LpConstraint):
            if self.sense * other.sense <= 0:
                LpAffineExpression.subInPlace(self, other)
                self.sense |= - other.sense
            else:
                LpAffineExpression.addInPlace(self, other)
                self.sense |= other.sense
        elif isinstance(other,list):
            for e in other:
                self.subInPlace(e)
        else:
            LpAffineExpression.subInPlace(self, other)
            #raise TypeError, "Constraints and Expressions cannot be added"
        return self

    def __neg__(self):
        c = LpAffineExpression.__neg__(self)
        c.sense = - c.sense
        return c

    def __add__(self, other):
        return self.copy().addInPlace(other)

    def __radd__(self, other):
        return self.copy().addInPlace(other)

    def __sub__(self, other):
        return self.copy().subInPlace(other)

    def __rsub__(self, other):
        return (-self).addInPlace(other)

    def __mul__(self, other):
        if isinstance(other,LpConstraint):
            c = LpAffineExpression.__mul__(self, other)
            if c.sense == 0:
                c.sense = other.sense
            elif other.sense != 0:
                c.sense *= other.sense
            return c
        else:
            return LpAffineExpression.__mul__(self, other)

    def __rmul__(self, other):
        return self * other

    def __div__(self, other):
        if isinstance(other,LpConstraint):
            c = LpAffineExpression.__div__(self, other)
            if c.sense == 0:
                c.sense = other.sense
            elif other.sense != 0:
                c.sense *= other.sense
            return c
        else:
            return LpAffineExpression.__mul__(self, other)

    def __rdiv__(self, other):
        if isinstance(other,LpConstraint):
            c = LpAffineExpression.__rdiv__(self, other)
            if c.sense == 0:
                c.sense = other.sense
            elif other.sense != 0:
                c.sense *= other.sense
            return c
        else:
            return LpAffineExpression.__mul__(self, other)

    def valid(self, eps = 0):
        val = self.value()
        if self.sense == const.LpConstraintEQ: return abs(val) <= eps
        else: return val * self.sense >= - eps

    def makeElasticSubProblem(self, *args, **kwargs):
        """
        Builds an elastic subproblem by adding variables to a hard constraint

        uses FixedElasticSubProblem
        """
        return FixedElasticSubProblem(self, *args, **kwargs)

    def to_dict(self):
        """
        exports constraint information into a dictionary

        :return: dictionary with all the constraint information
        """
        return dict(sense=self.sense,
                    pi=self.pi,
                    constant=self.constant,
                    name=self.name,
                    coefficients=LpAffineExpression.to_dict(self))

    @classmethod
    def from_dict(cls, _dict):
        """
        Initializes a constraint object from a dictionary with necessary information

        :param dict _dict: dictionary with data
        :return: a new :py:class:`LpConstraint`
        """
        const = cls(e=_dict['coefficients'], rhs=-_dict['constant'], name=_dict['name'], sense=_dict['sense'])
        const.pi = _dict['pi']
        return const


class LpFractionConstraint(LpConstraint):
    """
    Creates a constraint that enforces a fraction requirement a/b = c
    """
    def __init__(self, numerator, denominator = None, sense = const.LpConstraintEQ,
                 RHS = 1.0, name = None,
                 complement = None):
        """
        creates a fraction Constraint to model constraints of
        the nature
        numerator/denominator {==, >=, <=} RHS
        numerator/(numerator + complement) {==, >=, <=} RHS

        :param numerator: the top of the fraction
        :param denominator: as described above
        :param sense: the sense of the relation of the constraint
        :param RHS: the target fraction value
        :param complement: as described above
        """
        self.numerator = numerator
        if denominator is None and complement is not None:
            self.complement = complement
            self.denominator = numerator + complement
        elif denominator is not None and complement is None:
            self.denominator = denominator
            self.complement = denominator - numerator
        else:
            self.denominator = denominator
            self.complement = complement
        lhs = self.numerator - RHS * self.denominator
        LpConstraint.__init__(self, lhs,
              sense = sense, rhs = 0, name = name)
        self.RHS = RHS

    def findLHSValue(self):
        """
        Determines the value of the fraction in the constraint after solution
        """
        if abs(value(self.denominator))>= const.EPS:
            return value(self.numerator)/value(self.denominator)
        else:
            if abs(value(self.numerator))<= const.EPS:
                #zero divided by zero will return 1
                return 1.0
            else:
                raise ZeroDivisionError

    def makeElasticSubProblem(self, *args, **kwargs):
        """
        Builds an elastic subproblem by adding variables and splitting the
        hard constraint

        uses FractionElasticSubProblem
        """
        return FractionElasticSubProblem(self, *args, **kwargs)


class LpConstraintVar(LpElement):
    """A Constraint that can be treated as a variable when constructing
    a LpProblem by columns
    """
    def __init__(self, name = None ,sense = None,
                 rhs = None, e = None):
        LpElement.__init__(self,name)
        self.constraint = LpConstraint(name = self.name, sense = sense,
                                       rhs = rhs , e = e)

    def addVariable(self, var, coeff):
        """
        Adds a variable to the constraint with the
        activity coeff
        """
        self.constraint.addterm(var, coeff)

    def value(self):
        return self.constraint.value()


class LpProblem(object):
    """An LP Problem"""
    def __init__(self, name = "NoName", sense = const.LpMinimize):
        """
        Creates an LP Problem

        This function creates a new LP Problem  with the specified associated parameters

        :param name: name of the problem used in the output .lp file
        :param sense: of the LP problem objective.  \
                Either :data:`~pulp.const.LpMinimize` (default) \
                or :data:`~pulp.const.LpMaximize`.
        :return: An LP Problem
        """
        if ' ' in name:
            warnings.warn("Spaces are not permitted in the name. Converted to '_'")
            name = name.replace(" ", "_")
        self.objective = None
        self.constraints = _DICT_TYPE()
        self.name = name
        self.sense = sense
        self.sos1 = {}
        self.sos2 = {}
        self.status = const.LpStatusNotSolved
        self.sol_status = const.LpSolutionNoSolutionFound
        self.noOverlap = 1
        self.solver = None
        self.modifiedVariables = []
        self.modifiedConstraints = []
        self.resolveOK = False
        self._variables = []
        self._variable_ids = {}  #old school using dict.keys() for a set
        self.dummyVar = None

        # locals
        self.lastUnused = 0

    def __repr__(self):
        s = self.name+":\n"
        if self.sense == 1:
            s += "MINIMIZE\n"
        else:
            s += "MAXIMIZE\n"
        s += repr(self.objective) +"\n"

        if self.constraints:
            s += "SUBJECT TO\n"
            for n, c in self.constraints.items():
                s += c.asCplexLpConstraint(n) +"\n"
        s += "VARIABLES\n"
        for v in self.variables():
            s += v.asCplexLpVariable() + " " + const.LpCategories[v.cat] + "\n"
        return s

    def __getstate__(self):
        # Remove transient data prior to pickling.
        state = self.__dict__.copy()
        del state['_variable_ids']
        return state

    def __setstate__(self, state):
        # Update transient data prior to unpickling.
        self.__dict__.update(state)
        self._variable_ids = {}
        for v in self._variables:
            self._variable_ids[v.hash] = v

    def copy(self):
        """Make a copy of self. Expressions are copied by reference"""
        lpcopy = LpProblem(name = self.name, sense = self.sense)
        lpcopy.objective = self.objective
        lpcopy.constraints = self.constraints.copy()
        lpcopy.sos1 = self.sos1.copy()
        lpcopy.sos2 = self.sos2.copy()
        return lpcopy

    def deepcopy(self):
        """Make a copy of self. Expressions are copied by value"""
        lpcopy = LpProblem(name = self.name, sense = self.sense)
        if self.objective is not None:
            lpcopy.objective = self.objective.copy()
        lpcopy.constraints = {}
        for k,v in self.constraints.items():
            lpcopy.constraints[k] = v.copy()
        lpcopy.sos1 = self.sos1.copy()
        lpcopy.sos2 = self.sos2.copy()
        return lpcopy

    def to_dict(self):
        """
        creates a dictionary from the model with as much data as possible.
        It replaces variables by variable names.
        So it requires to have unique names for variables.

        :return: dictionary with model data
        :rtype: dict
        """
        try:
            self.checkDuplicateVars()
        except const.PulpError:
            raise const.PulpError("Duplicated names found in variables:\nto export the model, variable names need to be unique")
        variables = self.variables()
        return \
            dict(
                objective=dict(name=self.objective.name, coefficients=self.objective.to_dict()),
                constraints=[v.to_dict() for v in self.constraints.values()],
                variables=[v.to_dict() for v in variables],
                parameters=dict(name=self.name,
                                sense=self.sense,
                                status=self.status,
                                sol_status=self.sol_status),
                sos1=list(self.sos1.values()),
                sos2=list(self.sos2.values())
            )

    @classmethod
    def from_dict(cls, _dict):
        """
        Takes a dictionary with all necessary information to build a model.
        And returns a dictionary of variables and a problem object

        :param _dict: dictionary with the model stored
        :return: a tuple with a dictionary of variables and a :py:class:`LpProblem`
        """

        # we instantiate the problem
        params = _dict['parameters']
        pb_params = {'name', 'sense'}
        args = {k: params[k] for k in pb_params}
        pb = cls(**args)
        pb.status = params['status']
        pb.sol_status = params['sol_status']

        # recreate the variables.
        var = {v['name']: LpVariable.from_dict(**v) for v in _dict['variables']}

        # objective function.
        # we change the names for the objects:
        obj_e = {var[v['name']]: v['value'] for v in _dict['objective']['coefficients']}
        pb += LpAffineExpression(e=obj_e, name=_dict['objective']['name'])

        # constraints
        # we change the names for the objects:
        def edit_const(const):
            const = dict(const)
            const['coefficients'] = {var[v['name']]: v['value'] for v in const['coefficients']}
            return const

        constraints = [edit_const(v) for v in _dict['constraints']]
        for c in constraints:
            pb += LpConstraint.from_dict(c)

        # last, parameters, other options
        list_to_dict = lambda v: {k: v for k, v in enumerate(v)}
        pb.sos1 = list_to_dict(_dict['sos1'])
        pb.sos2 = list_to_dict(_dict['sos2'])

        return var, pb

    def to_json(self, filename, *args, **kwargs):
        """
        Creates a json file from the LpProblem information

        :param str filename: filename to write json
        :param args: additional arguments for json function
        :param kwargs: additional keyword arguments for json function
        :return: None
        """
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, *args,  **kwargs)

    @classmethod
    def from_json(cls, filename):
        """
        Creates a new Lp Problem from a json file with information

        :param str filename: json file name
        :return: a tuple with a dictionary of variables and an LpProblem
        :rtype: (dict, :py:class:`LpProblem`)
        """
        with open(filename, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)

    def normalisedNames(self):
        constraintsNames = {k: "C%07d" % i for i, k in enumerate(self.constraints)}
        _variables = self.variables()
        variablesNames = {k.name: "X%07d" % i for i, k in enumerate(_variables)}
        return constraintsNames, variablesNames, "OBJ"

    def isMIP(self):
        for v in self.variables():
            if v.cat == const.LpInteger: return 1
        return 0

    def roundSolution(self, epsInt = 1e-5, eps = 1e-7):
        """
        Rounds the lp variables

        Inputs:
            - none

        Side Effects:
            - The lp variables are rounded
        """
        for v in self.variables():
            v.round(epsInt, eps)

    def unusedConstraintName(self):
        self.lastUnused += 1
        while 1:
            s = "_C%d" % self.lastUnused
            if s not in self.constraints: break
            self.lastUnused += 1
        return s

    def valid(self, eps = 0):
        for v in self.variables():
            if not v.valid(eps): return False
        for c in self.constraints.values():
            if not c.valid(eps): return False
        else:
            return True

    def infeasibilityGap(self, mip = 1):
        gap = 0
        for v in self.variables():
            gap = max(abs(v.infeasibilityGap(mip)), gap)
        for c in self.constraints.values():
            if not c.valid(0):
                gap = max(abs(c.value()), gap)
        return gap

    def addVariable(self, variable):
        """
        Adds a variable to the problem before a constraint is added

        @param variable: the variable to be added
        """
        if variable.hash not in self._variable_ids:
            self._variables.append(variable)
            self._variable_ids[variable.hash] = variable

    def addVariables(self, variables):
        """
        Adds variables to the problem before a constraint is added

        @param variables: the variables to be added
        """
        for v in variables:
            self.addVariable(v)

    def variables(self):
        """
        Returns a list of the problem variables

        Inputs:
            - none

        Returns:
            - A list of the problem variables
        """
        if self.objective:
            self.addVariables(list(self.objective.keys()))
        for c in self.constraints.values():
            self.addVariables(list(c.keys()))
        self._variables.sort(key=lambda v: v.name)
        return self._variables

    def variablesDict(self):
        variables = {}
        if self.objective:
            for v in self.objective:
                variables[v.name] = v
        for c in list(self.constraints.values()):
            for v in c:
                variables[v.name] = v
        return variables

    def add(self, constraint, name = None):
        self.addConstraint(constraint, name)

    def addConstraint(self, constraint, name = None):
        if not isinstance(constraint, LpConstraint):
            raise TypeError("Can only add LpConstraint objects")
        if name:
            constraint.name = name
        try:
            if constraint.name:
                name = constraint.name
            else:
                name = self.unusedConstraintName()
        except AttributeError:
            raise TypeError("Can only add LpConstraint objects")
            #removed as this test fails for empty constraints
#        if len(constraint) == 0:
#            if not constraint.valid():
#                raise ValueError, "Cannot add false constraints"
        if name in self.constraints:
            if self.noOverlap:
                raise const.PulpError("overlapping constraint names: " + name)
            else:
                print("Warning: overlapping constraint names:", name)
        self.constraints[name] = constraint
        self.modifiedConstraints.append(constraint)
        self.addVariables(list(constraint.keys()))

    def setObjective(self, obj):
        """
        Sets the input variable as the objective function. Used in Columnwise Modelling

        :param obj: the objective function of type :class:`LpConstraintVar`

        Side Effects:
            - The objective function is set
        """
        if isinstance(obj, LpVariable):
            # allows the user to add a LpVariable as an objective
            obj = obj + 0.0
        try:
            obj = obj.constraint
            name = obj.name
        except AttributeError:
            name = None
        self.objective = obj
        self.objective.name = name
        self.resolveOK = False

    def __iadd__(self, other):
        if isinstance(other, tuple):
            other, name = other
        else:
            name = None
        if other is True:
            return self
        if isinstance(other, LpConstraintVar):
            self.addConstraint(other.constraint)
        elif isinstance(other, LpConstraint):
            self.addConstraint(other, name)
        elif isinstance(other, LpAffineExpression):
            if self.objective is not None:
                warnings.warn("Overwriting previously set objective.")
            self.objective = other
            self.objective.name = name
        elif isinstance(other, LpVariable) or isinstance(other, (int, float)):
            if self.objective is not None:
                warnings.warn("Overwriting previously set objective.")
            self.objective = LpAffineExpression(other)
            self.objective.name = name
        else:
            raise TypeError("Can only add LpConstraintVar, LpConstraint, LpAffineExpression or True objects")
        return self

    def extend(self, other, use_objective = True):
        """
        extends an LpProblem by adding constraints either from a dictionary
        a tuple or another LpProblem object.

        @param use_objective: determines whether the objective is imported from
        the other problem

        For dictionaries the constraints will be named with the keys
        For tuples an unique name will be generated
        For LpProblems the name of the problem will be added to the constraints
        name
        """
        if isinstance(other, dict):
            for name in other:
                self.constraints[name] = other[name]
        elif isinstance(other, LpProblem):
            for v in set(other.variables()).difference(self.variables()):
                v.name = other.name + v.name
            for name,c in other.constraints.items():
                c.name = other.name + name
                self.addConstraint(c)
            if use_objective:
                self.objective += other.objective
        else:
            for c in other:
                if isinstance(c,tuple):
                    name = c[0]
                    c = c[1]
                else:
                    name = None
                if not name: name = c.name
                if not name: name = self.unusedConstraintName()
                self.constraints[name] = c

    def coefficients(self, translation = None):
        coefs = []
        if translation == None:
            for c in self.constraints:
                cst = self.constraints[c]
                coefs.extend([(v.name, c, cst[v]) for v in cst])
        else:
            for c in self.constraints:
                ctr = translation[c]
                cst = self.constraints[c]
                coefs.extend([(translation[v.name], ctr, cst[v]) for v in cst])
        return coefs

    def writeMPS(self, filename, mpsSense = 0, rename = 0, mip = 1):
        """
        Writes an mps files from the problem information

        :param str filename: name of the file to write
        :param int mpsSense:
        :param bool rename: if True, normalized names are used for variables and constraints
        :param mip: variables and variable renames
        :return:
        Side Effects:
            - The file is created
        """
        wasNone, dummyVar = self.fixObjective()
        if mpsSense == 0: mpsSense = self.sense
        cobj = self.objective
        if mpsSense != self.sense:
            n = cobj.name
            cobj = - cobj
            cobj.name = n
        if rename:
            constrNames, varNames, cobj.name = self.normalisedNames()
            # No need to call self.variables() again, we have just filled self._variables:
            vs = self._variables
        else:
            vs = self.variables()
            varNames = dict((v.name, v.name) for v in vs)
            constrNames = dict((c, c) for c in self.constraints)
        model_name = self.name
        if rename:
            model_name = "MODEL"
        objName = cobj.name
        if not objName:
            objName = "OBJ"

        # constraints
        mpsConstraintType = {const.LpConstraintLE: "L", const.LpConstraintEQ: "E", const.LpConstraintGE: "G"}
        row_lines = [" "+mpsConstraintType[c.sense] + "  " + constrNames[k] + "\n"
                     for k, c in self.constraints.items()]
        # Creation of a dict of dict:
        # coefs[variable_name][constraint_name] = coefficient
        coefs = {varNames[v.name]: {} for v in vs}
        for k, c in self.constraints.items():
            k = constrNames[k]
            for v, value in c.items():
                coefs[varNames[v.name]][k] = value

        # matrix
        columns_lines = []
        for v in vs:
            name = varNames[v.name]
            columns_lines.extend(self.MPS_column_lines(coefs[name], v, mip, name, cobj, objName))

        # right hand side
        rhs_lines = ["    RHS       %-8s  % .12e\n" % (constrNames[k], -c.constant if c.constant != 0 else 0)
                     for k, c in self.constraints.items()]
        # bounds
        bound_lines = []
        for v in vs:
            bound_lines.extend(self.MPS_bound_lines(varNames[v.name], v, mip))

        with open(filename, "w") as f:
            f.write("*SENSE:"+ const.LpSenses[mpsSense]+"\n")
            f.write("NAME          " + model_name + "\n")
            f.write("ROWS\n")
            f.write(" N  %s\n" % objName)
            f.write(''.join(row_lines))
            f.write("COLUMNS\n")
            f.write(''.join(columns_lines))
            f.write("RHS\n")
            f.write(''.join(rhs_lines))
            f.write("BOUNDS\n")
            f.write(''.join(bound_lines))
            f.write("ENDATA\n")
        self.restoreObjective(wasNone, dummyVar)
        # returns the variables, in writing order
        if rename == 0:
            return vs
        else:
            return vs, varNames, constrNames, cobj.name

    @staticmethod
    def MPS_column_lines(cv, variable, mip, name, cobj, objName):
        columns_lines = []
        if mip and variable.cat == const.LpInteger:
            columns_lines.append("    MARK      'MARKER'                 'INTORG'\n")
        # Most of the work is done here
        _tmp = ["    %-8s  %-8s  % .12e\n" % (name, k, v) for k, v in cv.items()]
        columns_lines.extend(_tmp)

        # objective function
        if variable in cobj:
            columns_lines.append("    %-8s  %-8s  % .12e\n" % (name, objName, cobj[variable]))
        if mip and variable.cat == const.LpInteger:
            columns_lines.append("    MARK      'MARKER'                 'INTEND'\n")
        return columns_lines

    @staticmethod
    def MPS_bound_lines(name, variable, mip):
        if variable.lowBound is not None and variable.lowBound == variable.upBound:
            return [" FX BND       %-8s  % .12e\n" % (name, variable.lowBound)]
        elif variable.lowBound == 0 and variable.upBound == 1 and mip and variable.cat == const.LpInteger:
            return [" BV BND       %-8s\n" % name]
        bound_lines = []
        if variable.lowBound is not None:
            # In MPS files, variables with no bounds (i.e. >= 0)
            # are assumed BV by COIN and CPLEX.
            # So we explicitly write a 0 lower bound in this case.
            if variable.lowBound != 0 or (mip and variable.cat == const.LpInteger and variable.upBound is None):
                bound_lines.append(" LO BND       %-8s  % .12e\n" % (name, variable.lowBound))
        else:
            if variable.upBound is not None:
                bound_lines.append(" MI BND       %-8s\n" % name)
            else:
                bound_lines.append(" FR BND       %-8s\n" % name)
        if variable.upBound is not None:
            bound_lines.append(" UP BND       %-8s  % .12e\n" % (name, variable.upBound))
        return bound_lines

    def writeLP(self, filename, writeSOS = 1, mip = 1, max_length=100):
        """
        Write the given Lp problem to a .lp file.

        This function writes the specifications (objective function,
        constraints, variables) of the defined Lp problem to a file.

        :param str filename: the name of the file to be created.
        :return: variables
        Side Effects:
            - The file is created
        """
        f = open(filename, "w")
        f.write("\\* "+self.name + " *\\\n")
        if self.sense == 1:
            f.write("Minimize\n")
        else:
            f.write("Maximize\n")
        wasNone, objectiveDummyVar = self.fixObjective()
        objName = self.objective.name
        if not objName: objName = "OBJ"
        f.write(self.objective.asCplexLpAffineExpression(objName, constant = 0))
        f.write("Subject To\n")
        ks = list(self.constraints.keys())
        ks.sort()
        dummyWritten = False
        for k in ks:
            constraint = self.constraints[k]
            if not list(constraint.keys()):
                #empty constraint add the dummyVar
                dummyVar = self.get_dummyVar()
                constraint += dummyVar
                #set this dummyvar to zero so infeasible problems are not made feasible
                if not dummyWritten:
                    f.write((dummyVar == 0.0).asCplexLpConstraint("_dummy"))
                    dummyWritten = True
            f.write(constraint.asCplexLpConstraint(k))
        # check if any names are longer than 100 characters
        self.checkLengthVars(max_length)
        vs = self.variables()
        # check for repeated names
        self.checkDuplicateVars()
        # Bounds on non-"positive" variables
        # Note: XPRESS and CPLEX do not interpret integer variables without
        # explicit bounds
        if mip:
            vg = [v for v in vs if not (v.isPositive() and v.cat == const.LpContinuous) \
                and not v.isBinary()]
        else:
            vg = [v for v in vs if not v.isPositive()]
        if vg:
            f.write("Bounds\n")
            for v in vg:
                f.write("%s\n" % v.asCplexLpVariable())
        # Integer non-binary variables
        if mip:
            vg = [v for v in vs if v.cat == const.LpInteger and not v.isBinary()]
            if vg:
                f.write("Generals\n")
                for v in vg: f.write("%s\n" % v.name)
            # Binary variables
            vg = [v for v in vs if v.isBinary()]
            if vg:
                f.write("Binaries\n")
                for v in vg: f.write("%s\n" % v.name)
        # Special Ordered Sets
        if writeSOS and (self.sos1 or self.sos2):
            f.write("SOS\n")
            if self.sos1:
                for sos in self.sos1.values():
                    f.write("S1:: \n")
                    for v, val in sos.items():
                        f.write(" %s: %.12g\n" % (v.name, val))
            if self.sos2:
                for sos in self.sos2.values():
                    f.write("S2:: \n")
                    for v, val in sos.items():
                        f.write(" %s: %.12g\n" % (v.name, val))
        f.write("End\n")
        f.close()
        self.restoreObjective(wasNone, objectiveDummyVar)
        return vs

    def checkDuplicateVars(self):
        """
        Checks if there are at least two variables with the same name
        :return: 1
        :raises `const.PulpError`: if there ar duplicates
        """
        vs = self.variables()

        repeated_names = {}
        for v in vs:
            repeated_names[v.name] = repeated_names.get(v.name, 0) + 1
        repeated_names = [(key, value) for key, value in list(repeated_names.items())
                          if value >= 2]
        if repeated_names:
            raise const.PulpError('Repeated variable names:\n' + str(repeated_names))
        return 1

    def checkLengthVars(self, max_length):
        """
        Checks if variables have names smaller than `max_length`
        :param int max_length: max size for variable name
        :return:
        :raises const.PulpError: if there is at least one variable that has a long name
        """
        vs = self.variables()
        long_names = [v.name for v in vs if len(v.name) > max_length]
        if long_names:
            raise const.PulpError('Variable names too long for Lp format\n'
                                + str(long_names))
        return 1

    def assignVarsVals(self, values):
        variables = self.variablesDict()
        for name in values:
            if name != '__dummy':
                variables[name].varValue = values[name]

    def assignVarsDj(self,values):
        variables = self.variablesDict()
        for name in values:
            if name != '__dummy':
                variables[name].dj = values[name]

    def assignConsPi(self, values):
        for name in values:
            try:
                self.constraints[name].pi = values[name]
            except KeyError:
                pass

    def assignConsSlack(self, values, activity=False):
        for name in values:
            try:
                if activity:
                    # reports the activity not the slack
                    self.constraints[name].slack = -1 * (
                            self.constraints[name].constant + float(values[name]))
                else:
                    self.constraints[name].slack = float(values[name])
            except KeyError:
                pass

    def get_dummyVar(self):
        if self.dummyVar is None:
            self.dummyVar = LpVariable("__dummy", 0, 0)
        return self.dummyVar

    def fixObjective(self):
        if self.objective is None:
            self.objective = 0
            wasNone = 1
        else:
            wasNone = 0
        if not isinstance(self.objective, LpAffineExpression):
            self.objective = LpAffineExpression(self.objective)
        if self.objective.isNumericalConstant():
            dummyVar = self.get_dummyVar()
            self.objective += dummyVar
        else:
            dummyVar = None
        return wasNone, dummyVar

    def restoreObjective(self, wasNone, dummyVar):
        if wasNone:
            self.objective = None
        elif not dummyVar is None:
            self.objective -= dummyVar

    def solve(self, solver = None, **kwargs):
        """
        Solve the given Lp problem.

        This function changes the problem to make it suitable for solving
        then calls the solver.actualSolve() method to find the solution

        :param solver:  Optional: the specific solver to be used, defaults to the
              default solver.

        Side Effects:
            - The attributes of the problem object are changed in
              :meth:`~pulp.solver.LpSolver.actualSolve()` to reflect the Lp solution
        """

        if not(solver): solver = self.solver
        if not(solver): solver = LpSolverDefault
        wasNone, dummyVar = self.fixObjective()
        #time it
        self.solutionTime = -clock()
        status = solver.actualSolve(self, **kwargs)
        self.solutionTime += clock()
        self.restoreObjective(wasNone, dummyVar)
        self.solver = solver
        return status

    def sequentialSolve(self, objectives, absoluteTols = None,
                        relativeTols = None, solver = None, debug = False):
        """
        Solve the given Lp problem with several objective functions.

        This function sequentially changes the objective of the problem
        and then adds the objective function as a constraint

        :param objectives: the list of objectives to be used to solve the problem
        :param absoluteTols: the list of absolute tolerances to be applied to
           the constraints should be +ve for a minimise objective
        :param relativeTols: the list of relative tolerances applied to the constraints
        :param solver: the specific solver to be used, defaults to the default solver.

        """
        #TODO Add a penalty variable to make problems elastic
        #TODO add the ability to accept different status values i.e. infeasible etc

        if not(solver): solver = self.solver
        if not(solver): solver = LpSolverDefault
        if not(absoluteTols):
            absoluteTols = [0] * len(objectives)
        if not(relativeTols):
            relativeTols  = [1] * len(objectives)
        #time it
        self.solutionTime = -clock()
        statuses = []
        for i,(obj,absol,rel) in enumerate(zip(objectives,
                                               absoluteTols, relativeTols)):
            self.setObjective(obj)
            status = solver.actualSolve(self)
            statuses.append(status)
            if debug: self.writeLP("%sSequence.lp"%i)
            if self.sense == const.LpMinimize:
                self += obj <= value(obj)*rel + absol,"%s_Sequence_Objective"%i
            elif self.sense == const.LpMaximize:
                self += obj >= value(obj)*rel + absol,"%s_Sequence_Objective"%i
        self.solutionTime += clock()
        self.solver = solver
        return statuses

    def resolve(self, solver = None, **kwargs):
        """
        resolves an Problem using the same solver as previously
        """
        if not(solver): solver = self.solver
        if self.resolveOK:
            return self.solver.actualResolve(self, **kwargs)
        else:
            return self.solve(solver = solver, **kwargs)

    def setSolver(self, solver = LpSolverDefault):
        """Sets the Solver for this problem useful if you are using
        resolve
        """
        self.solver = solver

    def numVariables(self):
        """

        :return: number of variables in model
        """
        return len(self._variable_ids)

    def numConstraints(self):
        """

        :return: number of constraints in model
        """
        return len(self.constraints)

    def getSense(self):
        return self.sense

    def assignStatus(self, status, sol_status=None):
        """
        Sets the status of the model after solving.
        :param status: code for the status of the model
        :param sol_status: code for the status of the solution
        :return:
        """
        if status not in const.LpStatus:
            raise const.PulpError("Invalid status code: "+str(status))

        if sol_status is not None and sol_status not in const.LpSolution:
            raise const.PulpError("Invalid solution status code: "+str(sol_status))

        self.status = status
        if sol_status is None:
            sol_status = const.LpStatusToSolution.get(status, const.LpSolutionNoSolutionFound)
        self.sol_status = sol_status
        return True


class FixedElasticSubProblem(LpProblem):
    """
    Contains the subproblem generated by converting a fixed constraint
    :math:`\sum_{i}a_i x_i = b` into an elastic constraint.

    :param constraint: The LpConstraint that the elastic constraint is based on
    :param penalty: penalty applied for violation (+ve or -ve) of the constraints
    :param proportionFreeBound:
        the proportional bound (+ve and -ve) on
        constraint violation that is free from penalty
    :param proportionFreeBoundList: the proportional bound on \
        constraint violation that is free from penalty, expressed as a list\
        where [-ve, +ve]
    """
    def __init__(self, constraint, penalty = None,
                                        proportionFreeBound = None,
                                        proportionFreeBoundList = None):
        subProblemName =  "%s_elastic_SubProblem" % constraint.name
        LpProblem.__init__(self, subProblemName, const.LpMinimize)
        self.objective = LpAffineExpression()
        self.constraint = constraint
        self.constant = constraint.constant
        self.RHS = - constraint.constant
        self.objective = LpAffineExpression()
        self += constraint, "_Constraint"
        #create and add these variables but disabled
        self.freeVar = LpVariable("_free_bound",
                                  upBound = 0, lowBound = 0)
        self.upVar = LpVariable("_pos_penalty_var",
                                upBound = 0, lowBound = 0)
        self.lowVar = LpVariable("_neg_penalty_var",
                                 upBound = 0, lowBound = 0)
        constraint.addInPlace(self.freeVar + self.lowVar + self.upVar)
        if proportionFreeBound:
            proportionFreeBoundList = [proportionFreeBound, proportionFreeBound]
        if proportionFreeBoundList:
            #add a costless variable
            self.freeVar.upBound = abs(constraint.constant *
                                        proportionFreeBoundList[0])
            self.freeVar.lowBound = -abs(constraint.constant *
                                       proportionFreeBoundList[1])
            # Note the reversal of the upbound and lowbound due to the nature of the
            # variable
        if penalty is not None:
            #activate these variables
            self.upVar.upBound = None
            self.lowVar.lowBound = None
            self.objective = penalty*self.upVar - penalty*self.lowVar

    def _findValue(self, attrib):
        """
        safe way to get the value of a variable that may not exist
        """
        var = getattr(self, attrib, 0)
        if var:
            if value(var) is not None:
                return value(var)
            else:
                return 0.0
        else:
            return 0.0

    def isViolated(self):
        """
        returns true if the penalty variables are non-zero
        """
        upVar = self._findValue("upVar")
        lowVar = self._findValue("lowVar")
        freeVar = self._findValue("freeVar")
        result = abs(upVar + lowVar) >= const.EPS
        if result:
            log.debug("isViolated %s, upVar %s, lowVar %s, freeVar %s result %s"%(
                        self.name, upVar, lowVar, freeVar, result))
            log.debug("isViolated value lhs %s constant %s"%(
                         self.findLHSValue(), self.RHS))
        return result

    def findDifferenceFromRHS(self):
        """
        The amount the actual value varies from the RHS (sense: LHS - RHS)
        """
        return self.findLHSValue() - self.RHS


    def findLHSValue(self):
        """
        for elastic constraints finds the LHS value of the constraint without
        the free variable and or penalty variable assumes the constant is on the
        rhs
        """
        upVar = self._findValue("upVar")
        lowVar = self._findValue("lowVar")
        freeVar = self._findValue("freeVar")
        return self.constraint.value() - self.constant - \
                upVar - lowVar - freeVar

    def deElasticize(self):
        """ de-elasticize constraint """
        self.upVar.upBound = 0
        self.lowVar.lowBound = 0

    def reElasticize(self):
        """
        Make the Subproblem elastic again after deElasticize
        """
        self.upVar.lowBound = 0
        self.upVar.upBound = None
        self.lowVar.upBound = 0
        self.lowVar.lowBound = None

    def alterName(self, name):
        """
        Alters the name of anonymous parts of the problem

        """
        self.name = "%s_elastic_SubProblem" % name
        if hasattr(self, 'freeVar'):
            self.freeVar.name = self.name + "_free_bound"
        if hasattr(self, 'upVar'):
            self.upVar.name = self.name + "_pos_penalty_var"
        if hasattr(self, 'lowVar'):
            self.lowVar.name = self.name + "_neg_penalty_var"


class FractionElasticSubProblem(FixedElasticSubProblem):
    """
    Contains the subproblem generated by converting a Fraction constraint
    numerator/(numerator+complement) = b
    into an elastic constraint

    :param name: The name of the elastic subproblem
    :param penalty: penalty applied for violation (+ve or -ve) of the constraints
    :param proportionFreeBound: the proportional bound (+ve and -ve) on
        constraint violation that is free from penalty
    :param proportionFreeBoundList: the proportional bound on
        constraint violation that is free from penalty, expressed as a list
        where [-ve, +ve]
    """
    def __init__(self, name, numerator, RHS, sense,
                                        complement = None,
                                        denominator = None,
                                        penalty = None,
                                        proportionFreeBound = None,
                                        proportionFreeBoundList = None):
        subProblemName = "%s_elastic_SubProblem" % name
        self.numerator = numerator
        if denominator is None and complement is not None:
            self.complement = complement
            self.denominator = numerator + complement
        elif denominator is not None and complement is None:
            self.denominator = denominator
            self.complement = denominator - numerator
        else:
            raise const.PulpError('only one of denominator and complement must be specified')
        self.RHS = RHS
        self.lowTarget = self.upTarget = None
        LpProblem.__init__(self, subProblemName, const.LpMinimize)
        self.freeVar = LpVariable("_free_bound",
                                  upBound = 0, lowBound = 0)
        self.upVar = LpVariable("_pos_penalty_var",
                                upBound = 0, lowBound = 0)
        self.lowVar = LpVariable("_neg_penalty_var",
                                 upBound = 0, lowBound = 0)
        if proportionFreeBound:
            proportionFreeBoundList = [proportionFreeBound, proportionFreeBound]
        if proportionFreeBoundList:
            upProportionFreeBound, lowProportionFreeBound = \
                    proportionFreeBoundList
        else:
            upProportionFreeBound, lowProportionFreeBound = (0, 0)
        #create an objective
        self += LpAffineExpression()
        #There are three cases if the constraint.sense is ==, <=, >=
        if sense in [const.LpConstraintEQ, const.LpConstraintLE]:
            #create a constraint the sets the upper bound of target
            self.upTarget = RHS + upProportionFreeBound
            self.upConstraint = LpFractionConstraint(self.numerator,
                                    self.complement,
                                    const.LpConstraintLE,
                                    self.upTarget,
                                    denominator = self.denominator)
            if penalty is not None:
                self.lowVar.lowBound = None
                self.objective += -1* penalty * self.lowVar
                self.upConstraint += self.lowVar
            self += self.upConstraint, '_upper_constraint'
        if sense in [const.LpConstraintEQ, const.LpConstraintGE]:
            #create a constraint the sets the lower bound of target
            self.lowTarget = RHS - lowProportionFreeBound
            self.lowConstraint = LpFractionConstraint(self.numerator,
                                                 self.complement,
                                                const.LpConstraintGE,
                                                self.lowTarget,
                                                denominator = self.denominator)
            if penalty is not None:
                self.upVar.upBound = None
                self.objective += penalty * self.upVar
                self.lowConstraint += self.upVar
            self += self.lowConstraint, '_lower_constraint'

    def findLHSValue(self):
        """
        for elastic constraints finds the LHS value of the constraint without
        the free variable and or penalty variable assumes the constant is on the
        rhs
        """
        # uses code from LpFractionConstraint
        if abs(value(self.denominator))>= const.EPS:
            return value(self.numerator)/value(self.denominator)
        else:
            if abs(value(self.numerator))<= const.EPS:
                #zero divided by zero will return 1
                return 1.0
            else:
                raise ZeroDivisionError

    def isViolated(self):
        """
        returns true if the penalty variables are non-zero
        """
        if abs(value(self.denominator))>= const.EPS:
            if self.lowTarget is not None:
                if self.lowTarget > self.findLHSValue():
                    return True
            if self.upTarget is not None:
                if self.findLHSValue() > self.upTarget:
                    return True
        else:
            #if the denominator is zero the constraint is satisfied
            return False


def lpSum(vector):
    """
    Calculate the sum of a list of linear expressions

    :param vector: A list of linear expressions
    """
    return LpAffineExpression().addInPlace(vector)


def lpDot(v1, v2):
    """Calculate the dot product of two lists of linear expressions"""
    if not const.isiterable(v1) and not const.isiterable(v2):
        return v1 * v2
    elif not const.isiterable(v1):
        return lpDot([v1]*len(v2),v2)
    elif not const.isiterable(v2):
        return lpDot(v1,[v2]*len(v1))
    else:
        return lpSum([lpDot(e1,e2) for e1,e2 in zip(v1,v2)])
