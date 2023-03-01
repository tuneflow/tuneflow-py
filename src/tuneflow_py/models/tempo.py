from __future__ import annotations
from tuneflow_py.models.protos import song_pb2


class TempoEvent:
    def __init__(
            self, ticks: int | None = None, bpm: float | None = None, time: float | None = None, proto: song_pb2.TempoEvent |
            None = None):
        if proto is not None:
            self._proto = proto
        else:
            self._proto = song_pb2.TempoEvent()
            self._proto.ticks = ticks
            self._proto.bpm = bpm
            if time is not None:
                self._proto.time = time

    def get_ticks(self) -> int:
        return self._proto.ticks

    def set_ticks(self, ticks: int):
        self._proto.ticks = ticks

    def get_bpm(self) -> float:
        return self._proto.bpm

    def get_time(self) -> float:
        return self._proto.time

    def __repr__(self) -> str:
        return str(self._proto)
