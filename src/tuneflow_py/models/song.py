from base64 import b64encode, b64decode
from tuneflow_py.models.protos import song_pb2


class Song:
    def __init__(self) -> None:
        self._proto = song_pb2.Song()
    
    def serialize(self):
        return b64encode(self._proto.SerializeToString()).decode('ascii') # type: ignore

    @staticmethod
    def _from_proto(proto: song_pb2.Song):
        song = Song()
        song._proto = proto
        return song

    @staticmethod
    def deserialize(serialized_song_string: str):
        song_proto = song_pb2.Song()
        song_proto.ParseFromString(b64decode(serialized_song_string)) # type: ignore
        return Song._from_proto(song_proto)