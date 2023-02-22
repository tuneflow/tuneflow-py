from __future__ import annotations
from tuneflow_py.models.protos import song_pb2
from tuneflow_py.utils import get_audio_plugin_tuneflow_id, are_tuneflow_ids_equal, are_tuneflow_ids_equal_ignore_version, decode_audio_plugin_tuneflow_id
from nanoid import generate as generate_nanoid


class AudioPlugin:
    def __init__(self,
                 name: str | None = None,
                 manufacturer_name: str | None = None,
                 plugin_format_name: str | None = None,
                 plugin_version: str | None = None,
                 proto: song_pb2.AudioPluginInfo | None = None
                 ):
        '''
        DO NOT call the constructor directly, use Track.create_audio_plugin(tf_id: str) instead.
        '''
        if proto is not None:
            self._proto = proto
        else:
            self._proto = song_pb2.AudioPluginInfo()
            self._proto.tf_id = get_audio_plugin_tuneflow_id(
                manufacturer_name=manufacturer_name, plugin_format_name=plugin_format_name, plugin_name=name,
                plugin_version=plugin_version)
            self._proto.is_enabled = True
            self._proto.local_instance_id = AudioPlugin._generate_audio_plugin_instance_id()

    def get_tuneflow_id(self):
        '''
        A unique id that TuneFlow uses to identify the type of plugin
        '''
        return self._proto.tf_id

    def matches_tf_id(self, tf_id: str):
        '''
        Exactly matches the plugin type specified by the tf_id.
        '''
        return are_tuneflow_ids_equal(tf_id, self.get_tuneflow_id())

    def matches_tf_id_ignore_version(self, tf_id: str):
        '''
        Similar to matches_tf_id but does not check version.
        '''
        return are_tuneflow_ids_equal_ignore_version(tf_id, self.get_tuneflow_id())

    def get_instance_id(self):
        '''
        A unique id to identify the plugin instance.
        '''
        return self._proto.local_instance_id

    def to_json(self):
        audio_plugin_info = decode_audio_plugin_tuneflow_id(self.get_tuneflow_id())
        return {
            "name": audio_plugin_info["name"],
            "manufacturer_name": audio_plugin_info["manufacturer_name"],
            "plugin_format_name": audio_plugin_info["plugin_format_name"],
            "plugin_version": audio_plugin_info["plugin_version"],
            "is_enabled": self._proto.is_enabled,
        }

    def set_is_enabled(self, is_enabled: bool):
        self._proto.is_enabled = is_enabled

    def get_is_enabled(self):
        return self._proto.is_enabled

    def set_base64_states(self, base64_states: str | None = None):
        if base64_states is None:
            self._proto.ClearField("base64_states")
        else:
            self._proto.base64_states = base64_states

    def get_base64_states(self):
        return self._proto.base64_states

    def __repr__(self) -> str:
        return str(self._proto)

    @staticmethod
    def _generate_audio_plugin_instance_id():
        return generate_nanoid(size=10)

    DEFAULT_SYNTH_TFID = get_audio_plugin_tuneflow_id('TuneFlow', 'VST3', 'TFSynth', '1.0.0')
