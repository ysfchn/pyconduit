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

from typing import Any, Dict, List, Union, Tuple
from pyconduit import Category, block, Variable, EMPTY

# DICTIONARY
# Contains blocks to work with dictionaries.
class Dictionary(Category):
    """
    Contains blocks to work with dictionaries.
    """

    @block
    def create(**kwargs) -> Dict[str, Any]:
        """
        Creates a new dictionary from keyword arguments.

        Args:
            kwargs:
                Dictionary.
        """
        return kwargs


    @block
    def create_from_pairs(*, key : str, value : Any) -> Dict[str, Any]:
        """
        Creates a new dictionary with one pairs from "key" and "value" parameters.

        Args:
            key:
                Key of the pair.
            value:
                Value of the pair.
        """
        return {key: value}

    
    @block
    def create_from_list(*, pairs : Union[Tuple[str, Any], List[Tuple[str, Any]]]) -> Dict[str, Any]:
        """
        Creates a new dictionary with list of pairs.

        Args:
            pairs:
                A list that contains two values, first is for key and second is for value.
                You can also provide a list of lists for creating dictionary with more than one pair.
        """
        if len(pairs) == 2 and isinstance(pairs[0], str):
            return { pairs[0] : pairs[1] }
        else:
            return { a[0] : a[1] for a in pairs }


    @block
    def get(*, key : str, dictionary : Dict[str, Any], default : Any = EMPTY) -> Any:
        """
        Gets a value from dictionary by using key. If value couldn't found and default parameter has specified, returns the default value.
        Otherwise, raises an error.

        Args:
            key:
                The key that used when getting value from dictionary.
            dictionary:
                The dictionary that will be used in the operation.
            default:
                The default value if key is not found in the dictionary.
        """
        if default != EMPTY:
            return dictionary.get(key, default)
        else:
            return dictionary[key]


    @block(label = "dictionary.set")
    def set_(*, key : str, value : Any, dictionary : Union[Dict[str, Any], Variable]) -> None:
        """
        Sets a key and value to dictionary. The key doesn't have to exists in the dictionary.

        Args:
            key:
                The key that used when getting value from dictionary.
            value:
                The value that will be added to dictionary.
            dictionary:
                The dictionary that will be used in the operation.
        """
        dictionary[key] = value

    
    @block
    def delete(*, key : Union[str, None, slice], dictionary : Union[Dict[str, Any], Variable], silent : bool = True) -> None:
        """
        Deletes a value and key from dictionary by using key or slice object. 
        If value couldn't found and `silent` parameter has set to `False`, it will raise an error.
        Setting the key to `None` will delete all keys.

        Args:
            key:
                It can be a dictionary key, slice object and `None`.
            dictionary:
                The dictionary that will be used in the operation.
            silent:
                Setting it to `False` will raise an error when value couldn't found. 
        """
        if key is slice:
            del dictionary[key]
            return
        if silent:
            if key in dictionary:
                if key == None:
                    del dictionary[:]
                else:
                    del dictionary[key]
        else:
            if key == None:
                del dictionary[:]
            else:
                del dictionary[key]


    @block
    def merge(*, dict1 : Dict[str, Any], dict2 : Dict[str, Any]) -> Dict[str, Any]:
        """
        Merges two dictionaries and returns a new dictionary. If same keys has provided in both
        dictionaries, `dict2` will be dominant.

        Args:
            dict1:
                First dictionary.
            dict2:
                Second dictionary.
        """
        return { **dict1, **dict2 }

    
    @block
    def pop(*, key : str, dictionary : Union[Dict[str, Any], Variable], default : Any = EMPTY) -> Any:
        """
        If key is in the dictionary, remove it and return its value, else return default. 
        If default is not given and key is not in the dictionary, an error is raised.

        Args:
            key:
                The key that used when getting value from dictionary.
            dictionary:
                The dictionary that will be used in the operation.
            default:
                The default value if key is not found in the dictionary.
        """
        if default != EMPTY:
            return dictionary.pop(key, default)
        else:
            return dictionary.pop(key)

    
    @block
    def update(*, dict1 : Union[Dict[str, Any], Variable], dict2 : Union[Dict[str, Any], Variable]) -> None:
        """
        Updates `dict1` by adding values from `dict2`. It doesn't returns the updated dictionary, instead it updates in place.

        Args:
            dict1:
                First dictionary.
            dict2:
                Second dictionary.
        """
        dict1.update(dict2)

    
    @block
    def clear(*, dictionary : Union[Dict[str, Any], Variable]) -> None:
        """
        Clears the dictionary.

        Args:
            dictionary:
                The dictionary that will be used in the operation.
        """
        dictionary.clear()


    @block
    def count(*, dictionary : Dict[str, Any]) -> int:
        """
        Counts the dictionary keys.

        Args:
            dictionary:
                The dictionary that will be used in the operation.
        """
        return len(dictionary.keys())


    @block
    def list_keys(*, dictionary : Dict[str, Any]) -> List[str]:
        """
        Returns a list of keys in the dictionary.

        Args:
            dictionary:
                The dictionary that will be used in the operation.
        """
        return list(dictionary.keys())


    @block
    def list_values(*, dictionary : Dict[str, Any]) -> List[Any]:
        """
        Returns a list of values in the dictionary.

        Args:
            dictionary:
                The dictionary that will be used in the operation.
        """
        return list(dictionary.values())

    
    @block
    def list_items(*, dictionary : Dict[str, Any]) -> List[List[Any]]:
        """
        Returns a list of pairs (as key and value list) in the dictionary.

        Args:
            dictionary:
                The dictionary that will be used in the operation.
        """
        return [[x, y] for x, y in dictionary.items()]


    @block
    def is_dictionary(*, value : Any) -> bool:
        """
        Tests to see whether the thing given to it is a dictionary or not.

        Args:
            value:
                Any value.
        """
        return isinstance(value, dict)


    @block
    def is_key_exists(*, key : str, dictionary : Dict[str, Any]) -> bool:
        """
        Tests whether the key exists in the dictionary.

        Args:
            key:
                The key that used when getting value from dictionary.
            dictionary:
                The dictionary that will be used in the operation.
        """
        return key in dictionary

    
    @block
    def is_value_exists(*, value : Any, dictionary : Dict[str, Any]) -> bool:
        """
        Tests whether the value exists in the dictionary.

        Args:
            value:
                Any value.
            dictionary:
                The dictionary that will be used in the operation.
        """
        return value in dictionary.values()