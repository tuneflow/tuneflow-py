from __future__ import annotations
from tuneflow_py.models.protos import song_pb2
from tuneflow_py.models.clip import Clip
from tuneflow_py.utils import db_to_volume_value, volume_value_to_db
import nanoid
TrackType = song_pb2.TrackType


class Track:
    def __init__(self, type: int | None = None,
                 song=None,
                 uuid=None,
                 instrument=None,
                 volume=db_to_volume_value(0),
                 solo=False,
                 muted=False,
                 rank=0,
                 pan=0, proto: song_pb2.Track | None = None) -> None:
        if song is None:
            raise Exception('song must be provided when creating track')
        self.song = song
        if proto is not None:
            self._proto = proto
            return
        self._proto = song_pb2.Track()
        self._proto.type = type
        if instrument is not None:
            self._proto.instrument.Merge(instrument)
        elif type == TrackType.MIDI_TRACK:
            self._proto.instrument.program = 0
            self._proto.instrument.is_drum = False
        self._proto.uuid = uuid if uuid is not None else Track._generate_track_id()
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

    def get_clip_at(self, clip_index: int):
        return Clip(proto=self._proto.clips[clip_index])

    def get_volume(self):
        '''
        Returns the fader position, ranging from 0 to 1.
        '''
        return self._proto.volume

    def get_volume_in_db(self):
        return volume_value_to_db(self._proto.volume)

    def get_pan(self):
        '''
        A pan value from -64 to 63
        '''
        return self._proto.pan

    def get_instrument(self):
        return self._proto.instrument

    def get_track_start_tick(self):
        if self.get_clip_count() == 0:
            return 0
        return self.get_clip_at(0).get_clip_start_tick()

    def get_track_end_tick(self):
        if self.get_clip_count() == 0:
            return 0
        return self.get_clip_at(self.get_clip_count() - 1).get_clip_end_tick()

    @staticmethod
    def _generate_track_id():
        return nanoid.generate()
