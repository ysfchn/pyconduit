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

class ConduitVariable(ObjectProxy):
    """
    A wrapper of `ObjectProxy` class which comes from [`wrapt`](https://github.com/GrahamDumpleton/wrapt) library.
    It doesn't contain any modifications, just a renamed object especially for pyconduit.

    It is used for Conduit variables, probably you won't need that in your end.
    """


class ConduitStep:
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
    """
    def __init__(
        self, 
        job : "Conduit", 
        block : Union[ConduitBlock, ConduitBlock._Partial], 
        parameters : dict = {}, 
        if_condition : Union[str, List[str], None] = None, 
        id : Optional[str] = None,
        forced : bool = False
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
        """
        self.job = job
        self._position : int = len(self.job.steps) + 1
        # An identifier for the step.
        self.id : str = str(id) if id != None else str(self.position)
        # Forced steps will work even if previous steps fails.
        self.forced : bool = forced
        self.block : Union[ConduitBlock, ConduitBlock._Partial] = block
        self.status : ConduitStatus = ConduitStatus.NONE
        self.refresh_status()
        self.return_value : Any = None
        self.parameters : Dict[str, Any] = parameters
        self.if_condition : Union[str, List[str], None] = if_condition
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
            self.status = ConduitStatus.BLOCK_NOT_FOUND
        elif self.is_id_duplicate:
            self.status = ConduitStatus.DUPLICATE_STEP_IDS
        elif not self.block.exists_tags(self.tags):
            self.status = ConduitStatus.FORBIDDEN_BLOCK
        elif self._get_block_limit(self.block)[0]:
            self.status = ConduitStatus.BLOCK_LIMIT_EXCEED
        elif not self.check_if_condition():
            self.status = ConduitStatus.IF_CONDITION_FAILED
        elif self.step_limit != None and len(self.steps) > self.step_limit:
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
                val = ConduitStep._parse_context_string(data, val.replace(item, ConduitStep._parse_context_tag(data, item)))
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
            if isinstance(self.if_condition, str):
                return True if self._parse_content_all(self.job.contexts, self.if_condition) else False
            else:
                return all([self._parse_content_all(self.job.contexts, x) for x in self.if_condition])
        return True


    def function(self) -> Union[Callable, Coroutine]:
        """
        Returns a custom function with keyword and positional parameters filled.

        Returns:
            The custom function.
        """
        if self.block.is_coroutine:
            async def run():
                return await self.block.function(
                    *self.block.prefill_arguments(self.job, **self.job.global_values), 
                    **self.resolve_references()
                )
            return run
        else:
            def run():
                return self.block.function(
                    *self.block.prefill_arguments(self.job, **self.job.global_values), 
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