# Context Values

With using context values, users can access to useful job data and read inner values of variables in step parameters. Context values are always updated before executing each step, so they can get return values of previous steps.

pyconduit currently has these context values but [it can be overriden by developer][pyconduit.Conduit.create_contexts]. 

|               Key               |     Type     |     Description      |
|:--------------------------------|:-------------|:---------------------|
| job.name       | `str` or `None` | Name of the job which provided when creating a [`Conduit`][pyconduit.conduit.Conduit]. |
| job.success      | `bool` or `None` | Returns a boolean about previous execution has exited without any errors. `True` if previous execution has exited without any errors. `False` if previous execution has exited with any errors. `None` if job has never executed yet. |
| job.parameters     | `dict` | Locals are extra parameters that passed in this job. It can contain any dictionary. |
| job.id      | `str` or `None` | An ID that used to identify the job. |
| job.variables     | `dict` | A dictionary of variables that created in the job. It can be edited and read, users can also use blocks from "Variable" category to create variables in runtime. |
| steps.X.result    | anything | Gets the return value of the step (by step ID). If step is not executed yet, this will be `None`. |
| steps.X.id    | `str` | Gets the ID of the step (by step ID). |
| steps.X.status.name    | `str` | Gets the status name of the step (by step ID). |
| steps.X.status.value    | `int` | Gets the status value of the step (by step ID). |
| steps.X.position    | `int` | Gets the step position of the step (by step ID). Position index starts with 1.  |
| steps.X.action    | `str` | Gets the action of the step (by step ID). For example: `TEXT.JOIN` |
| steps.X.block.category    | `str` or `None` | Gets the category name of the block that connected to the step (by step ID). For example: `TEXT` |
| steps.X.block.name    | `str` | Gets the block name of the block that connected to the step (by step ID). For example: `JOIN`  |
| steps.X.parameters    | `dict` | Gets the parameters of the step (by step ID). Note that this doesn't resolve the references, so context values appear as it looks. |

---

## Tags

To reference contexts values in step parameters, insert key in the tag like `{% job.name %}`. pyconduit will resolve to its value when you start running the job.

### Getting context values in parameters

You can add context tags in the `parameters` of the step payload. You can also add tags to parameter keys, not only values.

```json
{
    "action": "TEXT.JOIN",
    "parameters": {
        "text1": "{% job.name %}",
        "text2": " gives the name of the job."
    }
}
```

Getting the return value of one of the previous steps:

```json
[
    {
        "action": "TEXT.JOIN",
        "id": "my_step",
        "parameters": {
            "text1": "{% job.name %}",
            "text2": " is running right now!"
        }
    },
    {
        "action": "TEXT.JOIN",
        "parameters": {
            "text1": "step #{% steps.my_step.position %} returned ",
            "text2": "{% steps.my_step.result %}"
        }
    }
]
```

### Dotted keys

You can use dots for accessing inner objects of values. You can get a list item by its index or you can get inner keys of dictionary.

```
["a", "b", "c"] -> {% value.1 %} -> "b"
{"foo": "bar"} -> {% value.foo %} -> "bar"
```

=== "List"

    ```
    ["first", "second", "third"]
    ```

    ```json
    {
        "action": "TEXT.JOIN_LIST",
        "parameters": {
            "list": [
                "{% value.1 %}",
                " equals to 2nd."
            ]
        }
    }
    ```

=== "Dictionary"

    ```
    {
        "elements": [
            { "child": {"inner": "data"} }
        ]
    }
    ```

    ```json
    {
        "action": "TEXT.JOIN_LIST",
        "parameters": {
            "list": [
                "{% elements.0.child.inner %}",
                " equals to 'data'."
            ]
        }
    }
    ```

### Shortcut tags

There are shortuct tags for accessing steps, variables and local values instead of typing it in long form.

|     Shortcut     |       Equals     |    Description   | 
|:----------------:|:----------------:|:-----------------|
| `{: my_step :}`  | `{% steps.my_step.result %}` | Step result values |
| `{# my_variable #}` | `{% job.variables.my_variable %}` | Job variables |
| `{< my_parameter >}` | `{% job.parameters.my_parameter %}` | Job local values |

=== "Without shortcuts"

    ```json
    {
        "action": "TEXT.JOIN",
        "parameters": {
            "text1": "variable {% job.variables.my_variable %} and",
            "text2": "a step result {% steps.my_step.result %}"
        }
    }
    ```

=== "With shortcuts"

    ```json
    {
        "action": "TEXT.JOIN",
        "parameters": {
            "text1": "variable {# my_variable #} and",
            "text2": "a step result {: my_step :}"
        }
    }
    ```


### Inserting in other values

You can also access context values in lists, dictionaries and strings.

=== "String"

    ```json
    {
        "action": "TEXT.JOIN",
        "parameters": {
            "text1": "{% job.name %} gives the",
            "text2": "name of the job."
        }
    }
    ```

=== "List"

    ```json
    {
        "action": "TEXT.JOIN_LIST",
        "parameters": {
            "list": [
                "{% job.name %}",
                " gives the",
                " name of the job."
            ]
        }
    }
    ```

=== "Dictionary"

    ```json
    {
        "action": "DICTIONARY.CREATE",
        "parameters": {
            "foo": {
                "bar": {
                    "{% job.name %}": "gives the name of the job."
                }
            }
        }
    }
    ```


### Dynamic keys (Tags in tags)

You can also access keys dynamically by adding tags in the tags.

```json
{
    "action": "DICTIONARY.CREATE",
    "parameters": {
        "foo": "Just testing {% job.variables.{% job.name %} %}"
    }
}
```
