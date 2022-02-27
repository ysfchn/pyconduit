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

from typing import Any, Dict, Generator, Generic, List, Optional, Tuple, TypeVar, TYPE_CHECKING, Union
from pyconduit.enums import ConduitStatus
from pyconduit.function import FunctionStore, FunctionProtocol
from pyconduit.utils import make_name
from wrapt.wrappers import ObjectProxy

T = TypeVar('T')

if TYPE_CHECKING:
    from pyconduit.node import Node
    from pyconduit.job import Job

class _Empty:
    pass

EMPTY = _Empty()

class Category:
    @classmethod
    def get(cls, name : str) -> FunctionProtocol:
        return FunctionStore.get(make_name(cls.__name__, name))

    def __str__(self) -> str:
        return self.__class__.__name__


class ConduitVariable(ObjectProxy):
    pass


# A custom exception for errors that occurs in Actions.
class ConduitError(Exception):

    def __init__(self, status : ConduitStatus, *args): 
        self.status = status
        super(ConduitError, self).__init__(status, *args)

    @property
    def text(self) -> str:
        return f"{self.status.name} ({self.status.value})"

    def format_step(self, step : "Node"):
        return \
            self.text + "\n" + \
            step.action


class NodeIterator(Generic[T]):

    def __init__(self, items : Optional[List[T]] = None):
        self.items = items or []
        self._seen_items = 0

    def add_item(self, item : T, add_top : bool = True):
        if add_top:
            self.items.insert(self._seen_items, item)
        else:
            self.items.append(item)

    def add_items(self, items : List[T], add_top : bool = True):
        if add_top:
            for i, item in enumerate(items):
                self.items.insert(self._seen_items + i, item)
        else:
            self.items.extend(items)

    def copy(self):
        return NodeIterator(list(self.items))

    def __iter__(self):
        return self

    def __len__(self):
        return len(self.items)

    def __bool__(self):
        return bool(self.items)

    def __next__(self) -> T:
        self._seen_items += 1
        try:
            return self.items[self._seen_items - 1]
        except IndexError:
            self._seen_items = 0
            raise StopIteration


class NodeBase:

    def _append_node(self, clss, **kwargs):
        n = clss(parent = self, **kwargs)
        self.nodes.add_item(n, add_top = False)
        return n

    def get_node_by_id(self, id : str, recursive : bool = False) -> Optional["Node"]:
        if recursive:
            return next((x.get_node_by_id(id, recursive) for x in self.nodes.copy()), None)
        return next((x for x in self.nodes.copy() if x.id and (x.id == id)), None)

    def get_nodes_by_action(self, action : str, recursive : bool = False) -> List["Node"]:
        if recursive:
            nodes = []
            for x in self.nodes.copy():
                nodes.extend(x.get_nodes_by_action(action, recursive))
            return nodes
        else:
            return [x for x in self.nodes.copy() if (x.action == action)]

    def contexts(self) -> Dict[str, Any]:
        pass

    def tree(self) -> List[str]:
        pass

    def walk(self) -> Generator[Tuple["Node", Optional[ConduitStatus]], None, None]:
        for i in self.nodes.copy():
            # Check if block really exists.
            if not i.exists:
                yield i, ConduitStatus.BLOCK_NOT_FOUND,
            # Check if condition.
            if not i.check_if_condition(self.job._live_contexts):
                yield i, ConduitStatus.IF_CONDITION_FAILED,
            else:
                yield i, None,
                for x, status in i.walk():
                    yield x, status,

    @property
    def is_root(self) -> bool:
        return False

    @property
    def job(self) -> "Job":
        if self.is_root:
            return self
        return self._parent.job

    def __len__(self) -> int:
        return len(self.nodes)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} named '{self.__str__()}' with {self.__len__()} node(s)>"