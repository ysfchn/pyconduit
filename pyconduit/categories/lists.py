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

from typing import Any, List, Optional, Union, Dict
from pyconduit.category import ConduitCategory
from pyconduit.category import ConduitBlock as conduitblock
from pyconduit.step import ConduitVariable
from pyconduit.other import EMPTY

# Lists
# Contains blocks to interact with lists.
class Lists(ConduitCategory):
    """
    Contains blocks to interact with lists.
    """

    @conduitblock.make
    def create(*, value1 : Any = EMPTY, value2 : Any = EMPTY) -> List[Any]:
        """
        Creates a new list with items. If items are not provided, then returns an empty list.

        Args:
            value1:
                A value that will be added to list.
            value2:
                A value that will be added to list.
        """
        return [x for x in [value1, value2] if x != EMPTY]

    
    @conduitblock.make
    def count(*, list : Union[List[Any], ConduitVariable]) -> int:
        """
        Counts the elements in a list.

        Args:
            list:
                The list that will be used in the operation.
        """
        return len(list)

    
    @conduitblock.make
    def append(*, item : Any, list : Union[List[Any], ConduitVariable]) -> None:
        """
        Add item to the end of the list.

        Args:
            item:
                The item that will be added to list.
            list:
                The list that will be used in the operation.
        """
        return list.append(item)

    
    @conduitblock.make
    def clear(*, list : Union[List[Any], ConduitVariable]) -> None:
        """
        Remove all items from list.

        Args:
            list:
                The list that will be used in the operation.
        """
        list.clear()

    
    @conduitblock.make
    def extend(*, list1 : Union[List[Any], ConduitVariable], list2 : Union[List[Any], ConduitVariable]) -> None:
        """
        Extend list by appending elements from the `list2`. `list2` will not be modified but `list1` will be.

        Args:
            list1:
                First list.
            list2:
                Second list.
        """
        list1.extend(list2)

    
    @conduitblock.make
    def sort(*, list : Union[List[Any], ConduitVariable], reverse : bool = False) -> None:
        """
        Sort list in place.

        Args:
            list:
                The list that will be used in the operation.
            reverse:
                If `True`, the sorted list is reversed (or sorted in Descending order)
        """
        list.sort(key = None, reverse = reverse)
    

    @conduitblock.make
    def insert(*, list : Union[List[Any], ConduitVariable], index : int, item : Any) -> None:
        """
        Insert object before index.

        Args:
            list:
                The list that will be used in the operation.
            index:
                The index that will item placed in.
            item:
                The item that will be added to list.
        """
        list.insert(index, item)

    
    @conduitblock.make
    def copy(*, list : Union[List[Any], ConduitVariable]) -> List[Any]:
        """
        Return a shallow copy of the list.

        Args:
            list:
                The list that will be used in the operation.
        """
        return list.copy()

    
    @conduitblock.make
    def remove(*, item : Any, list : Union[List[Any], ConduitVariable]) -> None:
        """
        Remove a item from list.

        Args:
            item:
                The item that will be removed.
            list:
                The list that will be used in the operation.
        """
        list.remove(item)

    
    @conduitblock.make
    def pop(*, list : Union[List[Any], ConduitVariable], index : Optional[int] = None) -> Any:
        """
        Remove and return item at index (default last).

        Args:
            list:
                The list that will be used in the operation.
            index:
                The index of item that will be removed.
        """
        return list.pop(index)

    
    @conduitblock.make
    def reverse(*, list : Union[List[Any], ConduitVariable]) -> None:
        """
        Reverses the list in place.

        Args:
            list:
                The list that will be used in the operation.
        """
        list.reverse()

    
    @conduitblock.make
    def count_item(*, item : Any, list : Union[List[Any], ConduitVariable]) -> List[Any]:
        """
        Return number of occurrences of value.

        Args:
            item:
                The item that will be counted.
            list:
                The list that will be used in the operation.
        """
        return list.count(item)

    
    @conduitblock.make
    def merge(*, list1 : Union[List[Any], ConduitVariable], list2 : Union[List[Any], ConduitVariable]) -> List[Any]:
        """
        Merge the two lists.

        Args:
            list1:
                First list.
            list2:
                Second list.
        """
        return [*list1, *list2]


    @conduitblock.make
    def flatten(*, values : Union[List[Any], ConduitVariable]) -> List[Any]:
        """
        Moves the inner lists' items to the root of the list. Only one depth is supported.

        Args:
            values:
                The list that will be used in the operation. 
        """
        items = []
        for item in values:
            if isinstance(item, list):
                items.extend(item)
            else:
                items.append(item)
        return items


    @conduitblock.make
    def get(*, list : Union[List[Any], ConduitVariable], index : int) -> Any:
        """
        Return the item in the position.

        Args:
            list:
                The list that will be used in the operation.
            index:
                The index of item.
        """
        return list[index]

    
    @conduitblock.make
    def index(*, list : Union[List[Any], ConduitVariable], item : Any) -> int:
        """
        Return the index of the item. Returns -1 if item is not found.

        Args:
            list:
                The list that will be used in the operation.
            item:
                The item that its index will be returned.
        """
        return -1 if item not in list else list.index(item)