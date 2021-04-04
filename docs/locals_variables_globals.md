# Locals, Variables & Globals

|       Type        |    Can be used for    |   Can users write to it   |   Can users read from it   |
|:------------------|:-----------------------|:--------------------:|:------------------:|
| [Globals](#globals) | Values that needs to be filled by developer such as database objects | ❌ | ❌ |
| [Variables](#variables)  | Temporary key/value storage that lasts until job finishes | ✔ | ✔ |
| [Locals](#locals)  | Storing API results so users can get data only what they want from it | ❌ | ✔ |

---

## Globals

Globals are values that passed to positional-only or positional-or-keyword arguments to the block. To define a global value, use `global_values` attribute in [`Conduit`][pyconduit.conduit.Conduit] object.

```py
db = ...
contact_url = ...

job = Conduit(global_values = {
    "database": db,
    "contact_url": contact_url
})
```

After defining the global values, you can get these values in the ConduitBlocks by adding their names before keyword-only arguments.

```py
@ConduitBlock.make
def create_feedback(contact_url : str, *, message : str):
    """
    Posts a message to the contact url.
    """
    post(contact_url, message)
```

### Using same parameter name for both arguments

You can add double underscores to positional parameters if you want users to use `contact_url` in their payloads too. You don't need to add underscores too in `global_values` because underscores will be deleted already.

```py
@ConduitBlock.make
def create_feedback(contact_url__ : str, *, contact_url : str = None):
    """
    Posts a message to the contact url. If user passed their own contact urls,
    it will be used instead.
    """
    if contact_url:
        post(contact_url, message)
    else:
        post(contact_url__, message)

db = ...
contact_url = ...

job = Conduit(global_values = {
    "database": db,
    "contact_url": contact_url
    # Note that this is still `contact_url` instead of `contact_url__`.
})
```

It is not needed to have a double underscore at the end for positional parameters, but it is recommended if you want your users to use `contact_url` as parameter name in `**kwargs` or keyword arguments, so you can have two parameters with same name. 

---

## Variables

Variables are temporary key/value storage that lasts until job lifecycle. They can be read and created by both developer and user. As these values can be read and edited by users, don't pass any sensitive data here.

To define a new variable as developer, just use `variables` attribute of [`Conduit`][pyconduit.conduit.Conduit].

```py
job = Conduit(variables = {
    "my_variable": "Yay!"
})
```

Then users can read it by using [Context Values Tags](../context_values#tags) in their payloads.

```json
{
    "action": "TEXT.JOIN",
    "parameters": {
        "text1": "New message:",
        "text2": "{# my_variable #}"
    }
}
```

Users can also edit variables and create their own variables with [Variable blocks][pyconduit.categories.variable.Variable]

```json
{
    "action": "VARIABLE.SET",
    "parameters": {
        "name": "my_variable",
        "value": "Wow!"
    }
}
```

---

## Locals

Locals are values that can be read by users but not edited. This can be useful if you called an API and want users to use the result in a way that they want. For example your app just called an API and returned some results like this:

```json
{
    "colors": [
        {
            "color": "black",
            "category": "hue",
            "type": "primary",
            "code": {
                "rgba": [255,255,255,1],
                "hex": "#000"
            }
        },
        {
            "color": "white",
            "category": "value",
            "code": {
                "rgba": [0,0,0,1],
                "hex": "#FFF"
            }
        }
    ]
}
```

And if you want users to be able to use this data freely, add it to `local_values` attribute of [`Conduit`][pyconduit.conduit.Conduit].

```py
job = Conduit(local_values = {
    "colors": colors_dict
})
```

Then users can read it by using [Context Values Tags](../context_values#tags) in their payloads.

```json
{
    "action": "TEXT.JOIN",
    "parameters": {
        "text1": "First color from local values:",
        "text2": "{< colors.0.code.hex >}"
    }
}
```
