from __future__ import annotations
from tuneflow_py.models.protos import song_pb2
from tuneflow_py.models.note import Note
from nanoid import generate as generate_nanoid

ClipType = song_pb2.ClipType


class Clip:
    def __init__(self, proto: song_pb2.Clip | None = None) -> None:
        self._proto = proto if proto is not None else song_pb2.Clip()

    def get_note_count(self):
        return len(self._proto.notes)

    def get_raw_notes(self):
        for note_proto in self._proto.notes:
            yield Note(proto=note_proto)

    def get_raw_note_at(self, index: int):
        return Note(proto=self._proto.notes[index])

    def get_type(self) -> int:
        return self._proto.type

    def delete_note_at(self, index: int):
        self._proto.notes.pop(index)

    def get_clip_start_tick(self) -> int:
        return self._proto.clip_start_tick

    def get_clip_end_tick(self) -> int:
        return self._proto.clip_end_tick

    @staticmethod
    def is_note_in_clip(
        note_start_tick: int,
        note_end_tick: int,
        clip_start_tick: int,
        clip_end_tick: int,
    ):
        '''
        Note is in the clip when:
        * The note starts at or after the clip start.
        * The note has overlapping part with the clip.
        * The overlapping part is greater than 1 tick, i.e. the note does not start from the end of the clip or end at the start of the clip.
        '''
        # If the clip starts at 0, notes that start before 0 will start at 0.
        return (
            (note_start_tick >= clip_start_tick or (clip_start_tick == 0 and note_start_tick <= 0)) and
            note_start_tick < clip_end_tick and
            note_end_tick > note_start_tick
        )

    @staticmethod
    def _generate_clip_id():
        return generate_nanoid(size=10)
