from __future__ import annotations
from tuneflow_py.models.protos import song_pb2

AutomationTargetType = song_pb2.AutomationTarget.TargetType


class AutomationTarget:
    def __init__(
            self, type: AutomationTargetType | None = None, plugin_instance_id: str | None = None, param_id: str | None = None,
            proto: song_pb2.AutomationTarget | None = None) -> None:
        if proto is not None:
            self._proto = proto
        else:
            self._proto = song_pb2.AutomationTarget(
                type=type, plugin_instance_id=plugin_instance_id, param_id=param_id)

    def get_type(self):
        return self._proto.type

    def set_type(self, type: AutomationTargetType):
        self._proto.type = type

    def get_plugin_instance_id(self):
        return self._proto.audio_plugin_id

    def set_plugin_instance_id(self, plugin_instance_id: str | None = None):
        if plugin_instance_id is None:
            self._proto.ClearField("audio_plugin_id")
        else:
            self._proto.audio_plugin_id = plugin_instance_id

    def get_param_id(self):
        return self._proto.param_id

    def set_param_id(self, param_id: str | None = None):
        if param_id is None:
            self._proto.ClearField("param_id")
        else:
            self._proto.param_id = param_id

    def to_tf_automation_target_id(self):
        '''
        Gets a unique string id that identifies this target type.
        '''
        return AutomationTarget.encode_automation_target(
            self.get_type(),
            self.get_plugin_instance_id(),
            self.get_param_id())

    def __repr__(self) -> str:
        return str(self._proto)

    @staticmethod
    def encode_automation_target(
        target_type: AutomationTargetType,
        plugin_instance_id: str | None,
        param_id: str | None,
    ):
        if target_type == AutomationTargetType.AUDIO_PLUGIN:
            return f'{target_type}^^{plugin_instance_id}^^{param_id}'

        return f'{target_type}'

    @staticmethod
    def decode_automation_target(encoded_target: str):
        parts = encoded_target.split('^^')
        if len(parts) == 0:
            raise Exception(f'Invalid automation target id: {encoded_target}')

        type = int(parts[0])
        if len(parts) > 2:
            AutomationTarget(type, parts[1], parts[2])

        return AutomationTarget(type)
