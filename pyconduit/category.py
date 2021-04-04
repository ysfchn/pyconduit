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

__all__ = ["ConduitCategory"]

from typing import Union
from pyconduit import ConduitBlock

class ConduitCategory:
    """
    To create a new category, it must be derived from this class. Then you can create your blocks inside
    with [`@ConduitBlock.make`][pyconduit.block.ConduitBlock.make] decorator.

    ```py
    from pyconduit import ConduitCategory

    class MyBlocks(ConduitCategory):
        ...
    ```
    """
    @classmethod
    def get(cls, display_name : str) -> Union[ConduitBlock, ConduitBlock._Partial]:
        """
        Gets a block by its display name in this category. Category name will be added automatically, so you don't need
        to type the category name in the parameter. If you want to search for a full display name, then refer to 
        [`ConduitBlock.get`][pyconduit.block.ConduitBlock.get]

        Args:
            display_name:
                The display name of the block. 
        """
        return ConduitBlock.get(cls.__name__.upper() + "." + display_name)

    def __len__(self) -> int:
        return len(self.__class__.__blocks__)

    def __str__(self) -> str:
        return self.__class__.__category_name__

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} with {len(self.__class__.__blocks__)} block(s)>"

    def __bool__(self) -> bool:
        return len(self.__class__.__blocks__) > 0