# MIT License
# 
# Copyright (c) 2022-present Yusuf Cihan
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

from typing import Any
from enum import Enum
from pyconduit import Category, block, NodeStatus, ConduitError
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
class Logic(Category):
    """
    Contains blocks to work with conditions and logic values.
    """

    @block(label = "bool")
    def bool_(*, value : Any) -> bool:
        """
        Returns the value as bool.

        Args:
            value:
                The value that will be converted to bool.
        """
        return bool(value)


    @block(label = "if")
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


    @block
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


    @block
    def is_none(*, value : Any) -> bool:
        """
        Checks if value is equals to `None`.

        Args:
            value:
                Any value.
        """
        return value == None


    @block
    def true() -> bool:
        """
        Returns logical `True`.
        """
        return True


    @block
    def false() -> bool:
        """
        Returns logical `False`.
        """
        return False


    @block
    def none() -> None:
        """
        Returns `None`.
        """
        return None

    
    @block
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


    @block
    def logical_not(*, value : Any) -> bool:
        """
        Performs logical negation, returning false if the input is true, and true if the input is false.

        Args:
            value:
                Any value.
        """
        return not value


    @block
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


    @block
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

    
    @block
    def logical_nor(*, value1 : Any, value2 : Any) -> bool:
        """
        Performs logical NOR operation, returns true if all inputs are false, otherwise false.

        _Added in v1.1_
        
        Args:
            value1:
                First value.
            value2:
                Second value.
        """
        return not (value1 or value2)


    @block
    def logical_nand(*, value1 : Any, value2 : Any) -> bool:
        """
        Performs logical NAND operation, returns true if any input is false, otherwise it returns false.

        _Added in v1.1_

        Args:
            value1:
                First value.
            value2:
                Second value.
        """
        return not (value1 and value2)

    
    @block
    def logical_xor(*, value1 : Any, value2 : Any) -> bool:
        """
        Performs logical XOR operation, returns true if both value not equals in boolean context, otherwise it returns false.

        _Added in v1.1_

        Args:
            value1:
                First value.
            value2:
                Second value.
        """
        return bool(value1) != bool(value2)

    
    @block
    def logical_xnor(*, value1 : Any, value2 : Any) -> bool:
        """
        Performs logical XNOR (aka XAND) operation, returns true if both value equals in boolean context, otherwise it returns false.

        _Added in v1.1_

        Args:
            value1:
                First value.
            value2:
                Second value.
        """
        return bool(value1) == bool(value2)

    
    @block
    def bitwise_not(*, value : Any) -> Any:
        """
        Performs bitwise NOT operation.

        Args:
            value:
                Any value.
        """
        return ~value

    
    @block
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

    
    @block
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


    @block
    def bitwise_xor(*, value1 : Any, value2 : Any) -> bool:
        """
        Performs bitwise XOR operation, returns true if only a single value returns true, otherwise it returns false.

        _Added in v1.1_

        Args:
            value1:
                First value.
            value2:
                Second value.
        """
        return value1 ^ value2

    
    @block(label = "assert")
    def assert_(*, value : Any) -> None:
        """
        Raises an error if value is not truthy. Useful if you want to force the value to be truthy.

        Args:
            value:
                The value that will be checked.
        """
        if value:
            return
        raise ValueError(value)

    
    @block
    def not_assert(*, value : Any) -> None:
        """
        Raises an error if value is truthy. Useful if you want to force the value to be not truthy.

        Args:
            value:
                The value that will be checked.
        """
        if not value:
            return
        raise ValueError(value)

    
    @block
    def stop() -> None:
        """
        Stops the current working workflow.

        _Added in v1.1_
        """
        raise ConduitError(NodeStatus.KILLED_MANUALLY)

    
    @block
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
        if _operators[operator](value1, value2):
            return
        raise ValueError((value1, value2, ))
