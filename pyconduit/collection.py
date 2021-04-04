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

__all__ = ["ExtendedList", "ExtendedDict", "BlocksCollection"]

from collections import UserDict, UserList, OrderedDict
import random
from pyconduit.utils import pattern_match

from typing import Any, Optional, TYPE_CHECKING, List, Tuple, Union

if TYPE_CHECKING:
    from pyconduit import ConduitBlock

class ExtendedList(UserList):
    """
    A list object that based on UserList with additions such as filters
    and queries.
    """
    def find_all(self, func) -> List[Any]:
        """
        Returns all items that func(item) is True.
        If func is None, then returns all items that True.
        """
        return list(filter(func, self.data))

    def find_first(self, func) -> Any:
        """
        Returns the first that func(item) is True.
        If func is None, then returns the first truthy item.
        """
        if func == None:
            next((x for x in self.data if x), None)
        return next((x for x in self.data if func(x)), None)

    def unique(self) -> List[Any]:
        """
        Gets the unique items from the list.
        """
        return list(OrderedDict.fromkeys(self.data))

    def shuffle(self) -> None:
        """
        Shuffles the list in place.
        """
        random.shuffle(self)

    def random(self) -> Any:
        """
        Picks a random item from the list.
        """
        return random.choice(self.data)

    def first(self) -> Any:
        """
        Returns the first item. If list is empty, raises IndexError.
        """
        return self.data[0]

    def last(self) -> Any:
        """
        Returns the last item. If list is empty, raises IndexError.
        """
        return self.data[-1]

    def first_or_default(self, default = None) -> Any:
        """
        Returns the first item. If list is empty, returns the default.
        """
        return self.get(0, default = default)

    def last_or_default(self, default = None) -> Any:
        """
        Returns the last item. If list is empty, returns the default.
        """
        return self.get(-1, default = default)

    def get(self, index, default = None) -> Any:
        """
        Returns the item in specified index, it is same as list[index].
        If index doesn't exists in the list, then returns the default.
        """ 
        try:
            return self.data[index]
        except IndexError:
            return default


class ExtendedDict(UserDict):
    """
    A dict object that based on UserDict with additions such as filters
    and queries.
    """
    def find_all(self, func) -> List[Tuple[Any, Any]]:
        """
        Returns all pairs that func((key, value)) is True.
        If func is None, then returns all pairs that True.
        """
        return list(((k, v) for k, v in self.data.items() if func(k, v)))

    def find_first(self, func) -> Optional[Tuple[Any, Any]]:
        """
        Returns the first pair that func((key, value)) is True.
        If func is None, then returns the first pair that has a truthy value.
        """
        if func == None:
            next(((k, v) for k, v in self.data.items() if v), None)
        return next(((k, v) for k, v in self.data.items() if func(k, v)), None)

    def first(self) -> Tuple[Any, Any]:
        """
        Returns the first pair. If list is empty, raises IndexError.
        """
        return list(self.data.items())[0]

    def last(self) -> Tuple[Any, Any]:
        """
        Returns the last pair. If list is empty, raises IndexError.
        """
        return list(self.data.items())[-1]

    def first_or_default(self, default = None) -> Any:
        """
        Returns the first item. If list is empty, returns the default.
        """
        return ExtendedList(list(self.data.items())).first_or_default(default = default)

    def last_or_default(self, default = None) -> Any:
        """
        Returns the last item. If list is empty, returns the default.
        """
        return ExtendedList(list(self.data.items())).last_or_default(default = default)


class BlocksCollection(ExtendedDict):
    """
    A simple collection that holds ConduitBlocks.
    """
    def match_all(self, pattern : str, strict : bool = True) -> List["ConduitBlock"]:
        """
        Returns a list of ConduitBlocks that matches with the specified wildcard (glob) pattern.
        """
        return [v for k, v in self.data.items() if pattern_match(k.display_name, pattern, strict = strict)]

    def match_first(self, pattern : str, strict : bool = True) -> Optional["ConduitBlock"]:
        """
        Returns the first ConduitBlock that matches with the specified wildcard (glob) pattern.
        """
        next((v for k, v in self.data.items() if pattern_match(k.display_name, pattern, strict = strict)), None)
