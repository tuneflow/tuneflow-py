from tuneflow_py.descriptors.text import LabelText
from tuneflow_py.descriptors.common import PluginInfo
from tuneflow_py.descriptors.param import ParamDescriptor
from tuneflow_py.descriptors.audio_plugin import AudioPluginDescriptor
from typing import Optional, Any, List, Dict
from tuneflow_py.models.song import Song


class ReadAPIs:
    '''
    Read-only APIs used in `init` and `run` methods of a plugin.
    '''

    def get_system_locale(self):
        raise Exception("Not implemented")

    def translate_label(self, label_text: LabelText):
        raise Exception("Not implemented")

    def serialize_song(self, song: Song):
        raise Exception("Not implemented")

    def deserialize_song(self, encoded_song: str):
        raise Exception("Not implemented")

    def get_available_audio_plugins(self) -> List[AudioPluginDescriptor]:
        raise Exception("Not implemented")


class TuneflowPlugin:
    '''
    The base class of a plugin.

    All plugins should be a sub-class of this plugin in order to run in the pipeline.
    '''

    def __init__(self) -> None:
        self.params_result_internal = {}

    @staticmethod
    def provider_id() -> str:
        """
        The unique id to identify the plugin provider.

        For example:
        `friday-core`, `some-corp`, etc.
        """
        raise Exception("provider_id must be overwritten.")

    @staticmethod
    def plugin_id() -> str:
        '''
        The unique plugin id under the provider's namespace.

        For example:
        `melody-extractor`, `tune-analyzer`, etc.
        '''
        raise Exception("plugin_id must be overwritten.")

    @staticmethod
    def provider_display_name() -> LabelText:
        '''
        The display name of the provider.
        '''
        raise Exception("provider_display_name must be overwritten.")

    @staticmethod
    def plugin_display_name() -> LabelText:
        '''
        The display name of the plugin.
        '''
        raise Exception("plugin_display_name must be overwritten.")

    @staticmethod
    def plugin_description() -> Optional[LabelText]:
        '''
        The description of this plugin.
        '''
        return None

    @staticmethod
    def plugin_info() -> Optional[PluginInfo]:
        return None

    @staticmethod
    def allow_reset():
        '''
        Whether to allow users to reset all parameters of this plugin.
        '''
        return False

    def init(self, song: Song, read_apis: ReadAPIs):
        '''
        Initializes the plugin instance.

        Override this method to initialize your plugin before it starts running.
        '''
        pass

    def params(self) -> Dict[str, ParamDescriptor]:
        '''
        Specify params to get from user input.

        Param input widgets will be displayed on the UI, and the inputs will be collected and fed into @run method.

        If you don't need any param, return `{}`;
        '''
        return {}

    def allow_manual_apply_adjust(self):
        '''
        Whether the user can manually apply this plugin and go back to adjust it.
        Enable this when you want the user to frequently toggle this plugin on and off
        to see the difference.

        For example: A plugin that divides a track into two, you want the user to
        easily switch between the plugin is on or off to see what's going on.
        '''
        return False

    def run(self, song: Song, params: Dict[str, Any], read_apis: ReadAPIs):
        '''
        The main logic here.

        Args:
            `song`: The song that is being processed. You can directly modify the song
                by calling its methods.
            `params`: The results collected from user input specified by the `params` method.
        '''
        pass

    # =====================================
    # NO OVERWRITE BELOW
    # =====================================

    @classmethod
    def create(cls, song: Song, read_apis: ReadAPIs):
        plugin = cls()
        plugin.reset_internal()
        plugin.init(song, read_apis=read_apis)
        return plugin

    def reset_internal(self):
        params = self.params()
        for key in params.keys():
            param_descriptor = params[key]
            self.params_result_internal[key] = param_descriptor["defaultValue"]
