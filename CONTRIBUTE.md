# Contribute to `tuneflow-py`

## Overview

`tuneflow-py` is essentially a set of high-level data models built on top of [TuneFlow's data proto](https://github.com/tuneflow/tuneflow-proto). Each model class wraps a raw protocol buffer object, and provides high-level methods to read and modify the proto's data. Therefore, all write operations in a model class should write directly into the proto object, and read operations should return primitive value or a data model class wrapping a proto.

## Project setup

If you are developing a project that uses `tuneflow-py`, it is recommended to put `tuneflow-py` as a submodule alongside your repo in a larger parent repo, so that you can make changes to `tuneflow-py` without publishing a new version. For example, your directory structure could be:

```
---your_dev_folder
    |- ......
    |- tuneflow-py
    |- my-project
    |- ......
```
Note that if you decide to use `tuneflow-py` from a submodule, you should UNINSTALL `tuneflow-py` that was installed through pip or other tools, and then, add `tuneflow-py/src` into your `PYTHONPATH`. For example, in your terminal run:

``` bash
export PYTHONPATH=$PYTHONPATH:$PWD/tuneflow-py/src
```

## Testing

Tests are under the `test` directory, we use [pytest](https://docs.pytest.org/en/7.2.x/) to run tests and generate coverage reports. To run all the tests, run
``` bash
./scripts/test.sh
```

## Submit changes

To submit a change, create a separate branch, push it to github and then create a Pull Request.
