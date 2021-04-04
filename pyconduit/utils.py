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

__all__ = ["pattern_match", "parse_display_name"]

from typing import (
    Tuple,
    Optional,
    Any,
    Union
)
import re
from pyconduit.other import ScopedObject


def pattern_match(item : str, pattern : str, strict : bool = True) -> bool:
    """
    Check if item matches with the pattern that contains 
    "*" wildcards and "?" question marks.

    Args:
        item:
            The string that pattern will be applied to.
        pattern:
            A wildcard (glob) pattern.
        strict:
            If `True`, then it will check if matched string equals with the `item` parameter.
            So applying "foo?" pattern on "foobar" will result in `False`. Default is `True`.
    
    Returns:
        A boolean value.
    """
    _ptn = pattern.replace(".", "\.").replace("+", "\+").replace("*", ".+").replace("?", ".")
    _match = re.match(_ptn, item)
    if strict and bool(_match):
        return _match.group(0) == item
    return bool(_match)


def parse_display_name(name : str) -> Tuple[Optional[str], str]:
    """
    Splits the display name into two item tuple which represents
    category and block name.

    Args:
        name:
            Any string that represents the block display name.
    
    Returns:
        A two item tuple: first item is for category and
        second one is for block name. Category can be None if name doesn't contain
        any "." (dot) character.
    """
    _parts = name.split(".")
    if len(_parts) == 1:
        return (None, _parts[0])
    return (_parts[0], ".".join(_parts[1:]))


def parse_slice(value : str) -> Optional[slice]:
    """
    Parses a `slice()` from string, like `start:stop:step`.

    Args:
        value:
            A string value that contains the slice string. For example: `start:stop:step`.
    
    Returns:
        A slice object or `None` if string is not valid. 
    """
    try:
        if value:
            return slice(*[int(p) if p else None for p in value.split(":")])
    except TypeError:
        return None


def get_key_path(obj : Union[dict, list, ScopedObject, str], key : str) -> Any:
    """
    Gets a key from dict or value from list with dotted key path. It can also read attributes of object
    if object is wrapped in the [`ScopedObject`][pyconduit.other.ScopedObject].

    It raises KeyError if key starts with or ends with underscore to prevent unwanted access in runtime.

    Args:
        obj:
            A dictionary, list or [`ScopedObject`][pyconduit.other.ScopedObject].
        key:
            List of keys joined with "." (dots).

    Returns:
        The final value.
    """
    current_value = obj
    for item in key.split("."):
        if item.startswith("__") or item.endswith("__") or item.startswith("_") or item.endswith("_"):
            raise KeyError(item)
        elif isinstance(current_value, (list, str)) and item.isnumeric() and int(item) < len(current_value):
            current_value = current_value[int(item)]
        elif isinstance(current_value, (list, str)) and parse_slice(item) != None:
            current_value = current_value[parse_slice(item)]
        elif isinstance(current_value, ScopedObject):
            current_value = getattr(current_value, item)
        elif isinstance(current_value, dict):
            current_value = current_value[item]
    return current_value