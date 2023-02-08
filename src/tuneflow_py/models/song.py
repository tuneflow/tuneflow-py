from base64 import b64encode, b64decode
from tuneflow_py.models.protos import song_pb2
from tuneflow_py.models.track import Track


class Song:
    def __init__(self, proto: song_pb2.Song | None = None) -> None:
        self._proto = proto if proto is not None else song_pb2.Song()

    def get_track_count(self):
        return len(self._proto.tracks)

    def get_tracks(self):
        for track_proto in self._proto.tracks:
            yield Track(proto=track_proto)

    def get_track_by_id(self, track_id: str) -> Track | None:
        for track_proto in self._proto.tracks:
            if track_proto.uuid == track_id:
                return Track(proto=track_proto)
        return None

    def serialize(self):
        # type: ignore
        return b64encode(self._proto.SerializeToString()).decode('ascii')

    @staticmethod
    def deserialize(serialized_song_string: str):
        song_proto = song_pb2.Song()
        song_proto.ParseFromString(
            b64decode(serialized_song_string))  # type: ignore
        return Song(proto=song_proto)

    def create_track(self, type: int,
                     index: int,
                     rank: int | None =None):
        new_track = Track(
            type=type, song=self, rank=rank if rank is not None else self.get_next_track_rank())
        self._proto.tracks.insert(index, new_track._proto)
        return new_track

    def get_next_track_rank(self):
        return 1 if len(self._proto.tracks) == 0 else max([track.rank for track in self._proto.tracks]) + 1
