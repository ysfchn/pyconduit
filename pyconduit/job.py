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

import inspect
from typing import Callable, Dict, Optional, Union, List, Any
from pyconduit.node import Node
from pyconduit.base import ConduitError, NodeBase, NodeIterator
from pyconduit.enums import ConduitStatus

try:
    from pydantic import ValidationError
except (ImportError, ModuleNotFoundError):
    ValidationError = type("ValidationError", (Exception,), {})


class Job(NodeBase):

    def __init__(
        self,
        id : Optional[str] = None, 
        name : Optional[str] = None,
        variables : Optional[dict] = {},
        local_values : Optional[dict] = {},
        global_values : Optional[dict] = {},
        on_step_update : Union[Callable, None] = None,
        on_job_finish : Union[Callable, None] = None,
        block_limit_overrides : Optional[Dict[str, Optional[int]]] = None,
        debug : bool = False,
        ctx : Optional[dict] = None
    ) -> None:
        self.id = id
        self.name = name
        self.variables = variables or {}
        self.local_values = local_values or {}
        self.global_values = global_values or {}
        self.on_step_update = on_step_update
        self.on_job_finish = on_job_finish
        self.block_limit_overrides = block_limit_overrides or {}
        self.debug = debug
        self.ctx = ctx or {}
        self.nodes : NodeIterator[Node] = NodeIterator()
        self._status : Optional[bool] = None
        self._running : bool = False
        self._live_contexts : dict = {}


    def append_node(self, **kwargs):
        return super()._append_node(Node, **kwargs)


    def tree(self) -> List[str]:
        t = []
        t.append(self.name or "Unnamed Conduit")
        for k in self.nodes.copy():
            t.extend(k.tree(2))
        return t


    def contexts(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "variables": self.variables,
            "ctx": self.ctx,
            "status": self.status,
            "parameters": self.local_values
        }

    
    def _record_result(self, node : Node, result : Any, status : ConduitStatus):
        self._live_contexts["results"][node.path] = {"value": result, "status": status}


    async def run(self) -> None:
        failed_step = None
        self._status = None
        self._live_contexts = {"job": self.contexts(), "results": {}, "steps": {}}
        for node, status in self.walk():
            self._live_contexts["steps"][node.path] = node.contexts()
            # Refresh the contexts (job parameters).
            # If one of previous steps has failed don't execute the next ones.
            if self._status == None or node.forced:
                try:
                    if status:
                        raise ConduitError(status)
                    else:
                        func = node.get_callable()
                        if inspect.iscoroutine(func):
                            # Execute the function as coroutine.
                            self._record_result(
                                node = node, 
                                value = await func(), 
                                status = ConduitStatus.DONE
                            )
                        else:
                            # Execute the function as it is.
                            self._record_result(
                                node = node, 
                                value = func(), 
                                status = ConduitStatus.DONE
                            )
                except ValueError as vae:
                    self._record_result(
                        node = node, 
                        value = vae if len(vae.args) != 1 else vae.args[0], 
                        status = ConduitStatus.INVALID_ARGUMENT
                    )
                except ValidationError as val:
                    self._record_result(
                        node = node, 
                        value = val, 
                        status = ConduitStatus.INVALID_TYPE
                    )
                except ConduitError as act:
                    self._record_result(
                        node = node, 
                        value = act.format_step(node), 
                        status = act.status
                    )
                except Exception as e:
                    self._record_result(
                        node = node, 
                        value = e, 
                        status = ConduitStatus.UNHANDLED_EXCEPTION
                    )
                else:
                    pass
                if self._live_contexts["results"][node.path] not in [ConduitStatus.DONE, ConduitStatus.IF_CONDITION_FAILED]:
                    failed_step = node
                    self._status = False
            else:
                self._record_result(
                    node = node, 
                    value = ConduitError(node.status).format_step(node), 
                    status = ConduitStatus.SKIPPED
                )
            # Run the listener if exists.
            if self.on_step_update:
                if inspect.iscoroutinefunction(self.on_step_update):
                    await self.on_step_update(self, node)
                else:
                    self.on_step_update(self, node)
        # If there are no any errors in the jobs, set the success to True.
        if self.status == None:
            self._status = True
        # Run the listener if exists.
        if self.on_job_finish:
            if inspect.iscoroutinefunction(self.on_job_finish):
                await self.on_job_finish(self, failed_step)
            else:
                self.on_job_finish(self, failed_step)

    @property
    def is_root(self) -> bool:
        return True

    @property
    def status(self) -> Optional[bool]:
        return self._status

    @property
    def running(self) -> bool:
        return self._running

    @property
    def path(self) -> str:
        return ""

    def __bool__(self) -> bool:
        return bool(self._status)

    def __str__(self) -> str:
        return self.name