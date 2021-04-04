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

from pyconduit.other import EMPTY, ConduitError
from typing import Any, List
from pyconduit.category import ConduitCategory
from pyconduit.category import ConduitBlock as conduitblock
from pyconduit.conduit import Conduit
from pyconduit.enums import ConduitStatus
from pyconduit.step import ConduitVariable

# VARIABLE
# Contains blocks to access job variables.
class Variable(ConduitCategory):
    """
    Contains blocks to access job variables.
    """

    @conduitblock.make(name = "set")
    def set_(job__ : Conduit, *, name : str, value : Any = None) -> None:
        """
        Sets a value to variable. If variable doesn't exists, creates new one.

        Args:
            name:
                Name of the variable.
            value:
                Value of the variable.
        """
        job__.variables[name] = ConduitVariable(value)


    @conduitblock.make
    def create(job__ : Conduit, *, name : str) -> None:
        """
        Creates a new blank variable, if variable is already exists, raises an error.

        Args:
            name:
                Name of the variable.
        """
        assert name in job__.variables, name
        job__.variables[name] = ConduitVariable(None)


    @conduitblock.make
    def get(job__ : Conduit, *, name : str, default : Any = EMPTY) -> ConduitVariable:
        """
        Gets the variable by its name. Raises an error if default value hasn't provided and variable doesn't exists.
        
        Args:
            name:
                Name of the variable.
            default:
                If provided, returns it if variable is not found. If not provided, raises an error if variable
                doesn't exists.
        """
        if default != EMPTY:
            return job__.variables.get(name, default)
        else:
            return job__.variables[name]

    
    @conduitblock.make
    def delete(job__ : Conduit, *, name : str, silent : bool = True) -> None:
        """
        Deletes the variable by its name. Raises an error if `silent` flag is set to `False` and variable doesn't exists.
        
        Args:
            name:
                Name of the variable.
            silent:
                Raises an error if `silent` flag is set to `False` and variable doesn't exists.
        """
        if silent:
            if name in job__.variables:
                del job__.variables[name]
        else:
            del job__.variables[name]

    
    @conduitblock.make
    def list_names(job__ : Conduit) -> List[str]:
        """
        Lists the variable names.
        """
        return list(job__.variables.keys())


    @conduitblock.make
    def list_values(job__ : Conduit) -> List[ConduitVariable]:
        """
        Lists the variable values.
        """
        return list(job__.variables.values())

    
    @conduitblock.make
    def is_exists(job__ : Conduit, *, name : str) -> bool:
        """
        Checks if variable exists.

        Args:
            name:
                Name of the variable.
        """
        return name in job__.variables

    
    @conduitblock.make
    def count(job__ : Conduit) -> int:
        """
        Counts the variables.
        """
        return len(job__.variables.keys())