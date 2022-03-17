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

import random
from typing import Any, List, Union
from pyconduit import Category, block
import math
from pydantic import confloat, conint
import operator as op

SAFE_NUMBER = Union[confloat(le = 10000), conint(le = 10000)]

# MATH
# Contains blocks to interact with numbers.
class Math(Category):
    """
    Contains blocks to interact with numbers.
    """

    @block
    @staticmethod
    def create_integer(*, value : Any) -> int:
        """
        Convert a value to an integer.

        Args:
            value:
                Any value.
        """
        return int(value)

    
    @block
    @staticmethod
    def create_float(*, value : Any) -> float:
        """
        Convert a value to a float.

        Args:
            value:
                Any value.
        """
        return float(value)


    @block(label = "math.sum")
    @staticmethod
    def sum_(*, value1 : Union[int, float], value2 : Union[int, float]) -> Union[int, float]:
        """
        Return the sum of two numbers.

        Args:
            value1:
                Left side of the operator.
            value2:
                Right side of the operator.
        """
        return value1 + value2


    @block
    @staticmethod
    def sum_list(*, list : List[Any], start : Union[int, float] = 0) -> Union[int, float]:
        """
        Return the sum of a 'start' value (default: 0) plus an list of numbers.
        When the list is empty, return the start value. 

        Args:
            list:
                The list that contains items.
        """
        return sum(list, start)


    @block
    @staticmethod
    def sub(*, value1 : Union[int, float], value2 : Union[int, float]) -> Union[int, float]:
        """
        Return the subtraction of two numbers.

        Args:
            value1:
                Left side of the operator.
            value2:
                Right side of the operator.
        """
        return value1 - value2


    @block
    @staticmethod
    def div(*, value1 : Union[int, float], value2 : Union[int, float]) -> Union[int, float]:
        """
        Return the division of two numbers.

        Args:
            value1:
                Left side of the operator.
            value2:
                Right side of the operator.
        """
        return value1 / value2


    @block
    @staticmethod
    def mul(*, value1 : SAFE_NUMBER, value2 : SAFE_NUMBER) -> Union[int, float]:
        """
        Return the multiplication of two numbers.

        Args:
            value1:
                Left side of the operator.
            value2:
                Right side of the operator.
        """
        return value1 * value2


    @block
    @staticmethod
    def exp(*, value1 : confloat(le = 50), value2 : confloat(le = 50)) -> Union[int, float]:
        """
        Returns the value of x to the power of y.

        Args:
            value1:
                Left side of the operator.
            value2:
                Right side of the operator.
        """
        return value1 ** value2


    @block
    @staticmethod
    def mod(*, value1 : Union[int, float], value2 : Union[int, float]) -> Union[int, float]:
        """
        Performs a division and then returns the remainder of the division.

        Args:
            value1:
                Left side of the operator.
            value2:
                Right side of the operator.
        """
        return value1 % value2

    
    @block
    @staticmethod
    def floor(*, value : Union[int, float]) -> int:
        """
        Returns the greatest integer that's less than or equal to the given number.

        Args:
            value:
                A number.
        """
        return math.floor(value)

    
    @block
    @staticmethod
    def ceiling(*, value : Union[int, float]) -> int:
        """
        Returns the smallest integer that's greater than or equal to the given number.

        Args:
            value:
                A number.
        """
        return math.ceil(value)


    @block
    @staticmethod
    def random(*, value1 : SAFE_NUMBER, value2 : SAFE_NUMBER) -> int:
        """
        Returns a random integer from between value1 and value2 (including both numbers).

        Args:
            value1:
                A number.
            value2:
                A number.
        """
        return random.randint(value1, value2)


    @block(label = "math.max")
    @staticmethod
    def max_(*, value1 : Any, value2 : Any) -> Any:
        """
        Return the largest value from two values.

        Args:
            value1:
                First value.
            value2:
                Second value.
        """
        return max(value1, value2)

    
    @block
    @staticmethod
    def sqrt(*, value : Union[int, float]) -> Union[int, float]:
        """
        Returns the square root of the given number.

        Args:
            value:
                A number.
        """
        return math.sqrt(value)

    
    @block(label = "math.abs")
    @staticmethod
    def abs_(*, value : Any) -> Any:
        """
        Return the absolute value of the argument.

        Args:
            value:
                A number.
        """
        return op.abs(value)


    @block
    @staticmethod
    def max_list(*, list : List[Any]) -> Any:
        """
        Return the largest value from a list.

        Args:
            list:
                The list that contains items.
        """
        return max(list)


    @block(label = "math.min")
    @staticmethod
    def min_(*, value1 : Any, value2 : Any) -> Any:
        """
        Return the smallest value from two items.

        Args:
            value1:
                First value.
            value2:
                Second value.
        """
        return min(value1, value2)
    

    @block
    @staticmethod
    def min_list(*, list : List[Any]) -> Any:
        """
        Return the smallest value from a list.

        Args:
            list:
                The list that contains items.
        """
        return min(list)