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

from typing import Any, Optional
from pyconduit.category import ConduitCategory
from pyconduit.category import ConduitBlock as conduitblock
import copy

# OBJECT
# Contains blocks to manage objects.
class Object(ConduitCategory):
    """
    Contains blocks to manage objects.
    """

    @conduitblock.make
    def create_slice(*, stop : Optional[int] = None, start : Optional[int] = None, step : Optional[int] = None) -> slice:
        """
        Creates a new slice object and returns it.
        """
        return slice(start, stop, step)

    
    @conduitblock.make
    def apply_slice(*, value : Any, slice : slice) -> Any:
        """
        Slices a given sequence.
        """
        return value[slice]


    @conduitblock.make
    def slice_value(*, value : Any, stop : Optional[int] = None, start : Optional[int] = None, step : Optional[int] = None) -> Any:
        """
        Slices a given sequence.
        """
        slice_object = slice(start, stop, step)
        return value[slice_object]


    @conduitblock.make
    def copy(*, value : Any) -> Any:
        """
        Shallow copy operation.
        """
        return copy.copy(value)

    
    @conduitblock.make
    def length(*, value : Any) -> Any:
        """
        Get length of the object.
        """
        return len(value)
