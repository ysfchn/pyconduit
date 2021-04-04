# MIT License
# 
# Copyright (c) 2021 Yusuf Cihan
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import Any, Dict, List, Union
from enum import Enum
from pyconduit.category import ConduitCategory
from pyconduit.other import ConduitError
from pyconduit.enums import ConduitStatus
from pyconduit.category import ConduitBlock as conduitblock
import operator as op

class LogicalOperators(str, Enum):
    EQUALS = "="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUALS = ">="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUALS = "<="
    IS = "is"
    IS_NOT = "is not"

# LOGIC
# Contains blocks to work with conditions and logic values.
class Logic(ConduitCategory):
    """
    Contains blocks to work with conditions and logic values.
    """

    @conduitblock.make(name = "bool")
    def bool_(*, value : Any) -> bool:
        """
        Returns the value as bool.

        Args:
            value:
                The value that will be converted to bool.
        """
        return bool(value)


    @conduitblock.make(name = "if")
    def if_(*, value1 : Any, value2 : Any, operator : LogicalOperators) -> bool:
        """
        Performs a classic "IF" condition and returns the result.

        Args:
            value1:
                Left side of the operator.
            value2:
                Right side of the operator.
            operator:
                One of conditional operators.
                ```
                "=" (equals), 
                "!=" (not equals), 
                ">" (greater than), 
                ">=" (greater than or equal)
                "<" (less than)
                "<=" (less than or equal)
                "is" (is)
                "is not" (is not)
                ```
        """
        _operators = {
            LogicalOperators.EQUALS: op.eq,
            LogicalOperators.NOT_EQUALS: op.ne,
            LogicalOperators.GREATER_THAN: op.gt,
            LogicalOperators.GREATER_THAN_OR_EQUALS: op.ge,
            LogicalOperators.LESS_THAN: op.lt,
            LogicalOperators.LESS_THAN_OR_EQUALS: op.le,
            LogicalOperators.IS: op.is_,
            LogicalOperators.IS_NOT: op.is_not
        }
        return _operators[operator](value1, value2)


    @conduitblock.make
    def is_truth(*, value : Any) -> bool:
        """
        Checks if value is truthy.

        A truthy value is a value that translates to "true" when evaluated in a boolean context.
        Empty sequences, collections and numeric values that are zero (0) means a falsy value.

        Args:
            value:
                Any value.
        """
        return op.truth(value)


    @conduitblock.make
    def is_none(*, value : Any) -> bool:
        """
        Checks if value is equals to `None`.

        Args:
            value:
                Any value.
        """
        return value == None


    @conduitblock.make
    def true() -> bool:
        """
        Returns logical `True`.
        """
        return True


    @conduitblock.make
    def false() -> bool:
        """
        Returns logical `False`.
        """
        return False


    @conduitblock.make
    def none() -> None:
        """
        Returns `None`.
        """
        return None

    
    @conduitblock.make
    def if_then_else(*, value : Any, then : Any, otherwise : Any) -> Any:
        """
        Checks if `value` is a truthy value or not. If it is a truthy value, then it returns `then` parameter,
        otherwise it returns the `otherwise` parameter.

        Args:
            value:
                Any value.
            then:
                The value that will return if `value` is truthy.
            otherwise:
                The value that will return if `value` is not truthy.
        """
        if value:
            return then
        else:
            return otherwise


    @conduitblock.make
    def logical_not(*, value : Any) -> bool:
        """
        Performs logical negation, returning false if the input is true, and true if the input is false.

        Args:
            value:
                Any value.
        """
        return not value


    @conduitblock.make
    def logical_or(*, value1 : Any, value2 : Any) -> bool:
        """
        Performs logical OR operation, returns true if one of the inputs are true, if all inputs are false, then it returns false.
        
        Args:
            value1:
                First value.
            value2:
                Second value.
        """
        return value1 or value2


    @conduitblock.make
    def logical_and(*, value1 : Any, value2 : Any) -> bool:
        """
        Performs logical AND operation, returns true if all inputs are true, otherwise it returns false.

        Args:
            value1:
                First value.
            value2:
                Second value.
        """
        return value1 and value2

    
    @conduitblock.make
    def bitwise_and(*, value1 : Any, value2 : Any) -> Any:
        """
        Performs bitwise AND operation.

        Args:
            value1:
                First value.
            value2:
                Second value.
        """
        return value1 & value2

    
    @conduitblock.make
    def bitwise_or(*, value1 : Any, value2 : Any) -> Any:
        """
        Performs bitwise OR operation.

        Args:
            value1:
                First value.
            value2:
                Second value.
        """
        return value1 | value2

    
    @conduitblock.make
    def bitwise_not(*, value : Any) -> Any:
        """
        Performs bitwise NOT operation.

        Args:
            value:
                Any value.
        """
        return ~value

    
    @conduitblock.make(name = "assert")
    def assert_(*, value : Any) -> None:
        """
        Raises an error if value is not truthy. Useful if you want to force the value to be truthy.

        Args:
            value:
                The value that will be checked.
        """
        assert value, value

    
    @conduitblock.make
    def not_assert(*, value : Any) -> None:
        """
        Raises an error if value is truthy. Useful if you want to force the value to be not truthy.

        Args:
            value:
                The value that will be checked.
        """
        assert not value, value

    
    @conduitblock.make
    def if_assert(*, value1 : Any, value2 : Any, operator : LogicalOperators) -> None:
        """
        Performs a classic "IF" condition. And raises an error if check is `False`. 
        Useful if you want to terminate the workflow when the condition results with `False`.

        Args:
            value1:
                Left side of the operator.
            value2:
                Right side of the operator.
            operator:
                One of conditional operators.
                ```
                "=" (equals), 
                "!=" (not equals), 
                ">" (greater than), 
                ">=" (greater than or equal)
                "<" (less than)
                "<=" (less than or equal)
                "is" (is)
                "is not" (is not)
                ```
        """
        _operators = {
            LogicalOperators.EQUALS: op.eq,
            LogicalOperators.NOT_EQUALS: op.ne,
            LogicalOperators.GREATER_THAN: op.gt,
            LogicalOperators.GREATER_THAN_OR_EQUALS: op.ge,
            LogicalOperators.LESS_THAN: op.lt,
            LogicalOperators.LESS_THAN_OR_EQUALS: op.le,
            LogicalOperators.IS: op.is_,
            LogicalOperators.IS_NOT: op.is_not
        }
        assert _operators[operator](value1, value2), False
