# Quick Start

### Defining Blocks

Let's say you have a function that sums two number and you want users to be able to use this function by just calling its name and passing the keyword parameters.

```py
def sum_number(*, value1, value2): 
    """
    Return the sum of two numbers.
    """
    return value1 + value2
```

Just add it in any class that inherits `ConduitCategory` and wrap the block with `ConduitBlock.make()` decorator. Adding in a class is not required (if you don't add in a class, it will be a "unattached block" but will still work as other blocks), but it is encouraged to add blocks in their own categories, so you can group all math related functions in Math category.

If your environment has [pydantic](https://github.com/samuelcolvin/pydantic/){target=_blank} library installed, pyconduit will use it for validating function parameters so users will receive an exception when they try to pass any type of value except integers. You don't need to do anything to enable pydantic.

```py
from pyconduit import ConduitCategory
from pyconduit import ConduitBlock as conduitblock

class Math(ConduitCategory):
"""
Some useful math functions.
"""
    @block
    def sum_number(*, value1 : int, value2 : int) -> int:
        """
        Return the sum of two numbers.
        """
        return value1 + value2
```

!!! note
    Whenever we want to get this block object, we will only need the its category name and block name. ConduitBlocks will always uppercase the category name and block name, so you can search for a block name with case insensitively.
    In this case: `MATH.SUM_NUMBER`

    `@block` decorator registers the function as `ConduitBlock`. And note that ConduitBlocks are always static method even if they are in the class. Because `ConduitBlock` objects are designed to be independent, so when you search for a `MATH.SUM_NUMBER` block, you will directly get the block without needing to creating a instance of `Math` category.

Now users will able to call this method by just proving the block name and parameters, you need to just load their data and it is now ready to be executed.

```py
from pyconduit import Conduit, ConduitCategory
from pyconduit import ConduitBlock as conduitblock

class MyMath(ConduitCategory):
    @block
    def sum_number(*, value1 : int, value2 : int) -> int:
        return value1 + value2

# Assume that this JSON data has came from user by database or etc.
user_provided_data = \
{
    "name": "My Workflow",
    "steps": [
        {
            "action": "MATH.SUM_NUMBER",
            "parameters": {
                "value1": 5,
                "value2": 10
            }
        }
    ]
}

job = Conduit.from_dict(user_provided_data)
```

Keyword-only and keyword-variable (**kwargs) parameters means that parameter must be filled by the user, so you must add these parameters when user input is required. 

[Read more in "Defining Blocks"](../defining_blocks){ .md-button }

### Global values

Positional-only and positional-or-keyword parameters means they will be filled by server-side with global values. It is used for private values such as database objects. Users can't able to fill these positional parameters even if they provided their parameter name and value.

```py
@block
def get_user(database__, *, name : str) -> dict:
    return database__.get(name)

job = Conduit(global_values = {
    "database": a_database_object
})
```

!!! note
    As you can see, positional-only and positional-or-keyword parameters ends with double underscore. pyconduit will delete double underscore, so you can just pass `database` to `global_values` dictionary even if parameter name is `database__`.
    
    It is not needed to have a double underscore at the end for positional parameters, but it is recommended if you want your users to use `database` as keyword parameter name in **kwargs, so you can have two parameters with same name. 

[Read more in "Locals, Variables & Globals"](../locals_variables_globals){ .md-button }

### Context values

Step parameters can include a reference to other values, so it can be used to get previous step's results.

```py
user_provided_data = \
{
    "name": "My Workflow",
    "steps": [
        {
            "action": "TEXT.JOIN",
            "id": "join_text_1",
            "parameters": {
                "text1": "Hello",
                "text2": "World",
                "join_with": " "
            }
        },
        {
            "action": "TEXT.REPLACE",
            "parameters": {
                "text": "{: join_text_1 :}",
                "old": "World",
                "new": "Space"
            }
        }
    ]
}
```

[Read more in "Context Values"](../context_values){ .md-button }

### Running Job

To run the job, use `run()` method. No execution will be made until calling that method. Running jobs will not raise exception when a step raises an exception (it will just catch the all step exceptions) as these step exceptions meant for user, not the developer.

```py
await job.run()
```

!!! danger
    If you use `await` for `job.run()`, then this means no other jobs will be executed until previous job finishes. If that's the thing that you don't want, then you can use [asyncio](https://docs.python.org/3/library/asyncio.html){target=_blank} or alternatives.

[Read more in "Running Job"](../running_job){ .md-button }
