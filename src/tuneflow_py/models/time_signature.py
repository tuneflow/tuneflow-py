from __future__ import annotations
from tuneflow_py.models.protos import song_pb2


class TimeSignatureEvent:
    def __init__(self, ticks: int | None = None, numerator: int | None = None, denominator: int | None = None,
                 proto: song_pb2.TimeSignatureEvent | None = None):
        if proto is not None:
            self._proto = proto
        else:
            self._proto = song_pb2.TimeSignatureEvent()
            self._proto.ticks = ticks
            self._proto.numerator = numerator
            self._proto.denominator = denominator

    def get_ticks(self) -> int:
        return self._proto.ticks

    def set_ticks(self, ticks: int):
        self._proto.ticks = ticks

    def get_numerator(self) -> int:
        return self._proto.numerator

    def set_numerator(self, numerator: int):
        self._proto.numerator = numerator

    def get_denominator(self) -> int:
        return self._proto.denominator

    def set_denominator(self, denominator: int):
        self._proto.denominator = denominator

    def __repr__(self) -> str:
        return str(self._proto)
