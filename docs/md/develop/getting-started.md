# Plugin Development 101

The core idea of TuneFlow's plugin system is that you only care about the data model, NOT the implementation.

## Lifecycle of a Plugin

A plugin's only goal is to modify the song, and the DAW will get the modified result and apply changes automatically. Below is an illustration:

![Plugin Flow](../../images/pipeline_flow_en.jpg)

The lifecycle of a plugin consists of 5 stages: **Installed, Created, Cunning and Finished**.

* `Installed` This is when the plugin has been installed to the plugin inventory but hasn't been triggered by the user.

* `Created` This is when the user triggers the plugin from the plugin inventory or a right-click menu. At this point, the plugin is added to the editing panel, but the params that are needed from the user or the DAW are not fulfilled yet.

* `Running` This is when the user hits the **Apply** button of the plugin control panel(or if all params have been fulfilled at creation and no Apply button is specified for this plugin) and starts running the plugin.

* `Finished` This is after the plugin has modified the song snapshot and the DAW has created a new snapshot based on the modified result. The plugin is then destroyed and resources are freed.

* `Error` This happens if the plugin encountered error during the `Running` stage.

### Stage Transitions

The basic stage transition follows the `installed` -> `created` -> `running` -> `finished` order. But there are two exceptions:

1. If the plugin encountered error during the `running` stage, the status bar turns red and it transitions into the `error` stage.

2. If the user choose to adjust a plugin at `finished` or `error` stage, it will go back to the `created` stage.

## Defining a Plugin

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

This is called when the user triggers the plugin (i.e. `installed` -> `created`). And you should specify the input parameters that you want from the user or from the DAW. It will be processed by the DAW and generate your plugin's UI widgets.

You can optionally use `song` to get some additional information about the project's current snapshot, so that you can customize your params. For example, if you have a list of presets that applies to different time signatures, you can use `init` to read the current song's time signature and filter out those options that don't work for the song.

### `run`

Called by the DAW when the user actually runs the plugin by hitting the **Apply** button. (i.e. `created` -> `running`)

Here is where you implement your main logic. The method takes in the current song snapshot (`song: Song`), the params that are actually provided by the user or the DAW (`params`).


## Next

Now we understood the basic lifecycle and structure of a plugin, let's actually start building one! Continue to read [Run and Debug Your Plugin Locally](./devkit.md)