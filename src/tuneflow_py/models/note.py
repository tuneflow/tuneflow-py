from __future__ import annotations
from tuneflow_py.models.protos import song_pb2


class Note:
    def __init__(self, proto: song_pb2.Note | None = None) -> None:
        self._proto = proto if proto is not None else song_pb2.Note()

    def get_pitch(self) -> int:
        return self._proto.pitch

    def get_velocity(self) -> int:
        return self._proto.velocity

    def get_start_tick(self) -> int:
        return self._proto.start_tick

    def get_end_tick(self) -> int:
        return self._proto.end_tick

    def set_pitch(self, pitch: int):
        if not Note.is_valid_pitch(pitch):
            raise Exception("Invalid note pitch " + str(pitch))
        self._proto.pitch = pitch

    def get_start_time(self) -> float:
        return self._proto.start_time

    def get_end_time(self) -> float:
        return self._proto.end_time

    @staticmethod
    def is_valid_pitch(pitch: int):
        return pitch >= 0 and pitch <= 127 and isinstance(pitch, int)
