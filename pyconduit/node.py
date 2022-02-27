# MIT License
# 
# Copyright (c) 2022 Yusuf Cihan
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

from typing import Any, Callable, Dict, List, Optional, Union, TYPE_CHECKING, get_args, get_origin
from pyconduit.enums import ConduitStatus
from pyconduit.base import ConduitVariable, NodeBase, NodeIterator
from pyconduit.utils import upper, get_key_path
from pyconduit.function import FunctionProtocol, FunctionStore
import re

if TYPE_CHECKING:
    from pyconduit.job import Job


class Node(NodeBase):

    def __init__(
        self,
        action : str,
        parent : Union["Node", "Job"],
        parameters : dict = {}, 
        condition : Optional[Any] = None, 
        id : Optional[str] = None,
        forced : bool = False,
        ctx : Optional[Dict[str, Any]] = None
    ) -> None:
        self.id = id or None
        self.forced : bool = forced
        self.action : str = upper(action)
        self.status : ConduitStatus = ConduitStatus.NONE
        self.return_value : Any = None
        self.parameters : Dict[str, Any] = parameters
        self.condition : Optional[Any] = condition
        self.ctx : Dict[str, Any] = ctx or {}
        self.nodes : NodeIterator[Node] = NodeIterator()
        self._parent = parent


    def get_function(self) -> Optional[FunctionProtocol]:
        return FunctionStore.get(self.action)


    def check_if_condition(self) -> bool:
        if self.condition != None:
            return self._parse_content_all_bool(self.job._contexts, self.condition)
        return True


    def append_node(self, **kwargs):
        return super()._append_node(Node, **kwargs)


    def tree(self, indent : int = 0) -> List[str]:
        t = []
        t.append(((indent or 0) * " ") + self.action + " #" + str(self.position))
        for k in self.nodes.copy():
            t.extend(k.tree((indent or 0) + 2))
        return t


    def contexts(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "id": self.id,
            "forced": self.forced,
            "ctx": self.ctx,
            "parameters": self.parameters,
            "condition": self.condition,
            "nodes": [x.contexts() for x in self.nodes.copy()]
        }


    def resolve_references(self) -> Dict[str, Any]:
        params = {}
        for key, value in self.parameters.items():
            val = self._parse_content_all(self.job.contexts, value)
            # Check if Union parameter annotation accepts a ConduitVariable. (i.e Union[ConduitVariable, list])
            if isinstance(val, ConduitVariable) and key in self.block.parameters:
                is_union = get_origin(self.block.parameters[key].annotation) is Union
                is_variable_accepted = False if not is_union else ConduitVariable in get_args(self.block.parameters[key].annotation)
                if not is_variable_accepted:
                    val = val.__wrapped__
            # Save to params.
            params[key] = val
        return params


    def get_callable(self) -> Callable:
        func = self.get_function()
        if func.conduit.is_coroutine:
            async def run():
                return await func(
                    *func.conduit.prefill_arguments(self), 
                    **self.resolve_references()
                )
            return run
        else:
            def run():
                return func(
                    *func.conduit.prefill_arguments(self), 
                    **self.resolve_references()
                )
            return run


    @staticmethod
    def _parse_content_all(data : dict, value : Any) -> Any:
        if isinstance(value, str):
            return Node._parse_context_string(data, value)
        elif isinstance(value, list):
            return [Node._parse_content_all(data, x) for x in value]
        elif isinstance(value, dict):
            return { Node._parse_context_string(data, x) : Node._parse_content_all(data, y) for x, y in value.items() }
        return value


    @staticmethod
    def _parse_content_all_bool(data : dict, value : Any) -> bool:
        if isinstance(value, str):
            return bool(Node._parse_context_string(data, value))
        elif isinstance(value, list):
            return all([Node._parse_content_all(data, x) for x in value])
        return bool(value)


    @staticmethod
    def _parse_context_string(data : dict, value : str) -> Any:
        # Find all context values in string.
        contexts = re.findall("({[<%#:]{1} [\S]+ [%#:>]{1}})", value)
        # If there is no any context values in string,
        # return the string itself.
        if len(contexts) == 0:
            return value
        # If value is just a context value, 
        # return the value of the context item instead of a string.
        if len(contexts) == 1 and value.strip() == contexts[0]:
            return Node._parse_context_tag(data, contexts[0])
        else:
            val = value
            for item in contexts:
                val = Node._parse_context_string(data, val.replace(item, str(Node._parse_context_tag(data, item))))
            return val


    @staticmethod
    def _parse_context_tag(data : dict, value : str) -> Any:
        # Check if value is in "step result" format.
        # {: key :} 
        if value.startswith("{: ") and value.endswith(" :}") and len(value) > 6:
            step, *keys = Node._parse_context_string(data, value[3:-3]).split(".")
            return get_key_path(data["steps"], step + ".result" + ("." if keys else "") + ".".join(keys))
        # Check if value is in "job variable" format.
        # {# key #}
        elif value.startswith("{# ") and value.endswith(" #}") and len(value) > 6:
            return get_key_path(data["job"]["variables"], Node._parse_context_string(data, value[3:-3]))
        # Check if value is in "job parameter" format.
        # {< key >}
        elif value.startswith("{< ") and value.endswith(" >}") and len(value) > 6:
            return get_key_path(data["job"]["parameters"], Node._parse_context_string(data, value[3:-3]))
        # Check if value is plain key path format.
        # {% key %}
        elif value.startswith("{% ") and value.endswith(" %}") and len(value) > 6:
            return get_key_path(data, Node._parse_context_string(data, value[3:-3]))
        return value


    @property
    def position(self) -> int:
        return (self._parent.nodes.items.index(self) + 1)

    @property
    def parent(self) -> Union["Node", "Job"]:
        return self._parent

    @property
    def job(self) -> "Job":
        if self.is_root:
            return self
        return self._parent.job

    def __bool__(self) -> bool:
        return bool(self.nodes)

    def __str__(self) -> str:
        return self.action