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

__all__ = ["FunctionStore"]

from functools import partial
from typing import Coroutine, List, Callable, Any, Dict, Optional, Union, Protocol, runtime_checkable, TYPE_CHECKING
import inspect
from pyconduit.node import Node
from pyconduit.utils import parse_name, make_name, pattern_match

# If pydantic is available, use pydantic's validate arguments function.
try:
    from pydantic import validate_arguments
except (ImportError, ModuleNotFoundError):
    validate_arguments = None


@runtime_checkable
class FunctionProtocol(Protocol):
    conduit : "FunctionStore"

Function = Callable[..., FunctionProtocol]


class FunctionStore:

    functions : Dict[str, FunctionProtocol] = {}

    def __init__(
        self,
        label : str,
        max_uses : Optional[int] = None,
        private : bool = False,
        tags : List[str] = [],
        doc : Optional[str] = None,
        validate : bool = True,
        ctx : Optional[dict] = None
    ) -> None:
        self.label : str = label
        self._name, self._category = parse_name(self.label)
        self.max_uses : Optional[int] = max_uses
        self.private : bool = private
        self.tags : List[str] = tags
        self.doc : Optional[str] = doc
        self.validate : bool = validate
        self.ctx : dict = ctx or {}
        # Populated when function has provided.
        self._return_type : Optional[Any] = None
        self._parameters : Optional[Dict[str, inspect.Parameter]] = None
        self._is_coroutine : Optional[bool] = None
        self._doc : Optional[str] = None
        self._populated : bool = False

    def from_function(self, func : Union[Callable, Coroutine]):
        self._populated = True
        # Get function's docstring if not providen.
        self._doc = self.doc or inspect.getdoc(func)
        # Get function's return type.
        self._return_type = inspect.signature(func).return_annotation
        # Get function's parameters.
        self._parameters = inspect.signature(func).parameters
        # Check if function is coroutine.
        self._is_coroutine = inspect.iscoroutinefunction(func)

    @property
    def display_name(self) -> str:
        return make_name(self._name, self._category)

    @property
    def return_type(self) -> Any:
        return self._return_type

    @property
    def parameters(self) -> Dict[str, inspect.Parameter]:
        return self._parameters

    @property
    def is_coroutine(self) -> bool:
        return self._is_coroutine

    @property
    def description(self) -> Optional[str]:
        return self._doc

    @classmethod
    def get(cls, display_name : str) -> Optional[FunctionProtocol]:
        return cls.blocks.get(display_name)

    @classmethod
    def match_first(cls, pattern : str) -> Optional[FunctionProtocol]:
        return next((v for k, v in cls.blocks.items() if pattern_match(k.display_name, pattern, strict = True)), None)

    @classmethod
    def match_all(cls, pattern : str) -> List[FunctionProtocol]:
        return [v for k, v in cls.blocks.items() if pattern_match(k.display_name, pattern, strict = True)]

    @staticmethod
    def block(
        __func : Optional[Function] = None,
        /,
        **kwargs
    ) -> Function:
        if not __func:
            return partial(FunctionStore.block, **kwargs)
        x = FunctionStore(label = kwargs.pop("label", __func.__qualname__), **kwargs)
        x.from_function(func = __func)
        __func.conduit = x
        if (x.validate == True) and validate_arguments:
            __func = validate_arguments(__func)
        if not x.private:
            x.blocks[x.display_name] = __func
        return __func

    @staticmethod
    def is_block(__func : Callable):
        return hasattr(__func, "conduit") and isinstance(__func.conduit, FunctionStore)

    def exists_tags(self, tags : List[str]) -> bool:
        return all([x in tags for x in self.tags])

    def prefill_arguments(self, step : Node) -> List[Any]:
        args = []
        for k, v in self.parameters.items():
            # Check if parameter is positional argument.
            if v.kind in [inspect.Parameter.KEYWORD_ONLY, inspect.Parameter.VAR_KEYWORD]:
                continue
            name = k.replace("__", "")
            # If positional parameter name is "job", pass the job itself.
            if name == "job":
                args.append(step.job)
            # If positional parameter name is "step", pass the step.
            elif name == "step":
                args.append(step)
            # Otherwise, get positional parameter from global values.
            else:
                args.append(step.job.global_values.get(name))
        return args

    def __bool__(self) -> bool:
        return self._populated

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} for {self.display_name}>"


block = FunctionStore.block


@block(private = True)
def debug(**kwargs):
    print(kwargs)


if TYPE_CHECKING:
    # Override block() to show available keyword arguments
    # instead of just displaying **kwargs.
    def block(
        __func : Optional[Function] = None,
        /,
        label : Optional[str] = None,
        max_uses : Optional[int] = None,
        private : bool = False,
        tags : List[str] = [],
        doc : Optional[str] = None,
        validate : bool = True,
        ctx : Optional[dict] = None
    ) -> Function:
        ...