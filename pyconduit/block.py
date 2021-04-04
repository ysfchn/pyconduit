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

__all__ = ["ConduitBlock"]

from typing import Coroutine, List, Callable, Any, Dict, Optional, Tuple, Union
import inspect
from pyconduit.utils import parse_display_name
from pyconduit.collection import BlocksCollection

# If pydantic is available, use pydantic's validate arguments function.
try:
    from pydantic import validate_arguments
except (ImportError, ModuleNotFoundError):
    validate_arguments = lambda x, **y: x


class ConduitBlockBase:
    """
    Test
    """

    def __init__(
        self,
        name : str,
        category : Optional[str] = None,
        max_uses : Optional[int] = None,
        private : bool = False,
        tags : List[str] = [],
        function : Union[None, Callable, Coroutine] = None
    ) -> None:
        """
        Test2
        """
        self.name : str = name.upper()
        self.category : Optional[str] = None if not category else category.upper()
        if "." in self.name or "." in self.category:
            raise ValueError("block name and category name can't contain dots (.)")
        self.max_uses : Optional[int] = max_uses
        self.private : bool = private
        self.tags : List[str] = tags
        self.function : Union[None, Callable, Coroutine] = function
    
    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} for {self.display_name}>"

    @property
    def display_name(self) -> str:
        """
        Gets the display name for this block. This will be used as identifier when searching for a block.

        Returns:
            If block is defined in a [`ConduitCategory`][pyconduit.category.ConduitCategory] then this will return
            the category name which is joined with dot `(CATEGORY).(BLOCK)`, otherwise it will just return the block name `(BLOCK)`.
        """
        if not self.category:
            return self.name
        return self.category + "." + self.name


    @property
    def return_type(self) -> Any:
        """
        Returns the return type / annotation of the function.

        Returns:
            Any
        """
        _r = inspect.signature(self.raw_function).return_annotation
        if _r == inspect.Signature.empty:
            return Any
        return _r


    @property
    def parameters(self) -> Dict[str, inspect.Parameter]:
        """
        Returns a dictionary that contains parameters of inner function.

        Returns:
            A dictionary of function parameters.
        """
        return inspect.signature(self.raw_function).parameters


    @property
    def is_coroutine(self) -> bool:
        """
        Returns `True` if the inner function is coroutine / async.

        Returns:
            `True` if the inner function is coroutine (defined with `async def` syntax), otherwise `False`.
        """
        return inspect.iscoroutinefunction(self.raw_function)


    @property
    def description(self) -> Optional[str]:
        """
        Returns the docstring of function.

        Returns:
            Documentation string of the inner function. If there is no documentation string, it will be `None`.
        """
        return inspect.getdoc(self.raw_function)

    
    @property
    def raw_function(self) -> Union[None, Callable, Coroutine]:
        """
        Returns the same raw function that provided when creating the ConduitBlock. 

        If pydantic is installed, this will return the function without pydantic validation.
        If pydantic is not installed, this is same as `function` attribute.

        Returns:
            Returns the unwrapped raw function.
        """
        return getattr(self.function, "raw_function", self.function)

    __call__ = lambda *args, **kwargs: None
    # __wrapped__ = None
    # Uncommenting this causes Mkdocs to don't render the documentation.


class ConduitPartialBlock(ConduitBlockBase):
    """
    Same as [`ConduitBlock`][pyconduit.block.ConduitBlock], but it is used as placeholder for non-existing blocks.

    **ALL** partial blocks means non-existing blocks and they doesn't have any functionality.
    If that's the thing that you don't want, please refer to [`ConduitBlock`][pyconduit.block.ConduitBlock] class instead.

    Danger:
        It is discouraged to create instance of this block manually, because it is only returned 
        when searching for a non-existing block.
    
    Attributes:
        name (str):
            A custom name for the block.
        category (Optional[str]):
            Name of the category for the block. It can point to a non-existing category.
    """

    def __init__(
        self,
        name : str,
        category : Optional[str] = None
    ) -> None:
        """
        Args:
            name (str):
                A custom name for the block.
            category (Optional[str]):
                Name of the category for the block. It can point to a non-existing category.
        """
        super().__init__(name = name, category = category)

    def __bool__(self) -> bool:
        return False


