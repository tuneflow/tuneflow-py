# TuneFlow Python SDK

![TuneFlow Screenshots](docs/images/tuneflow_wall_thin.jpg)

[![Build Status](https://dev.azure.com/zeostudio/tuneflow-public/_apis/build/status/tuneflow.tuneflow-py?branchName=main)](https://dev.azure.com/zeostudio/tuneflow-public/_build/latest?definitionId=32&branchName=main)
[![Code Coverage](https://img.shields.io/azure-devops/coverage/zeostudio/tuneflow-public/32/main?logo=azure-pipelines)](https://dev.azure.com/zeostudio/tuneflow-public/_build/latest?definitionId=32&branchName=main)
[![PyPI](https://img.shields.io/pypi/v/tuneflow-py?color=blue&label=tuneflow-py&logo=pypi)](https://pypi.org/project/tuneflow-py/)
[![Discord](https://img.shields.io/discord/1076012137161424906?color=%237289da&logo=discord)](https://discord.com/channels/1076012137161424906/1076012755250851860)
![License](https://img.shields.io/github/license/tuneflow/tuneflow-py)

## What is `TuneFlow` and `tuneflow-py`?

[TuneFlow](https://www.tuneflow.com) is a next-gen DAW that aims to boost music making productivity through the power of AI. Unlike traditional DAWs, TuneFlow has a plugin system designed to facilitate music production in almost all areas, including but not limited to **song writing**, **arrangement**, **automation**, **mixing**, **transcription**...... You can easily write your own algorithms or integrate your AI models directly into the song-making process. `tuneflow-py` is the Python SDK of TuneFlow plugins.

## Installation

```bash
pip install tuneflow-py
```

## Prefer another language?

Check out the SDKs in other languages:

- **Typescript**: https://www.github.com/tuneflow/tuneflow
- Other: Contributions welcome!

## Getting started

The core idea of TuneFlow's plugin system is that you only care about the data model, NOT the implementation. A plugin's only goal is to modify the song, and the DAW will get the modified result and apply changes automatically. Below is an illustration:

![Plugin Flow](docs/images/pipeline_flow_en.jpg)

A python plugin bundle consists of 2 components: The bundle file and the plugin files.

### Bundle file (`bundle.json`)

The bundle file, which we usually name it `bundle.json`, contains the information of the plugins in this bundle. The information here will be shown to the users before they need to load the code of your plugin.

An example manifest file looks like this.

```json
{
  "plugins": [
    ......,
    {
      "providerId": "my-provider-id",
      "providerDisplayName": "My Provider Name",
      "pluginId": "my-plugin-id",
      "pluginDisplayName": "My Plugin Name",
      "version": "1.0.0",
      "minRequiredDesktopVersion": "1.8.3",
      "options": {
        "allowReset": false
      }
    },
    ......
  ]
}

```

### Plugin code (`plugin.py`)

Under the plugin's root folder we need to create a `plugin.py` file, which is where we define the plugin code. You can put other source code under the same folder, too. When TuneFlow runs the plugin, it adds the plugin's root folder to the `PYTHONPATH`.

A barebone python plugin may look like this:

```python
from tuneflow_py import TuneflowPlugin, Song, ParamDescriptor


class HelloWorld(TuneflowPlugin):
    @staticmethod
    def provider_id():
        return "andantei"

    @staticmethod
    def plugin_id():
        return "hello-world"

    @staticmethod
    def params(song: Song) -> dict[str, ParamDescriptor]:
        return {}

    @staticmethod
    def run(song: Song, params: dict[str, Any]):
        print("Hello World!")

```

> **Note:** All methods here are static methods. This is by design: The entire plugin should be stateless -- the outcome of one plugin execution is only determined by the input and NOT by any internal states of the plugin itself.

When writing a plugin, our main focus is in `params` and `run`.

### `params`

This is where you specify the input parameters you want from the user or from the DAW. It will be processed by the DAW and generate your plugin's UI widgets.

You can optionally use `song` to get some additional information about the project's current snapshot, so that you can customize your params. For example, if you have a list of presets that applies to different time signatures, you can use `init` to read the current song's time signature and filter out those options that don't work for the song.

### `run`

Called by the DAW when the user actually runs the plugin by hitting the **Apply`** button.

Here is where you implement your main logic. The method takes in the current song snapshot (`song: Song`), the params that are actually provided by the user or the DAW (`params`).

## Run your plugin

To debug and run your plugin locally, you can use `tuneflow-devkit-py`. For more documentation, visit: https://github.com/tuneflow/tuneflow-devkit-py

## Examples

For a comprehensive of example plugins, check out https://www.github.com/tuneflow/tuneflow-py-demos

## Contribute

Checkout [contribution guidelines](./CONTRIBUTE.md).

## Resources

[TuneFlow Website](https://tuneflow.com)

[Typescript SDK](https://www.github.com/tuneflow/tuneflow)
