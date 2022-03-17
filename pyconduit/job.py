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

import inspect
from typing import Callable, Dict, Optional, Type, Union, List, Any
from pyconduit.node import Node
from pyconduit.base import NodeError, NodeBase, NodeIterator, NodeLike, NodeStatus

try:
    from pydantic import ValidationError
except (ImportError, ModuleNotFoundError):
    ValidationError = type("ValidationError", (Exception,), {})


class Job(NodeBase, NodeLike):

    __slots__ = (
        "id",
        "name",
        "variables",
        "local_values",
        "global_values",
        "on_step_update",
        "on_job_finish",
        "block_limit_overrides",
        "debug",
        "ctx",
        "nodes",
        "_status",
        "_running",
        "_data_steps",
        "_data_results",
        "_data_status",
        "_data_job",
        "_data_context"
    )

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
        self.ctx : Optional[dict] = ctx
        self.nodes : NodeIterator[Node] = NodeIterator()
        self._status : Optional[bool] = None
        self._running : bool = False
        self._data_steps : dict = {}
        self._data_results : dict = {}
        self._data_status : dict = {}
        self._data_job : dict = {}
        self._data_context : dict = {}


    def tree(self, indent : int = 0) -> List[str]:
        t = []
        t.append(repr(self))
        for k in self.nodes.items:
            t.extend(k.tree(indent))
        return t


    def get_contexts(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "variables": self.variables,
            "ctx": self.ctx,
            "status": self.status,
            "parameters": self.local_values
        }

    def _save_node_result(self, node : Node, value : Any, status : NodeStatus):
        self._data_results.update({node.path: value})
        self._data_status.update({node.path: status})

    def _save_node_contexts(self, node : Node):
        self._data_steps.update({node.path: node.get_contexts()})

    def _save_job_contexts(self):
        self._data_job.update(self.get_contexts())

    def reset(self):
        self._status = None
        self._data_steps.clear()
        self._data_results.clear()
        self._data_job.clear()
        self._data_status.clear()
        self._save_job_contexts()

    async def run(self) -> None:
        failed_step = None
        self.reset()
        self._running = True
        for node, status in self.walk():
            self._save_node_contexts(node)
            # Refresh the contexts (job parameters).
            # If one of previous steps has failed don't execute the next ones.
            if self._status == None or node.forced:
                try:
                    if status:
                        raise NodeError(status)
                    else:
                        func = node.get_callable()
                        if inspect.iscoroutine(func):
                            # Execute the function as coroutine.
                            self._save_node_result(
                                node = node, 
                                value = await func(), 
                                status = NodeStatus.DONE
                            )
                        else:
                            # Execute the function as it is.
                            self._save_node_result(
                                node = node, 
                                value = func(), 
                                status = NodeStatus.DONE
                            )
                except ValueError as vae:
                    if self.debug:
                        raise vae
                    self._save_node_result(
                        node = node, 
                        value = vae if len(vae.args) != 1 else vae.args[0], 
                        status = NodeStatus.INVALID_ARGUMENT
                    )
                except ValidationError as val:
                    self._save_node_result(
                        node = node, 
                        value = val, 
                        status = NodeStatus.INVALID_TYPE
                    )
                except NodeError as act:
                    self._save_node_result(
                        node = node, 
                        value = act, 
                        status = act.status
                    )
                except Exception as e:
                    if self.debug:
                        raise e
                    self._save_node_result(
                        node = node, 
                        value = e, 
                        status = NodeStatus.UNHANDLED_EXCEPTION
                    )
                else:
                    pass
                if node.status not in [NodeStatus.DONE, NodeStatus.IF_CONDITION_FAILED]:
                    failed_step = node
                    self._status = False
            else:
                self._save_node_result(
                    node = node, 
                    value = NodeError(node.status), 
                    status = NodeStatus.SKIPPED
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
        self._running = False
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
    def job(self) -> "Job":
        return self

    @property
    def status(self) -> Optional[bool]:
        return self._status

    @property
    def running(self) -> bool:
        return self._running

    @property
    def path(self) -> str:
        return "/"
    
    @property
    def contexts(self) -> Dict[str, Any]:
        return self._data_job

    @property
    def _node_type(self) -> Type["Node"]:
        return Node

    def __bool__(self) -> bool:
        return bool(self._status)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} nodes={len(self.nodes)} running={self._running} status={self._status}>"