class ConduitBlock(ConduitBlockBase):
    """
    Represents a function-like object. It holds the parameters, name and the function itself. 
    To access the inner function, use `function` or `__call__` attribute.

    Blocks can be defined with [`@ConduitBlock.make`][pyconduit.block.ConduitBlock.make] decorator.

    ```py
    @ConduitBlock.make
    def say hi():
        return "Hello!"

    # Call the function with pydantic validation (if pydantic is available, otherwise it is same as `hi()`):
    hi.function() 

    # Call the function without pydantic validation:
    hi() # Same as hi.__call__()
    ```

    Attributes:
        function (Union[Callable, Coroutine]):
            The function that wrapped as ConduitBlock. If pydantic has installed, this will be a custom function
            which comes from pydantic's [`validate_arguments` decorator](https://pydantic-docs.helpmanual.io/usage/validation_decorator/){target=_blank}
            that enforces parameter types.
        name (str):
            A custom name for the block, if it doesn't provided, then it will be the function name. 
            This is always converted to uppercase even if input is lowercase.
        category (Optional[str]):
            Name of the [`ConduitCategory`][pyconduit.category.ConduitCategory] that this block registered in. 
            It will be `None` if block is not registered in a category.
        tags (List[str]):
            List of tags for this block. Tags allows to restrict a block, in order to use a block that has
            tags, then all block tags need to be exist in [`Conduit`][pyconduit.conduit.Conduit], otherwise using that block will result in a `FORBIDDEN_BLOCK` status code.
            For example, if this block has "A" and "B" tags, then the job must have both "A" and "B" tags too.
            (if job has extra tags such as "C", it doesn't affect the result of the tag checking operation)
        private (Optional[bool]): 
            If checked to `True`, then this block won't be registered, so it will not be possible to get this block
            by its name. Setting it to `None` will detect if function needs to be private or not by checking if function name starts and ends with double underscore.
        max_uses (Optional[int]):
            Limits the usage count for this block per job. For example, if this set to 1, it will not be possible to execute this 
            block more than once. This can be overriden by `block_limit_overrides` attribute in [`Conduit`][pyconduit.conduit.Conduit]
    """
    _Partial = ConduitPartialBlock
    _blocks : BlocksCollection = {}

    def __init__(
        self, 
        function : Union[Callable, Coroutine], 
        name : str = None, 
        tags : List[str] = [], 
        private : Optional[bool] = None,
        max_uses : Optional[int] = None
    ) -> None:
        """
        Creates a new block.

        Warning:
            It is recommended to use [`@ConduitBlock.make`][pyconduit.block.ConduitBlock.make] decorator instead of creating a new instance manually.

        Args:
            function:
                The function that will be wrapped as ConduitBlock. If pydantic has installed, the function will be wrapped with
                pydantic's [`validate_arguments` decorator](https://pydantic-docs.helpmanual.io/usage/validation_decorator/){target=_blank}
                which creates a custom function that enforces parameter types.
            name:
                A custom name for the block, if it doesn't provided, then it uses the function name. 
                This is always converted to uppercase even if input is lowercase.
            tags:
                List of tags for this block. Tags allows to restrict a block, in order to use a block that has
                tags, then all block tags need to be exist in [`Conduit`][pyconduit.conduit.Conduit], otherwise using that block will result in a `FORBIDDEN_BLOCK` status code.
                For example, if this block has "A" and "B" tags, then the job must have both "A" and "B" tags too.
                (if job has extra tags such as "C", it doesn't affect the result of the tag checking operation)
            private: 
                If checked to `True`, then this block won't be registered, so it will not be possible to get this block
                by its name. Setting it to `None` will detect if function needs to be private or not by checking if function name starts and ends with double underscore.
            max_uses:
                Limits the usage count for this block per job. For example, if this set to 1, it will not be possible to execute this 
                block more than once. This can be overriden by `block_limit_overrides` attribute in [`Conduit`][pyconduit.conduit.Conduit]
        """
        super().__init__(
            name = name if name else function.__name__, 
            category = None if "." not in function.__qualname__ else function.__qualname__.split(".")[0],
            max_uses = max_uses,
            private = private or (function.__name__.startswith("_") if not name else name.startswith("_")),
            tags = tags,
            function = validate_arguments(function, config = { "arbitrary_types_allowed": True })
        )
        # TODO: These won't work because Python calls magic methods on class itself because of instances.
        self.__wrapped__ = function
        self.__call__ = function
        if self.display_name in ConduitBlock._blocks:
            raise ValueError(f"the block named '{self.display_name}' already exists, you can't define it multiple times")
        if not self.private:
            ConduitBlock._blocks[self.display_name] = self

    def __bool__(self) -> bool:
        return True

    def __auto_params(self) -> List[str]:
        """
        Returns a list of parameter names that needs to be filled by the ConduitStep itself.
        """
        return [
            key for key, value in self.parameters.items() if value.kind not in [inspect.Parameter.KEYWORD_ONLY, inspect.Parameter.VAR_KEYWORD]
        ]


    # TODO: Make better prefill arguments function
    def prefill_arguments(self, job, **kwargs) -> List[Any]:
        """
        Converts required keyword arguments to positional arguments and returns a list of parameters.

        Returns:
            List of positional arguments that will be passed in to the inner function.
        """
        return [kwargs.get(y.replace("__", ""), None) if y.replace("__", "") != "job" else job for y in self.__auto_params()]

    
    def exists_tags(self, tags : List[str]) -> bool:
        """
        Checks if all block tags are exists in specified tags list.

        Returns:
            `True` if all block tags are exists in the `tags` parameter, otherwise `False`.
        """
        return all([x in tags for x in self.tags])

    
    @classmethod
    def get(cls, display_name : str) -> Union["ConduitBlock", "ConduitBlock._Partial"]:
        """
        Gets a block by its display name. You can also search blocks only in a specific category with
        [`ConduitCategory.get`][pyconduit.category.ConduitCategory.get]

        Args:
            display_name:
                The display name of the block.

        Returns:
            A [`ConduitBlock`][pyconduit.block.ConduitBlock] object or 
            [`ConduitPartialBlock`][pyconduit.block.ConduitPartialBlock] if block is not found.
        """
        category, name = parse_display_name(display_name)
        return cls._blocks.get(display_name, cls._Partial(name, category))

    
    @classmethod
    def match_first(cls, pattern : str) -> Optional["ConduitBlock"]:
        """
        Returns the first ConduitBlock that matches with the specified wildcard (glob) pattern.

        Args:
            pattern:
                The display name of the block.

        Returns:
            A [`ConduitBlock`][pyconduit.block.ConduitBlock] object or 
            None if no matching block has found.
        """
        return cls._blocks.match_first(pattern)

    
    @classmethod
    def match_all(cls, pattern : str) -> List["ConduitBlock"]:
        """
        Returns a list of ConduitBlocks that matches with the specified wildcard (glob) pattern.

        Args:
            pattern:
                The display name of the block.

        Returns:
            A list of [`ConduitBlock`][pyconduit.block.ConduitBlock] object or 
            a empty list if no matching block has found.
        """
        return cls._blocks.match_all(pattern)


    @staticmethod
    def make(
        function : Union[Callable, Coroutine] = None, 
        name : Optional[str] = None, 
        tags : List[str] = [],
        private : Optional[bool] = None,
        max_uses : Optional[int] = None
    ) -> "ConduitBlock":
        """
        Decorate a Callable to ConduitBlock. This registers a function as ConduitBlock.
        
        Given functions will be wrapped with pydantic's 
        [`validate_arguments` decorator](https://pydantic-docs.helpmanual.io/usage/validation_decorator/){target=_blank}
        (if pydantic has installed in the environment, otherwise it will just wrap without any modification) and
        returned object will be a `ConduitBlock` object.

        To access the inner function, use `function` or `__call__` attribute.

        ```py
        @ConduitBlock.make
        def say hi():
            return "Hello!"

        # Call the function with pydantic validation (if pydantic is available, otherwise it is same as `hi()`):
        hi.function() 

        # Call the function without pydantic validation:
        hi() # Same as hi.__call__()
        ```

        Args:
            function:
                The function that will be wrapped as ConduitBlock. If pydantic has installed, the function will be wrapped with
                pydantic's [`validate_arguments` decorator](https://pydantic-docs.helpmanual.io/usage/validation_decorator/){target=_blank}
                which creates a custom function that enforces parameter types.
            name:
                A custom name for the block, if it doesn't provided, then it uses the function name. 
                This is always converted to uppercase even if input is lowercase.
            tags:
                List of tags for this block. Tags allows to restrict a block, in order to use a block that has
                tags, then all block tags need to be exist in [`Conduit`][pyconduit.conduit.Conduit], otherwise using that block will result in a `FORBIDDEN_BLOCK` status code.
                For example, if this block has "A" and "B" tags, then the job must have both "A" and "B" tags too.
                (if job has extra tags such as "C", it doesn't affect the result of the tag checking operation)
            private: 
                If checked to `True`, then this block won't be registered, so it will not be possible to get this block
                by its name. Setting it to `None` will detect if function needs to be private or not by checking if function name starts and ends with double underscore.
            max_uses:
                Limits the usage count for this block per job. For example, if this set to 1, it will not be possible to execute this 
                block more than once. This can be overriden by `block_limit_overrides` attribute in [`Conduit`][pyconduit.conduit.Conduit]
        
        Returns:
            The created [`ConduitBlock`][pyconduit.block.ConduitBlock] object.
        """
        if function:
            f = staticmethod(function)
            block = ConduitBlock(function = f.__func__, name = name, tags = tags, private = private, max_uses = max_uses)
            return block
        else:
            def prefilled_make(func : Callable):
                f = staticmethod(func)
                blck = ConduitBlock(function = f.__func__, name = name, tags = tags, private = private, max_uses = max_uses)
                return blck
            return prefilled_make
