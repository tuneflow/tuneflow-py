from tuneflow_py.descriptors.text import LabelText
from tuneflow_py.descriptors.param import ParamDescriptor
from tuneflow_py.descriptors.audio_plugin_descriptor import AudioPluginDescriptor
from typing import Any, List, Dict
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
    def params(song: Song, read_apis: ReadAPIs) -> Dict[str, ParamDescriptor]:
        '''
        Specify params to get from user input.

        Param input widgets will be displayed on the UI, and the inputs will be collected and fed into @run method.

        You can also optionally use `song` and `read_apis` to adjust your params based on the current snapshot.

        If you don't need any param, return `{}`;
        '''
        return {}

    @staticmethod
    def run(song: Song, params: Dict[str, Any], read_apis: ReadAPIs):
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

    @staticmethod
    def _get_default_params(param_config):
        param_result = {}
        for key in param_config.keys():
            param_descriptor = param_config[key]
            param_result[key] = param_descriptor["defaultValue"]
        return param_result
