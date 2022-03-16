# Running Job

When you run the [`Conduit`][pyconduit.conduit.Conduit], all steps will be iterated and underlying functions will be executed. If a function raises and exception, Conduit will catch it and store the exception in the `return_value` of [`ConduitStep`][pyconduit.step.ConduitStep] object.

To run the job you can execute [`Conduit.run()`][pyconduit.conduit.Conduit.run], if you want to execute jobs one by one then you can use `await` keyword, however this will suspend your app until it completes executing all steps.

Before Conduit executes the underlying function, it performs several checks to verify if step has configured correctly (If it has a duplicate ID, if the block doesn't exists and so on.) and changes the status of the step from one of [`NodeStatus`](#NodeStatus) enum.

## `NodeStatus`

|    Name    |    Value   |  Is used for raised exceptions in the block? |   Description   |
|:-----------|:-----------|:-----------:|:----------------|
| NONE | -1 | | The step has not executed yet. This will be set as first value to every created step. |
| DONE | 0 | | Step has executed without any errors. |
| SKIPPED | 100 | | This step has skipped because of previous failed steps. |
| UNHANDLED_EXCEPTION | 101 | ✅ | All general unexpected errors in the block. |
| BLOCK_NOT_FOUND | 102 |  | The action / block doesn't exists. |
| INVALID_ARGUMENT | 103 | ✅ | Returned if block raised an `ValueError`. |
| DUPLICATE_STEP_IDS | 104 | | Duplicate step IDs has detected. |
| FORBIDDEN_BLOCK | 105 | | This block is forbidden to use because of missing tags in the job. |
| INVALID_TYPE | 107 | | Returned if user passed a type of value that doesn't match with the parameter type. If pydantic has not installed, then this will not be used as there will be no type validation without pydantic. |
| IF_CONDITION_FAILED | 110 | | `if_condition` of the step returned `False`. |
| KILLED_MANUALLY | 111 | ✅ | An exception raised manually to stop the job. |

## Events

If you want Conduit to execute the specified function when a step updates or/and job finishes, you can use `on_step_update` and `on_job_finish`.

```py
job = Conduit()

job.on_step_update = lambda j, step: print(step.id, "has finished!")
```

You can also provide a `async` function.

```py
job = Conduit()

async def done(j, step):
    await do_something(...)

job.on_step_update = done
```