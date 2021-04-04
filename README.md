<p align="center">
<img src="https://pyconduit.ysfchn.com/images/main.png" width="800">
</p>

# pyconduit

A simple workflow manager that executes pre-defined functions from user-defined workflow files. You ("developer") create the functions, and they ("users") will able to call the functions by typing its name and pass the required parameters.

It can be used to provide a "custom code evaluation" / "safe eval" feature to your users in your app. So they will only able to access functions that you allow. Users can also reference to other steps, set variables, and use standard functions in their workflow files.

pyconduit comes with Text, Math, Dictionary, List and Variable blocks like in Python's standard built-in functions. So you don't need to reinvent the wheel by writing these functions again.

It **does not** execute multiple functions in the same time. It executes functions _step by step_ (because that's a how "workflow" works), so next function will only execute **after** previous function has finished execution. Even if they are asynchronous / coroutines.

## Features

* Prevent access to a block for specific user. For example, if you have a block that makes a HTTP request, you can add a label to it, and pyconduit will not allow your users to use the function if job doesn't have that label too.

* Add step limits, max usage limit for a block per workflow (it can be changed for a specific job too).

* If you install [`pydantic` library](https://github.com/samuelcolvin/pydantic/) in your environment, pyconduit will use it automatically to enforce type hints / annotations in function parameters, so users won't able to send invalid type of values when parameter expects a specific type of value.

* Use [Context Tags](https://pyconduit.ysfchn.com/context_values) in the workflows to access variables, get the return value of previous steps and read object values with dotted path. For example, users can type `{: my_step_id :}` in the workflow to get the return value of `my_step_id` dynamically.

## Warning

As pyconduit can be used as "isolated space", you should be careful about functions that you enabled to user. (for example, you shouldn't make a function that allows users to get a global value in the runtime from their input). Also, even pyconduit blocks access to keys that starts or ends with underscore, there is no 100% warranty about security.

## Install

```
python -m pip install pyconduit
```

## Links

* [Quick Start](https://pyconduit.ysfchn.com/quick_start)
* [Documentation](https://pyconduit.ysfchn.com/)

## License

Source code is licensed under MIT license. You must include the license notice in all copies or substantial uses of the work.