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

__all__ = ["ConduitVariable", "ConduitStep"]

from typing import Any, Callable, Coroutine, Dict, List, Union, Optional
from typing_extensions import get_origin, get_args
from pyconduit import ConduitBlock, ConduitStatus
from wrapt.wrappers import ObjectProxy
from pyconduit.utils import get_key_path
import re

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyconduit import Conduit


@ConduitBlock.make(private = True)
def debug(**kwargs):
    print(kwargs)


class ConduitVariable(ObjectProxy):
    """
    A wrapper of `ObjectProxy` class which comes from [`wrapt`](https://github.com/GrahamDumpleton/wrapt) library.
    It doesn't contain any modifications, just a renamed object especially for pyconduit.

    It is used for Conduit variables, probably you won't need that in your end.
    """


class ConduitStep:
    DEFAULT_ROUTE_NAME = "default"
    DEBUG_BLOCK : ConduitBlock = debug

    """
    Represents a single step that is in the job.

    Every step is connected to a specific function. When a step starts running, it executes the function internally.
    Steps also hold variables to track the execution progress of the function such as return values, statuses.

    Steps can be created with `create_step()` in [`Conduit`][pyconduit.conduit.Conduit] objects, 
    but you can create a this object manually by providing a existing `Conduit` object.

    Note:
        Creating a step with same ID is not allowed. However, you will not get any exception as steps are designed to
        be defined by users. When you run the job, it will result in `DUPLICATE_STEP_IDS` status code.

    Attributes:
        job (pyconduit.conduit.Conduit):
            An [`Conduit`][pyconduit.conduit.Conduit] object that this step has added / attached to.
        block:
            An [`ConduitBlock`][pyconduit.block.ConduitBlock] object to specify which block will be executed.
        parameters:
            A dictionary of parameters that will be passed to this block as keyword parameters.
        id (str):
            An identifier for this step. It is unique among all other steps in the job. If no any ID provided when creating
            the step, then the position of the step will be set as step ID.
        forced:
            Specifies if this step must be executed even if one (or more) of the previous steps fails. Defaults to `False`.
        if_condition:
            A list or string of if conditions that contains context values. These conditions will be checked before block executing starts,
            so if one (or more) of conditions fails, then the step will not be executed.
        status:
            It is used to store the status of step.
        return_value:
            The value that returned after executing the step. If step is not executed yet, this will be `None`.
        attach:
            If True, this step will be appended to given job's steps automatically. If False, this step won't be added to
            job. In this case you need to call `job.steps.append(step)` manually. Lastly, if None (which is default), this step will be
            automatically added to current running job's steps (instead of pre-run job steps). If job is not running, behaves same as True.
        ctx:
            Any extra value for this step.
        routes:
            Routes are inner steps that added under this step. When a route has activated, its inner steps are appended to
            current running job's steps.
        route_checks:
            A mapping of route names and conditions for enabling a route automatically.
    """
    def __init__(
        self, 
        job : "Conduit", 
        block : Union[ConduitBlock, ConduitBlock._Partial], 
        parameters : dict = {}, 
        if_condition : Optional[Any] = None, 
        id : Optional[str] = None,
        forced : bool = False,
        attach : Optional[bool] = None,
        ctx : Optional[Any] = None,
        routes : Optional[Dict[str, List["ConduitStep"]]] = None,
        route_checks : Optional[Dict[str, Union[List[str], str]]] = None
    ) -> None:
        """
        Args:
            job (pyconduit.conduit.Conduit):
                An [`Conduit`][pyconduit.conduit.Conduit] object that this step will added / attached to. 
            block:
                An [`ConduitBlock`][pyconduit.block.ConduitBlock] object to specify which block will be executed.
            parameters:
                A dictionary of parameters that will be passed to this block as keyword parameters.
            id:
                An identifier for this step. It needs to be unique among all other steps in the job. If it is `None`, then
                the position of the step will be used as step ID.
            forced:
                Specifies if this step must be executed even if one (or more) of the previous steps fails. Defaults to `False`.
            if_condition:
                A list or string of if conditions that contains context values. These conditions will be checked before block executing starts,
                so if one (or more) of conditions fails, then the step will not be executed.
            attach:
                If True, this step will be appended to given job's steps automatically. If False, this step won't be added to
                job. In this case you need to call `job.steps.append(step)` manually. Lastly, if None (which is default), this step will be
                automatically added to current running job's steps (instead of pre-run job steps). If job is not running, behaves same as True.
            ctx:
                Any extra value for this step.
            routes:
                Routes are inner steps that added under this step. When a route has activated, its inner steps are appended to
                current running job's steps.
            route_checks:
                A mapping of route names and conditions for enabling a route automatically.
        """
        self.job = job
        self._position : int = len(self.job.steps) + 1
        # An identifier for the step.
        self.id : str = str(id) if id != None else str(self.position)
        # Forced steps will work even if previous steps fails.
        self.forced : bool = forced
        self.block : Union[ConduitBlock, ConduitBlock._Partial] = block
        self.status : ConduitStatus = ConduitStatus.NONE
        self.return_value : Any = None
        self.parameters : Dict[str, Any] = parameters
        self.if_condition : Optional[Any] = if_condition
        self.ctx : Optional[Any] = ctx
        self.routes : Dict[str, List["ConduitStep"]] = routes or {}
        self.route_checks : Optional[Dict[str, Union[List[str], str]]] = route_checks
        self.refresh_status()
        if (attach == None) and (self.job.running):
            self.job._steps_iterator.add_item(self)
        elif attach == False:
            pass
        else:
            self.job.steps.append(self)


    @property
    def position(self) -> int:
        """
        Returns the position of this step in job. Position index starts with 1.

        Returns:
            An integer which represents the position index.
        """
        return self._position

    
    def refresh_status(self) -> None:
        """
        Checks for errors and updates the step's status.
        """
        if not self.block:
            if not self.job.debug:
                self.status = ConduitStatus.BLOCK_NOT_FOUND
            else:
                self.parameters["__block"] = self.block.display_name
                self.block = ConduitStep.DEBUG_BLOCK
        elif self.is_id_duplicate:
            self.status = ConduitStatus.DUPLICATE_STEP_IDS
        elif not self.block.exists_tags(self.job.tags):
            self.status = ConduitStatus.FORBIDDEN_BLOCK
        elif self.job._get_block_limit(self.block)[0]:
            self.status = ConduitStatus.BLOCK_LIMIT_EXCEED
        elif self.job.step_limit != None and len(self.job.steps) > self.job.step_limit:
            self.status = ConduitStatus.STEP_LIMIT_EXCEED
        else:
            self.status = ConduitStatus.NONE


    def resolve_references(self) -> Dict[str, Any]:
        """
        Returns the step parameters and converts the variable references to their values.

        Returns:
            A dictionary that contains step parameters with resolved context values.
        """
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


    def activate_router(self, name : Optional[str] = None) -> None:
        """
        Appends all steps to current running job in specified route name.
        """
        n = name or self.DEFAULT_ROUTE_NAME
        if n not in self.routes:
            raise KeyError(f"Route '{name}' couldn't found.")
        if not self.job.running:
            raise ValueError("A route can't be activated when job is not running.")
        self.job._steps_iterator.add_items(self.routes[n])


    @staticmethod
    def _parse_content_all(data : dict, value : Any) -> Any:
        """
        Parses all context values in the "value" parameter.
        If "value" parameter is a list or dictionary that holds multiple values, then every item will be
        parsed with this method recursively.

        ["{% job.variables.foo %}", "{% job.variables.bar %}"] -> [..., ...]
        "{% job.variables.foo %}" -> ...
        """
        if isinstance(value, str):
            return ConduitStep._parse_context_string(data, value)
        elif isinstance(value, list):
            return [ConduitStep._parse_content_all(data, x) for x in value]
        elif isinstance(value, dict):
            return { ConduitStep._parse_context_string(data, x) : ConduitStep._parse_content_all(data, y) for x, y in value.items() }
        return value


    @staticmethod
    def _parse_content_all_bool(data : dict, value : Any) -> bool:
        """
        Like `parse_content_all()` but returns a boolean value instead.
        """
        if isinstance(value, str):
            return bool(ConduitStep._parse_context_string(data, value))
        elif isinstance(value, list):
            return all([ConduitStep._parse_content_all(data, x) for x in value])
        return bool(value)


    @staticmethod
    def _parse_context_string(data : dict, value : str) -> Any:
        """
        Parses a single context value.

        "{% job.variables.foo %}" -> ...
        """
        # Find all context values in string.
        contexts = re.findall("({[<%#:]{1} [\S]+ [%#:>]{1}})", value)
        # If there is no any context values in string,
        # return the string itself.
        if len(contexts) == 0:
            return value
        # If value is just a context value, 
        # return the value of the context item instead of a string.
        if len(contexts) == 1 and value.strip() == contexts[0]:
            return ConduitStep._parse_context_tag(data, contexts[0])
        else:
            val = value
            for item in contexts:
                val = ConduitStep._parse_context_string(data, val.replace(item, str(ConduitStep._parse_context_tag(data, item))))
            return val

    
    @staticmethod
    def _parse_context_tag(data : dict, value : str) -> Any:
        # Check if value is in "step result" format.
        # {: key :} 
        if value.startswith("{: ") and value.endswith(" :}") and len(value) > 6:
            step, *keys = ConduitStep._parse_context_string(data, value[3:-3]).split(".")
            return get_key_path(data["steps"], step + ".result" + ("." if keys else "") + ".".join(keys))
        # Check if value is in "job variable" format.
        # {# key #}
        elif value.startswith("{# ") and value.endswith(" #}") and len(value) > 6:
            return get_key_path(data["job"]["variables"], ConduitStep._parse_context_string(data, value[3:-3]))
        # Check if value is in "job parameter" format.
        # {< key >}
        elif value.startswith("{< ") and value.endswith(" >}") and len(value) > 6:
            return get_key_path(data["job"]["parameters"], ConduitStep._parse_context_string(data, value[3:-3]))
        # Check if value is plain key path format.
        # {% key %}
        elif value.startswith("{% ") and value.endswith(" %}") and len(value) > 6:
            return get_key_path(data, ConduitStep._parse_context_string(data, value[3:-3]))
        return value


    def check_if_condition(self) -> bool:
        """
        Checks if all if conditions passes that defined in `if_condition` attribute.

        Returns:
            `True` if all conditions has passed, `False` otherwise.
        """
        if self.if_condition != None:
            return self._parse_content_all_bool(self.job.contexts, self.if_condition)
        return True


    def get_valid_route(self) -> Optional[str]:
        """
        Checks for all route checks and gets the first name of the passed route.
        """
        if self.route_checks == None:
            return None
        for k, v in self.route_checks.items():
            if self._parse_content_all_bool(self.job.contexts, v):
                return k


    def function(self) -> Union[Callable, Coroutine]:
        """
        Returns a custom function with keyword and positional parameters filled.

        Returns:
            The custom function.
        """
        if self.block.is_coroutine:
            async def run():
                return await self.block.function(
                    *self.block.prefill_arguments(self), 
                    **self.resolve_references()
                )
            return run
        else:
            def run():
                return self.block.function(
                    *self.block.prefill_arguments(self), 
                    **self.resolve_references()
                )
            return run


    # Every step needs to have own unique ID,
    # so this method checks if the new step ID has used before.
    @property
    def is_id_duplicate(self) -> bool:
        """
        Check if the new step ID has used before.

        Returns:
            `True` if step ID has used more than once, `False` otherwise.
        """
        for step in self.job.steps:
            if (step.id == self.id) and (step != self):
                return True
        return False
    
    def __bool__(self) -> bool:
        return bool(self.block)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} for {self.block.display_name} in '{str(self.job)}'>"

    def __str__(self) -> str:
        return self.id