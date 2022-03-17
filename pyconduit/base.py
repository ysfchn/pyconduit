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

from abc import ABC, abstractmethod, abstractproperty
from typing import Any, Dict, Generator, Generic, List, Optional, Protocol, Tuple, Type, TypeVar, TYPE_CHECKING, Union, runtime_checkable
from pyconduit.function import FunctionStore, FunctionProtocol
from pyconduit.utils import make_name
from wrapt.wrappers import ObjectProxy
from enum import Enum

T = TypeVar('T')

if TYPE_CHECKING:
    from pyconduit.node import Node
    from pyconduit.job import Job


class _Empty:
    pass


EMPTY = _Empty()


class NodeStatus(Enum):
    # The step has not executed yet.
    NONE = -1
    # Exited without any errors.
    DONE = 0
    # This step has skipped because of previous failed steps.
    SKIPPED = 100
    # All general unexpected errors.
    UNHANDLED_EXCEPTION = 101
    # This action can't found.
    BLOCK_NOT_FOUND = 102
    # Pydantic validation errors.
    INVALID_TYPE = 107
    # If condition failed.
    IF_CONDITION_FAILED = 110
    # Invalid argument has provided for function.
    INVALID_ARGUMENT = 103
    # Conduit killed manually.
    KILLED_MANUALLY = 111


class Category:
    @classmethod
    def get(cls, name : str) -> FunctionProtocol:
        return FunctionStore.get(make_name(cls.__name__, name))

    def __str__(self) -> str:
        return self.__class__.__name__


class Variable(ObjectProxy):
    pass


# A custom exception for errors that occurs in nodes.
class NodeError(Exception):
    def __init__(self, status : NodeStatus, *args): 
        self.status = status
        super(NodeError, self).__init__(status, *args)


class NodeIterator(Generic[T]):
    __slots__ = (
        "items",
        "_seen_items"
    )

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

    def remove_item(self, item : T):
        i = -1
        try:
            i = self.items.index(item)
        except ValueError:
            return
        self.items.remove(item)
        if (self._seen_items >= 1) and (self._seen_items > i):
            self._seen_items -= 1

    def copy(self):
        return NodeIterator(list(self.items))

    def clear(self):
        self.items.clear()
        self._seen_items = 0

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


class NodeBase(ABC):
    @abstractmethod
    def get_contexts(self) -> Dict[str, Any]:
        ...

    @abstractmethod
    def tree(self, indent : int = 0) -> List[str]:
        ...

    @abstractproperty
    def path(self) -> str:
        ...

    @abstractproperty
    def is_root(self) -> bool:
        ...

    @abstractproperty
    def job(self) -> "Job":
        ...

    @abstractproperty
    def contexts(self) -> Dict[str, Any]:
        ...

    @abstractproperty
    def _node_type(self) -> Type["Node"]:
        ...


@runtime_checkable
class NodeLikeProtocol(Protocol):
    nodes : NodeIterator["Node"]


class NodeLike(NodeLikeProtocol):
    def append_node(self, **kwargs) -> "Node":
        n : "Node" = self._node_type(parent = self, **kwargs)
        self.nodes.add_item(n, add_top = False)
        return n

    def remove_node(self, node : "Node"):
        self.nodes.remove_item(node)

    def get_node_by_id(self, id : str, recursive : bool = False) -> Optional["Node"]:
        if recursive:
            return next((x.get_node_by_id(id, recursive) for x in self.nodes.items), None)
        return next((x for x in self.nodes.items if x.id and (x.id == id)), None)

    def get_nodes_by_action(self, action : str, recursive : bool = False) -> List["Node"]:
        if recursive:
            nodes = []
            for x in self.nodes.items:
                nodes.extend(x.get_nodes_by_action(action, recursive))
            return nodes
        else:
            return [x for x in self.nodes.items if (x.action == action)]

    def walk(self) -> Generator[Tuple["Node", Optional[NodeStatus]], None, None]:
        self.nodes = self.nodes.copy()
        for i in self.nodes:
            # Check if block really exists.
            if not i.exists:
                yield i, NodeStatus.BLOCK_NOT_FOUND,
            # Check if condition.
            elif not i.check_if_condition():
                yield i, NodeStatus.IF_CONDITION_FAILED,
            else:
                yield i, None,
                for x, status in i.walk():
                    yield x, status,

    def __len__(self) -> int:
        return len(self.nodes)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} named '{self.__str__()}' with {self.__len__()} node(s)>"