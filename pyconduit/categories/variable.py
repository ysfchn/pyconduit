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

from pyconduit import Category, block, Job, ConduitVariable, EMPTY
from typing import Any, List

# VARIABLE
# Contains blocks to access job variables.
class Variable(Category):
    """
    Contains blocks to access job variables.
    """

    @block(label = "set")
    def set_(job__ : Job, *, name : str, value : Any = None) -> None:
        """
        Sets a value to variable. If variable doesn't exists, creates new one.

        Args:
            name:
                Name of the variable.
            value:
                Value of the variable.
        """
        job__.variables[name] = ConduitVariable(value)


    @block
    def create(job__ : Job, *, name : str) -> None:
        """
        Creates a new blank variable, if variable is already exists, doesn't do anything.

        _In v1.1, creating a new variable that exists already doesn't raise an exception anymore. Before v1.1,
        creating a new variable is already exists raise an exception._

        Args:
            name:
                Name of the variable.
        """
        if name in job__.variables:
            return
        job__.variables[name] = ConduitVariable(None)


    @block
    def get(job__ : Job, *, name : str, default : Any = EMPTY) -> ConduitVariable:
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

    
    @block
    def delete(job__ : Job, *, name : str, silent : bool = True) -> None:
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

    
    @block
    def list_names(job__ : Job) -> List[str]:
        """
        Lists the variable names.
        """
        return list(job__.variables.keys())


    @block
    def list_values(job__ : Job) -> List[ConduitVariable]:
        """
        Lists the variable values.
        """
        return list(job__.variables.values())

    
    @block
    def is_exists(job__ : Job, *, name : str) -> bool:
        """
        Checks if variable exists.

        Args:
            name:
                Name of the variable.
        """
        return name in job__.variables

    
    @block
    def count(job__ : Job) -> int:
        """
        Counts the variables.
        """
        return len(job__.variables.keys())