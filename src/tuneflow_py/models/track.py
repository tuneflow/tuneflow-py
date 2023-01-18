from tuneflow_py.models.protos import song_pb2
from tuneflow_py.models.clip import Clip

TrackType = song_pb2.TrackType

class Track:
    def __init__(self, proto: song_pb2.Track | None = None) -> None:
        self._proto = proto if proto is not None else song_pb2.Track()
    
    def get_clip_count(self):
        return len(self._proto.clips)
    
    def get_clips(self):
        for clip_proto in self._proto.clips:
            yield Clip(proto=clip_proto)
    
    def get_clip_at(self, clip_index):
        return Clip(proto=self._proto.clips[clip_index])
        