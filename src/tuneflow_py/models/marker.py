from __future__ import annotations
from tuneflow_py.models.protos import song_pb2

StructureType = song_pb2.StructureMarker.StructureType


class StructureMarker:
    def __init__(self, song, tick:int=None, type: int | None = None,
                 custom_name: str | None = None, proto: song_pb2.StructureMarker | None = None) -> None:
        if song is None:
            raise Exception('song must be provided when creating a track')
        self.song = song
        if proto is not None:
            self._proto = proto
            return
        self._proto = song_pb2.StructureMarker()
        self._proto.type = type if type is not None else StructureType.INTRO
        self._proto.tick = tick if tick is not None else 0
        if type == StructureType.CUSTOM:
            self._proto.custom_name = custom_name if custom_name is not None else ''

    def get_tick(self) -> int:
        return self._proto.tick

    def set_tick(self, tick: int):
        self._proto.tick = tick

    def get_type(self) -> StructureType:
        return self._proto.type

    def set_type(self, type: StructureType):
        self._proto.type = type
    
    def set_custom_name(self, name: str):
        self._proto.custom_name = name
    
    def get_custom_name(self) -> str:
        return self._proto.custom_name