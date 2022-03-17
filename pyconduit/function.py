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

__all__ = ["FunctionStore"]

from functools import partial
from typing import Coroutine, List, Callable, Any, Dict, Optional, Union, Protocol, runtime_checkable, TYPE_CHECKING
import inspect
from pyconduit.utils import parse_name, make_name, pattern_match

if TYPE_CHECKING:
    from pyconduit.node import Node

# If pydantic is available, use pydantic's validate arguments function.
try:
    from pydantic import create_model, BaseConfig
except (ImportError, ModuleNotFoundError):
    create_model = None
    BaseConfig = None


@runtime_checkable
class FunctionProtocol(Protocol):
    conduit : "FunctionStore"

Function = Callable[..., FunctionProtocol]


class FunctionStore:

    functions : Dict[str, FunctionProtocol] = {}

    __slots__ = (
        "label",
        "_name",
        "_category",
        "max_uses",
        "private",
        "tags",
        "doc",
        "validate",
        "ctx",
        "_return_type",
        "_parameters",
        "_is_coroutine",
        "_doc",
        "_populated",
        "_model"
    )

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
        self._model : Any = None

    def from_function(self, func : Union[Callable, Coroutine]):
        self._populated = True
        # Get function's docstring if not providen.
        self._doc = self.doc or inspect.getdoc(self.get_wrapped(func))
        # Get function's return type.
        self._return_type = inspect.signature(self.get_wrapped(func)).return_annotation
        # Get function's parameters.
        self._parameters = dict(inspect.signature(self.get_wrapped(func)).parameters)
        # Check if function is coroutine.
        self._is_coroutine = inspect.iscoroutinefunction(self.get_wrapped(func))
        self._model = self.to_model(
            arbitrary_types_allowed = True,
            extra = "ignore"
        )


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
    def is_validated(self):
        return bool(self._model)

    @property
    def description(self) -> Optional[str]:
        return self._doc

    @classmethod
    def get(cls, display_name : str) -> Optional[FunctionProtocol]:
        return cls.functions.get(display_name)

    @classmethod
    def match_first(cls, pattern : str) -> Optional[FunctionProtocol]:
        return next((v for k, v in cls.functions.items() if pattern_match(k.display_name, pattern, strict = True)), None)

    @classmethod
    def match_all(cls, pattern : str) -> List[FunctionProtocol]:
        return [v for k, v in cls.functions.items() if pattern_match(k.display_name, pattern, strict = True)]

    @staticmethod
    def block(
        __func : Optional[Function] = None,
        /,
        **kwargs
    ) -> Function:
        if not __func:
            return partial(FunctionStore.block, **kwargs)
        name = getattr(__func, "__func__", __func).__qualname__
        x = FunctionStore(label = (kwargs.pop("label", None) or name), **kwargs)
        x.from_function(func = __func)
        __func.conduit = x
        if not x.private:
            x.functions[x.display_name] = __func
        return __func

    @staticmethod
    def is_block(__func : Callable):
        return hasattr(__func, "conduit") and isinstance(__func.conduit, FunctionStore)

    @staticmethod
    def get_wrapped(__func : Callable):
        return getattr(__func, "__func__", __func)

    def to_model(self, **kwargs):
        if not create_model:
            return
        if not self._parameters:
            return
        m = {}
        for k, v in self._parameters.items():
            if v.kind not in [inspect.Parameter.KEYWORD_ONLY, inspect.Parameter.VAR_KEYWORD, inspect.Parameter.POSITIONAL_OR_KEYWORD]:
                continue
            m[k] = (
                Any if v.annotation == inspect._empty else v.annotation, 
                ... if v.default == inspect._empty else v.default,
            )
        return create_model("FunctionValidate", __config__ = type("Config", (BaseConfig, ), kwargs), **m)

    def validate_params(self, **kwargs):
        if not self.is_validated:
            return
        self._model(**kwargs)

    def exists_tags(self, tags : List[str]) -> bool:
        return all([x in tags for x in self.tags])

    def prefill_arguments(self, node : "Node") -> List[Any]:
        args = []
        for k, v in self.parameters.items():
            # Check if parameter is positional argument.
            if v.kind in [inspect.Parameter.KEYWORD_ONLY, inspect.Parameter.VAR_KEYWORD]:
                continue
            name = k.replace("__", "")
            # If positional parameter name is "job", pass the job itself.
            if name == "job":
                args.append(node.job)
            # If positional parameter name is "node", pass the node.
            elif name == "node":
                args.append(node)
            # Otherwise, get positional parameter from global values.
            else:
                args.append(node.job.global_values.get(name))
        return args

    def __bool__(self) -> bool:
        return self._populated

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} for {self.display_name}>"


block = FunctionStore.block


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