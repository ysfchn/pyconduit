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

from typing import Any, List
from pyconduit.category import ConduitCategory
from pyconduit.category import ConduitBlock as conduitblock

# TEXT
# Contains blocks to manipulate texts.
class Text(ConduitCategory):
    """
    Contains blocks to manipulate texts.
    """

    @conduitblock.make
    def create(*, value : Any) -> str:
        """
        Convert a value to text.

        Args:
            value:
                Any value.
        """
        return str(value)


    @conduitblock.make
    def join(*, text1 : str, text2 : str, join_with : str = " ") -> str:
        """
        Joins two texts.

        Args:
            text1:
                A string that will be added to start.
            text2:
                A string that will be added to end.
            join_with:
                A string that will be added between `text1` and `text2`.
        """
        return text1 + join_with + text2


    @conduitblock.make
    def join_list(*, list : List[str], seperator : str = "") -> str:
        """
        Joins all strings in the list.

        Args:
            seperator:
                A seperator for joining strings.
            list:
                A list that contains strings.
        """
        return seperator.join(list)


    @conduitblock.make
    def includes(*, text : str, piece : str) -> bool:
        """
        Checks if piece is in the text.

        Args:
            text:
                The text that piece will be checked in.
            piece:
                The piece that will be searched.
        """
        return piece in text


    @conduitblock.make
    def count(*, text : str) -> int:
        """
        Counts the characters in a string.

        Args:
            text:
                The text that will be used in the operation.
        """
        return len(text)

    
    @conduitblock.make(name = "get")
    def get_(*, text : str, index : int) -> str:
        """
        Gets the character in specified index.

        Args:
            text:
                The text that will be used in the operation.
            index:
                The index of the character.
        """
        return text[index]

    
    @conduitblock.make
    def count_piece(*, text : str, piece : str) -> int:
        """
        Return the number of non-overlapping occurrences of substring in string.

        Args:
            text:
                The text that will be used in the operation.
            piece:
                The piece that will be searched.
        """
        return text.count(piece)


    @conduitblock.make
    def is_empty(*, text : str, include_spaces : bool = True) -> bool:
        """
        Checks if string is empty.

        Args:
            text:
                The text that will be used in the operation.
            include_spaces:
                Set it `True` to include spaces too, if you want to strip the text first,
                set it to `False`.
        """
        if include_spaces:
            return len(text) == 0
        else:
            return len(text.strip()) == 0


    @conduitblock.make
    def strip(*, text : str, chars : str = None) -> str:
        """
        Return a copy of the string with leading and trailing whitespace removed.
        If chars is given and not None, remove characters in chars instead.

        Args:
            text:
                The text that will be used in the operation.
            chars:
                If given, removes these characters from the string instead of trimming.
        """
        return text.strip(chars)
    

    @conduitblock.make
    def uppercase(*, text : str) -> str:
        """
        Return a copy of the string converted to uppercase.

        Args:
            text:
                The text that will be used in the operation.
        """
        return text.upper()


    @conduitblock.make
    def lowercase(*, text : str) -> str:
        """
        Return a copy of the string converted to lowercase.

        Args:
            text:
                The text that will be used in the operation.
        """
        return text.lower()

    
    @conduitblock.make
    def split(*, text : str, seperator : str = None, maxsplit : int = -1) -> List[str]:
        """
        Return a list of the words in the string, using "seperator" parameter as the delimiter string.
        
        Args:
            text:
                The text that will be used in the operation.
            seperator: 
                The delimiter according which to split the string. None (the default value) means split according to any whitespace, and discard empty strings from the result.
            maxsplit: 
                Maximum number of splits to do. -1 (the default value) means no limit.
        """
        return text.split(sep = seperator, maxsplit = maxsplit)


    @conduitblock.make
    def titlecase(*, text : str) -> str:
        """
        Return a version of the string where each word is titlecased.
        More specifically, words start with uppercased characters and all remaining cased characters have lower case.
        
        Args:
            text:
                The text that will be used in the operation.
        """
        return text.title()


    @conduitblock.make
    def starts_with(*, text : str, piece : str) -> bool:
        """
        Return `True` if text starts with the specified piece, `False` otherwise.

        Args:
            text:
                The text that will be used in the operation.
            piece:
                The piece that will be checked.
        """
        return text.startswith(piece)

    
    @conduitblock.make
    def ends_with(*, text : str, piece : str) -> bool:
        """
        Return `True` if text ends with the specified piece, `False` otherwise. 

        Args:
            text:
                The text that will be used in the operation.
            piece:
                The piece that will be checked.
        """
        return text.endswith(piece)


    @conduitblock.make
    def is_numeric(*, text : str) -> bool:
        """
        Return `True` if the string is a numeric string, `False` otherwise.
        A string is numeric if all characters in the string are numeric and there is at least one character in the string.
        
        Args:
            text:
                The text that will be used in the operation.
        """
        return text.isnumeric()


    @conduitblock.make
    def is_text(*, value : Any) -> bool:
        """
        Return `True` if the thing is a text, `False` otherwise.

        Args:
            value:
                Any value.
        """
        return isinstance(value, str)

    
    @conduitblock.make
    def replace(*, text : str, old : str, new : str, count : int = -1) -> str:
        """
        Return a copy with all occurrences of substring old replaced by new.
        If the optional argument count is given, only the first count occurrences are replaced.

        Args:
            text:
                The text that will be used in the operation.
            old:
                The string that will be replaced.
            new:
                The string that `old` replaced with.
            count:
                If given, only the first count occurrences are replaced.
        """
        return text.replace(old, new, count)