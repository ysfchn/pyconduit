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

import re
from typing import Any, Optional, Tuple, Union

FROM_CHARS = "ıi"
TO_CHARS   = "II"


def upper(text : str) -> str:
    """
    Convert text to uppercase (with handling Turkish characters correctly.)
    """
    t = text.maketrans(FROM_CHARS, TO_CHARS)
    return text.strip().strip("/<>\\#@").replace("'", "").replace('"', "").translate(t).upper()


def make_name(name : str, category : Optional[str] = None) -> str:
    """
    Create display name from category and name.
    """
    if ("." in name) or ("." in (category or "")):
        raise ValueError("Name or category can't contain (.) dots.")
    if not category:
        return upper(name)
    return ".".join([upper(name), upper(category)])


def parse_name(value : str) -> Tuple[str, Optional[str]]:
    """
    Parse category and name from a display name. 
    """
    name, *category = upper(value).split(".", 1)
    return (name, "".join(category) or None, )


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
    except (TypeError, ValueError):
        return None


def get_key_path(obj : Union[dict, list, str], key : str) -> Any:
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
        elif isinstance(current_value, dict):
            current_value = current_value[item]
    return current_value