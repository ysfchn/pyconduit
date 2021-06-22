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

__all__ = ["Conduit"]

import inspect
from typing import Coroutine, Iterator, List, Dict, Optional, Union, Any, Callable, Tuple
from pyconduit import ConduitError
from pyconduit import ConduitStatus
from pyconduit import ConduitStep, ConduitVariable
from pyconduit import ConduitBlock
from pyconduit.other import _ConduitProcess
from pyconduit.utils import pattern_match
import asyncio

try:
    from pydantic import ValidationError
except (ImportError, ModuleNotFoundError):
    ValidationError = type("ValidationError", (Exception,), {})


class Conduit:
    """
    Conduits are "job" objects that holds steps and executes them one by one. 
    
    If you want to create a new job, just create a new instance of this `Conduit` object.
    To create new steps, use `create_step()` or initialize `ConduitStep` objects.
    Lastly, to execute all steps, call the `run()` coroutine. 

    Attributes:
        id:
            An ID that used to identify the job. It doesn't have any effect in code, so it doesn't matter which ID you passed.
        name:
            A name that used to identify the job. It doesn't have any effect in code, so it doesn't matter which name you passed.
        steps:
            List of [`ConduitStep`][pyconduit.step.ConduitStep] that added to this job.
        tags:
            A list of tags that this job has. Tags can be useful to limit the availability to blocks. If you add a tag to a
            [`ConduitBlock`][pyconduit.block.ConduitBlock], only jobs has the tag wil able to use that block. For example,
            if a block has "A" and "B" tags, then the job must have both "A" and "B" tags too (if job has extra tags such as "C",
            it doesn't affect the result of the tag checking operation), otherwise using that block will result in a `FORBIDDEN_BLOCK` status code.
        variables:
            A dictionary that contains the job variables. Variables can be set by client or server. They can be accessed 
            inside steps. Note that as these values can be read and edited with users, don't pass any sensitive information here.
            It is just for creating a temporary storage so user can add and edit any value that they wants.
        local_values:
            A dictionary that contains the job parameters. These local values can be used to store any data that came from an
            any source. For example if this job has created automatically with one of your app's events, then you can pass the event
            data here, so users will able to access this value. It is like `variables`, however `local_values` is read only to users. 
        global_values:
            A dictionary that contains the job globals. Global values work same as `variables` and `local_values`, but globals can't be
            seen by users. Unlike `variables` and `local_values`, globals are passed as private function parameters. For example,
            if a block requires an object as parameter which can't be created by users (For example: You created a block that adds a value to your
            own app's database, so this operation will require a database instance object to call "write" method on it. 
            But it is impossible to provide a database instance object for user, so need to provide these objects as global value.)
        on_step_update:
            A callable that will be executed when any step in this job has finished (fail or success).
            It will call the method with two parameters: the Conduit object itself, and step which is updated.
        on_job_finish:
            A callable that will be executed when all steps in this job has finished (fail or success).
            It will call the method with two parameters: the Conduit object itself, and failed step. If there is no any failed step, then failed step will be None.
        step_limit:
            If you want to add a maximum number to the step count, you can set it here. Users will still able to create steps even if they
            exceed the limit, however when job has executed, it will exit with an code that says step limit has exceeded. `None` (which is default)
            means unlimited count of steps.
        block_limit_overrides:
            If you want to override "max_uses" count of [`ConduitBlock`][pyconduit.block.ConduitBlock] objects only for this conduit, you can write block names and set a new limit.
    """

    def __init__(
        self, 
        id : Optional[str] = None, 
        name : Optional[str] = None,
        tags : List[str] = [],
        variables : Dict[str, Any] = {},
        local_values : Dict[str, Any] = {},
        global_values : Dict[str, Any] = {},
        on_step_update : Union[Coroutine, Callable, None] = None,
        on_job_finish : Union[Coroutine, Callable, None] = None,
        step_limit : Optional[int] = None,
        block_limit_overrides : Dict[str, Optional[int]] = {}
    ) -> None:
        """
        Args:
            id:
                An ID that used to identify the job. It doesn't have any effect in code, so it doesn't matter which ID you passed.
            name:
                A name that used to identify the job. It doesn't have any effect in code, so it doesn't matter which name you passed.
            tags:
                A list of tags that this job has. Tags can be useful to limit the availability to blocks. If you add a tag to a
                [`ConduitBlock`][pyconduit.block.ConduitBlock], only jobs has the tag wil able to use that block. For example,
                if a block has "A" and "B" tags, then the job must have both "A" and "B" tags too (if job has extra tags such as "C",
                it doesn't affect the result of the tag checking operation), otherwise using that block will result in a `FORBIDDEN_BLOCK` status code.
            variables:
                A dictionary that contains the job variables. Variables can be set by client or server. They can be accessed 
                inside steps. Note that as these values can be read and edited with users, don't pass any sensitive information here.
                It is just for creating a temporary storage so user can add and edit any value that they wants.
            local_values:
                A dictionary that contains the job parameters. These local values can be used to store any data that came from an
                any source. For example if this job has created automatically with one of your app's events, then you can pass the event
                data here, so users will able to access this value. It is like `variables`, however `local_values` is read only to users. 
            global_values:
                A dictionary that contains the job globals. Global values work same as `variables` and `local_values`, but globals can't be
                seen by users. Unlike `variables` and `local_values`, globals are passed as private function parameters. For example,
                if a block requires an object as parameter which can't be created by users (For example: You created a block that adds a value to your
                own app's database, so this operation will require a database instance object to call "write" method on it. 
                But it is impossible to provide a database instance object for user, so need to provide these objects as global value.)
            on_step_update:
                A callable that will be executed when any step in this job has finished (fail or success).
                It will call the method with two parameters: the Conduit object itself, and step which is updated.
            on_job_finish:
                A callable that will be executed when all steps in this job has finished (fail or success).
                It will call the method with two parameters: the Conduit object itself, and failed step. If there is no any failed step, then failed step will be None.
            step_limit:
                If you want to add a maximum number to the step count, you can set it here. Users will still able to create steps even if they
                exceed the limit, however when job has executed, it will exit with an code that says step limit has exceeded. `None` (which is default)
                means unlimited count of steps.
            block_limit_overrides:
                If you want to override "max_uses" count of ConduitBlock objects only for this conduit, 
                you can write block names and set a new limit. You can also use "*" (wildcard) and "?" (question marks).
        """
        self.id : Optional[str] = id
        self.name : Optional[str]  = name
        # Steps of the job. They will be executed step by step.
        # When one of the step fails, next steps won't run.
        self.steps : List[ConduitStep] = []
        # Globals contains parameters that will be passed into the blocks.
        # For example, an ConduitBlock can want for Conduit object to do specific operation with it.
        # Globals are hidden from user as it may contain sentitive information.
        self.global_values : Dict[str, Any] = global_values
        # Local values are extra parameters that passed in this job.
        # It is like self.global_values but this value is public for users and filled by the bot itself.
        # Users can get value from this dictionary by using contexts.
        self.local_values : Dict[str, Any] = local_values
        # A callable that will be executed after every step.
        self.on_step_update : Union[Coroutine, Callable, None] = on_step_update
        # A callable that will be executed when all steps finished.
        self.on_job_finish : Union[Coroutine, Callable, None] = on_job_finish
        # Contexts.
        self.tags : List[str] = tags
        # None if this job has never executed.
        # True if last step was success, False otherwise.
        self._success : Optional[bool] = None
        self.step_limit : Optional[int] = step_limit
        # Variables are values that passed in this job.
        # It is like self.global_values but this value is public for users.
        # It can be edited and read, users can also use "Variable" blocks to create variables in runtime.
        self.variables : Dict[str, ConduitVariable] = {x : (y if isinstance(y, ConduitVariable) else ConduitVariable(y)) for x, y in variables.items()}
        self.block_limit_overrides : Dict[str, Optional[int]] = block_limit_overrides
        self._contexts : Dict[str, Any] = {}
        self.update_contexts()

    
    @property
    def success(self) -> Optional[bool]:
        """
        Returns a boolean about previous execution has exited without any errors.
        
        Returns:
            `True` if previous execution has exited without any errors. 
            `False` if previous execution has exited with any errors.
            `None` if job has never executed yet. 
        """
        return self._success

    
    @classmethod
    def from_dict(cls, data : Dict[str, Any]) -> "Conduit":
        """
        Creates a new Conduit from dictionary.

        Args:
            data:
                A dictionary that contains configuration for creating new Conduit.
                Available keys and values are same with `__init__` method.

        Returns:
            Returns the created Conduit.
        """
        _conduit = cls(
            id = data.get("id"),
            name = data.get("name"),
            tags = data.get("tags", []),
            variables = data.get("variables", {}),
            local_values = data.get("local_values", {}),
            global_values = data.get("global_values", {}),
            step_limit = data.get("step_limit"),
            on_step_update = data.get("on_step_update"),
            on_job_finish = data.get("on_job_finish"),
            block_limit_overrides = data.get("block_limit_overrides", {})
        )
        _conduit.load_step_list(data.get("steps", []))
        return _conduit

    
    def load_step_list(self, steps : List[Dict[str, Any]]) -> None:
        """
        Creates steps from a list that contains dictionary objects and adds to current job.

        Args:
            steps:
                List of dictionaries that contains step data. At least the `action` key is required
                in all dictionaries but it can include optional keys such as `parameters`, `id`, `forced` and `if`.
        """
        for step in steps:
            self.create_step(
                step["action"],
                parameters = step.get("parameters", {}),
                id = step.get("id"),
                forced = step.get("forced", False),
                if_condition = step.get("if")
            )

    
    def _count_block_usage(self, block : Union[ConduitBlock, ConduitBlock._Partial]) -> int:
        return len([x for x in self.steps if x.block == block])


    def _get_block_limit(self, block : Union[ConduitBlock, ConduitBlock._Partial]) -> Tuple[bool, Optional[int]]:
        _usage = self._count_block_usage(block)
        _limit = block.max_uses
        for key, value in self.block_limit_overrides.items():
            if pattern_match(block.display_name, key):
                _limit = value
                break
        if _limit == None:
            return False, _limit
        return _usage > _limit, _limit


    def create_step(
        self, 
        action : str, 
        parameters : dict = {}, 
        id : Optional[str] = None, 
        forced : bool = False, 
        if_condition : Union[str, List[str], None] = None
    ) -> ConduitStep:
        """
        Creates a new step in this job then returns the created step (after adding it to job).

        `action` is the name of the block along with category. For example, if `MATH.SUM` provided as `action`,
        It searches for a block named `sum` in the `Math` category. 
        Refer to [`ConduitBlock.get`][pyconduit.block.ConduitBlock.get] about getting a block by its display name.

        Args:
            action:
                Name of the block. 
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
        
        Returns:
            The created step.
        """
        _step = ConduitStep(
            job = self, 
            block = ConduitBlock.get(action), 
            parameters = parameters, 
            id = id, 
            forced = forced, 
            if_condition = if_condition
        )
        return _step


    def get_step(
        self,
        step : Union[str, int],
        silent : bool = False
    ) -> Union[ConduitStep, None]:
        """
        Gets a step in the job. 
        
        If `step` parameter is `int`, then it looks for step positions (which starts from 1).
        If `step` parameter is `str`, then it looks for step IDs.

        Raises KeyError if step is not found and `silent` flag is set to False.
        Otherwise it returns None when step is not found.

        Args:
            step:
                The ID or position of the step that will be searched for.
            silent:
                If set to `True`, it won't do anything when step is not found instead of raising an exception.
        """
        # Check type.
        if not isinstance(step, (int, str)):
            raise TypeError(f"invalid type: {type(step)}")
        is_int = isinstance(step, int)
        # Look for all steps.
        for item in self.steps:
            if is_int and step == item.position:
                return item
            elif step == item.id:
                return item
        if silent:
            return None
        raise KeyError(f"couldn't found any step for '{step}'")
    

    def delete_step(
        self,
        step : Union[str, int],
        silent : bool = True
    ) -> None:
        """
        Deletes a step from the job. 
        
        If `step` parameter is `int`, then it looks for step positions (which starts from 1).
        If `step` parameter is `str`, then it looks for step IDs.
        
        Raises KeyError if step is not found and `silent` flag is set to False.
        Otherwise it does nothing when step is not found.

        Args:
            step:
                The ID or position of the step that will be deleted.
            silent:
                If set to `True`, it won't do anything when step is not found instead of raising an exception.
        """
        step = self.get_step(step, silent = silent)
        if step:
            self.steps.remove(step)


    @property
    def contexts(self) -> Dict[str, Any]:
        """
        Returns the contexts of the job. Contexts are values that can be seen and used by users. 
        Refer to [Context Values](../../context_values) section to learn more about contexts.

        Returns:
            A dictionary that contains information about this job.
        """
        return self._contexts

    
    def create_contexts(self) -> Dict[str, Any]:
        """
        Creates and returns a dictionary of contexts.
        Refer to [Context Values](../../context_values) section to learn more about contexts.

        Note:
            When running the job, this method will be called before executing every step any will be set as job contexts. 
            If you want to edit the contexts, you can create a custom class that inherits from Conduit class, 
            then override that method.

        Returns:
            A dictionary that contains information about this job.
        """
        return { 
            "job": {
                "name": self.name,
                "success": self.success,
                "parameters": self.local_values,
                "id": self.id,
                "variables": self.variables
            },
            "steps": {
                step.id : {
                    "result": step.return_value,
                    "status": {
                        "name": step.status.name,
                        "value": step.status.value
                    },
                    "position": step.position,
                    "action": step.block.display_name,
                    "block": {
                        "category": step.block.category,
                        "name": step.block.name
                    },
                    "parameters": step.parameters,
                    "id": step.id,
                } for step in self.steps
            }
        }
    

    def update_contexts(self) -> None:
        """
        Gets the contexts from [`create_contexts`][pyconduit.conduit.Conduit.create_contexts] and sets it to
        job's contexts attribute.

        Equivalent to:
        ```py
        job._contexts = job.create_contexts()
        ```
        """
        self._contexts = self.create_contexts()


    async def run(self) -> None:
        """
        Executes all steps in this job one by one. If one of step fails, then next steps will be skipped unless
        their `forced` flag is set to `True`.

        Danger:
            If you use `await` for `job.run()`, then this means no other jobs will be executed until current job finishes. 
            If that's the thing that you don't want, then you can use [`asyncio`](https://docs.python.org/3/library/asyncio.html){target=_blank} or alternatives for executing the `run()` method
            without `await`.
        """
        failed_step = None
        self._success = None
        process = _ConduitProcess()
        for item in self.steps:
            self.update_contexts()
            # Refresh the contexts (job parameters).
            # If one of previous steps has failed don't execute the next ones.
            if self.success == None or item.forced:
                try:
                    if item.status not in [ConduitStatus.DONE, ConduitStatus.NONE]:
                        raise ConduitError(item.status, item)
                    elif not item.check_if_condition():
                        raise ConduitBlock(ConduitStatus.IF_CONDITION_FAILED, item)
                    else:
                        process.set_function(item.function())
                        if item.block.is_coroutine:
                            # Execute the function as coroutine.
                            item.return_value = await process.run_async()
                        else:
                            # Execute the function as it is.
                            item.return_value = process.run()
                except AssertionError as asr:
                    item.status = ConduitStatus.ASSERTION_ERROR
                    item.return_value = asr if len(asr.args) != 1 else asr.args[0]
                except ValueError as vae:
                    item.status = ConduitStatus.INVALID_ARGUMENT
                    item.return_value = vae if len(vae.args) != 1 else vae.args[0]
                except ValidationError as val:
                    item.status = ConduitStatus.INVALID_TYPE
                    item.return_value = val
                except ConduitError as act:
                    item.status = act.status
                    item.return_value = act.text
                except Exception as e:
                    item.status = ConduitStatus.UNHANDLED_EXCEPTION
                    item.return_value = e
                else:
                    item.status = ConduitStatus.DONE
                if item.status not in [ConduitStatus.DONE, ConduitStatus.IF_CONDITION_FAILED]:
                    failed_step = item
                    self._success = False
            else:
                item.status = ConduitStatus.SKIPPED
                item.return_value = ConduitError(item.status, item).text
            # Run the listener if exists.
            if self.on_step_update:
                if inspect.iscoroutinefunction(self.on_step_update):
                    await self.on_step_update(self, item)
                else:
                    self.on_step_update(self, item)
        process.close()
        # If there are no any errors in the jobs, set the success to True.
        if self.success == None:
            self._success = True
        # Run the listener if exists.
        if self.on_job_finish:
            if inspect.iscoroutinefunction(self.on_job_finish):
                await self.on_job_finish(self, failed_step)
            else:
                self.on_job_finish(self, failed_step)


    def __len__(self) -> int:
        return len(self.steps)


    def __getitem__(self, key) -> ConduitStep:
        return self.get_step(key)

    
    def __delitem__(self, key) -> None:
        self.delete_step(key)

    
    def __iter__(self) -> Iterator[ConduitStep]:
        return iter(self.steps)

    
    def __str__(self) -> str:
        return self.name or "Unnamed Conduit"

    
    def __bool__(self) -> bool:
        if self.success == None:
            return False
        return self.success

    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} named '{self.__str__()}' with {self.__len__()} step(s)>"