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

__all__ = ["ConduitError", "EMPTY", "ConduitIterator"]

from typing import Callable, Generic, List, Any, TYPE_CHECKING, Optional, TypeVar
from pyconduit import ConduitStatus
from multiprocessing import Process

if TYPE_CHECKING:
    from pyconduit.step import ConduitStep

# A custom exception for errors that occurs in Actions.
class ConduitError(Exception):
    """
    ## ConduitError
    A custom exception for errors that occurs in Actions.
    """
    def __init__(self, status : ConduitStatus, step : Optional["ConduitStep"] = None, *args): 
        self.status = status
        self.step = step
        super(ConduitError, self).__init__(status, step, *args)

    @property
    def text(self) -> str:
        return f"{self.status.name} ({self.status.value})" + \
            ("" if not self.step else \
                f"\nStep: {self.step.id} (#{self.step.position})" + \
                f"\nBlock: {self.step.block.display_name}"
            )


class _ConduitProcess(Process):
    """
    It is same as `Process` class but includes few modifications such as executing coroutines.
    """
    async def run_async(self, *args, **kwargs):
        if self._target:
            mtd = await self._target(*args, **kwargs)
            return mtd

    def run(self, *args, **kwargs):
        if self._target:
            return self._target(*args, **kwargs)

    def set_function(self, func : Callable):
        self._target = func


class _Empty:
    def __str__(self) -> str:
        return "Empty"

    def __bool__(self) -> bool:
        return False

    def __repr__(self):
        return "Empty"

    def __len__(self):
        return 0


T = TypeVar('T')


class ConduitIterator(Generic[T]):
    """
    A custom iterator for Conduit steps that supports
    adding new steps while keeping the index.
    """
    def __init__(self, items : List[T]):
        self._items = items or []
        self._seen_items = 0
        self._added_items = 0

    def __iter__(self):
        return self

    def add_item(self, item : T):
        self._items.insert(self._seen_items + self._added_items, item)
        self._added_items += 1

    def __next__(self) -> T:
        self._seen_items += 1
        try:
            return self._items[self._seen_items - 1]
        except IndexError:
            self._seen_items = 0
            self._added_items = 0
            raise StopIteration


EMPTY = _Empty()


class ScopedObject:
    """
    An object that holds a value then allows users to access attributes. 
    But you can change which attributes to read.
    """

    def __init__(self, obj : Any, attributes : List[str] = []) -> None:
        """
        Creates a new ScopedObject.

        Args:
            obj:
                The object will be inserted to the ScopedObject.
            attributes:
                A list of attributes that users can read from the object. Note that it only restricts
                for reading attributes, not for setting attributes.
        """
        self.__object = obj
        self.__attributes = attributes

    def __getattr__(self, name):
        if name.startsiwth("__") or name.endswith("__") or name.startswith("_") or name.endswith("_"):
            raise AttributeError(name)
        if name not in self.__attributes:
            raise AttributeError(name)
        return getattr(self.__object, name)

    def __bool__(self) -> bool:
        return bool(self.__object)

    def __iter__(self):
        return iter(self.__object)