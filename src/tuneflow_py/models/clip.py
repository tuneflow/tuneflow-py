from __future__ import annotations

from tuneflow_py.models.protos import song_pb2
from tuneflow_py.models.note import Note
import nanoid

ClipType = song_pb2.ClipType

class Clip:

    def __init__(self, type=ClipType.MIDI_CLIP,
                 track=None,
                 uuid=None,
                 clip_start_tick=0,
                 clip_end_tick=8000,
                 proto: song_pb2.Clip | None = None) -> None:
        if proto is not None:
            self._proto = proto
            return
        self._proto = song_pb2.Clip()
        self.track = track
        self._proto.type = type
        self._proto.clip_start_tick = clip_start_tick
        self._proto.clip_end_tick = clip_end_tick
        self._proto.id = uuid if uuid is not None else Clip.generateClipIdInternal()
    
    def get_note_count(self):
        return len(self._proto.notes)

    def get_raw_notes(self):
        for note_proto in self._proto.notes:
            yield Note(proto=note_proto)
    
    def get_type(self) -> int:
        return self._proto.type
    
    def delete_note_at(self, index: int):
        self._proto.notes.pop(index)

    def get_audio_clip_data(self):
        return self._proto.audio_clip_data
    
    @staticmethod
    def generateClipIdInternal():
        return nanoid.generate(size=10)
    
    def get_clip_start_tick(self):
        return self._proto.clip_start_tick
    
    def get_clip_end_tick(self):
        return self._proto.clip_end_tick
