from tuneflow_py.models.protos import song_pb2
from tuneflow_py.models.clip import Clip
from tuneflow_py.utils import dbToVolumeValue
import nanoid

TrackType = song_pb2.TrackType


class Track:
    def __init__(self, type: int,
                 song,
                 uuid=None,
                 instrument=None,
                 volume=dbToVolumeValue(0),
                 solo=False,
                 muted=False,
                 rank=0,
                 pan=0, proto: song_pb2.Track | None = None) -> None:
        if proto is not None:
            self._proto = proto
            return
        self._proto = song_pb2.Track()
        self.song = song
        self._proto.type = type
        if instrument is not None:
            self._proto.instrument.Merge(instrument)
        elif type == TrackType.MIDI_TRACK:
            self._proto.instrument.program = 0
            self._proto.instrument.is_drum = False
        self._proto.uuid = uuid if uuid is not None else Track.generateTrackIdInternal()
        self._proto.volume = volume
        self._proto.solo = solo
        self._proto.muted = muted
        self._proto.rank = rank
        self._proto.pan = pan

    def get_clip_count(self):
        return len(self._proto.clips)

    def get_clips(self):
        for clip_proto in self._proto.clips:
            yield Clip(proto=clip_proto)

    def get_clip_at(self, clip_index):
        return Clip(proto=self._proto.clips[clip_index])

    @staticmethod
    def generateTrackIdInternal():
        return nanoid.generate()
