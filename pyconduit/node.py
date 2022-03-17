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

from typing import Any, Callable, Dict, List, Optional, Type, Union, TYPE_CHECKING, get_args, get_origin
from pyconduit.base import Variable, NodeBase, NodeIterator, EMPTY, NodeLike, NodeStatus
from pyconduit.utils import get_node_path, upper, get_key_path
from pyconduit.function import FunctionProtocol, FunctionStore
import re

if TYPE_CHECKING:
    from pyconduit.job import Job


class Node(NodeBase, NodeLike):

    __slots__ = (
        "forced",
        "action",
        "parameters",
        "condition",
        "nodes",
        "_parent",
        "id"
    )

    def __init__(
        self,
        action : str,
        parent : Union["Node", "Job"],
        parameters : dict = {}, 
        condition : Optional[Any] = None, 
        id : Optional[str] = None,
        forced : bool = False,
        ctx : Optional[dict] = None
    ) -> None:
        self.forced : bool = forced
        self.action : str = upper(action)
        self.parameters : Dict[str, Any] = parameters
        self.condition : Optional[Any] = condition
        self.nodes : NodeIterator[Node] = NodeIterator()
        self._parent = parent
        self.id = str(id or ((len(self._parent.nodes.items) + 1)))
        self.ctx = ctx or {}


    def get_function(self) -> Optional[FunctionProtocol]:
        return FunctionStore.get(self.action)


    def check_if_condition(self) -> bool:
        if self.condition != None:
            return self._parse_content_all_bool(self.condition)
        return True


    def tree(self, indent : int = 0) -> List[str]:
        t = []
        t.append(((indent or 0) * " ") + repr(self))
        for k in self.nodes.items:
            t.extend(k.tree((indent or 0) + (indent or 0)))
        return t


    def get_contexts(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "id": self.id,
            "forced": self.forced,
            "ctx": self.ctx,
            "parameters": self.parameters,
            "condition": self.condition
        }


    def resolve_references(self) -> Dict[str, Any]:
        params = {}
        for key, value in self.parameters.items():
            val = self._parse_content_all(value)
            # Check if parameter annotation accepts a Variable. (i.e Union[Variable, list]),
            # if not, then get the actual value of the variable, instead of using the proxy object.
            if isinstance(val, Variable) and (key in self.block.parameters):
                if Variable.__name__ not in str(self.block.parameters[key].annotation):
                    val = val.__wrapped__
            # Save to params.
            params[key] = val
        return params


    def get_callable(self) -> Callable:
        func = self.get_function()
        if func.conduit.is_coroutine:
            async def run():
                r = self.resolve_references()
                func.conduit.validate_params(**r)
                return await func(
                    *func.conduit.prefill_arguments(self), 
                    **r
                )
            return run
        else:
            def run():
                r = self.resolve_references()
                func.conduit.validate_params(**r)
                return func(
                    *func.conduit.prefill_arguments(self), 
                    **r
                )
            return run


    def _parse_content_all(self, value : Any) -> Any:
        if isinstance(value, str):
            return self._parse_context_string(value)
        elif isinstance(value, list):
            return [self._parse_content_all(x) for x in value]
        elif isinstance(value, dict):
            return { self._parse_context_string(x) : self._parse_content_all(y) for x, y in value.items() }
        return value


    def _parse_content_all_bool(self, value : Any) -> bool:
        if isinstance(value, str):
            return bool(self._parse_context_string(value))
        elif isinstance(value, list):
            return all([self._parse_content_all(x) for x in value])
        return bool(value)


    def _parse_context_string(self, value : str) -> Any:
        # Find all context values in string.
        contexts = re.findall("({[<%#:]{1} [\S]+ [%#:>]{1}})", value)
        # If there is no any context values in string,
        # return the string itself.
        if len(contexts) == 0:
            return value
        # If value is just a context value, 
        # return the value of the context item instead of a string.
        if len(contexts) == 1 and value.strip() == contexts[0]:
            return self._parse_context_tag(contexts[0])
        else:
            val = value
            for item in contexts:
                val = self._parse_context_string(val.replace(item, str(self._parse_context_tag(item))))
            return val


    def _parse_context_tag(self, value : str) -> Any:
        # Check if value is in "step result" format.
        # {: key :} 
        if value.startswith("{: ") and value.endswith(" :}") and len(value) > 6:
            return get_key_path(self.job._data_results, self._parse_context_string(value[3:-3]))
        # Check if value is in "job variable" format.
        # {# key #}
        elif value.startswith("{# ") and value.endswith(" #}") and len(value) > 6:
            return get_key_path(self.job._data_job["variables"], self._parse_context_string(value[3:-3]))
        # Check if value is in "job parameter" format.
        # {< key >}
        elif value.startswith("{< ") and value.endswith(" >}") and len(value) > 6:
            return get_key_path(self.job._data_job["parameters"], self._parse_context_string(value[3:-3]))
        # Check if value is plain key path format.
        # {% key %}
        elif value.startswith("{% ") and value.endswith(" %}") and len(value) > 6:
            return get_node_path(self, self._parse_context_string(value[3:-3]))
        return value

    @property
    def is_root(self) -> bool:
        return False

    @property
    def job(self) -> "Job":
        return self._parent.job

    @property
    def position(self) -> int:
        return (self._parent.nodes.items.index(self) + 1)

    @property
    def parent(self) -> Union["Node", "Job"]:
        return self._parent

    @property
    def exists(self) -> bool:
        return self.action in FunctionStore.functions

    @property
    def path(self) -> str:
        return self._parent.path.removesuffix("/") + "/" + self.id

    @property
    def return_value(self) -> Any:
        return self._parent.job._data_results.get(self.path, EMPTY)

    @property
    def status(self) -> NodeStatus:
        return self._parent.job._data_status.get(self.path, NodeStatus.NONE)

    @property
    def contexts(self) -> Dict[str, Any]:
        return self._parent.job._data_steps.get(self.path) or {}

    @property
    def _node_type(self) -> Type["Node"]:
        return self.__class__

    @property
    def ctx(self) -> dict:
        return self._parent.job._data_context.get(self.path, {})

    @ctx.setter
    def ctx(self, value) -> None:
        self._parent.job._data_context[self.path] = value

    def __bool__(self) -> bool:
        return bool(self.nodes)

    def __str__(self) -> str:
        return self.action

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} action={self.action} nodes={len(self.nodes)} id={self.id} path={self.path}>"