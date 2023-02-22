from __future__ import annotations
from tuneflow_py.models.protos import song_pb2


class Note:
    def __init__(self, pitch: int | None = None, velocity: int | None = None, start_tick: int | None = None, end_tick: int |
                 None = None, id: int | None = None, clip=None, proto: song_pb2.Note | None = None) -> None:
        '''
        IMPORTANT: Do not use the constructor directly, call createNote from clips instead.

        @param clip  If left empty, all clip-related methods will be no-op.
        '''
        self.clip = clip
        if proto is not None:
            self._proto = proto
        else:
            self._proto = song_pb2.Note()
            self._proto.pitch = pitch
            self._proto.velocity = velocity
            self._proto.start_tick = start_tick
            self._proto.end_tick = end_tick
            self._proto.id = id

    def get_id(self) -> int:
        return self._proto.id

    def get_pitch(self) -> int:
        return self._proto.pitch

    def get_velocity(self) -> int:
        return self._proto.velocity

    def set_velocity(self, velocity: int):
        self._proto.velocity = velocity

    def get_start_tick(self) -> int:
        return self._proto.start_tick

    def set_start_tick(self, start_tick: int):
        self._proto.start_tick = start_tick

    def get_end_tick(self) -> int:
        return self._proto.end_tick

    def set_end_tick(self, end_tick: int):
        self._proto.end_tick = end_tick

    def set_pitch(self, pitch: int):
        if not Note.is_valid_pitch(pitch):
            raise Exception("Invalid note pitch " + str(pitch))
        self._proto.pitch = pitch

    def adjust_pitch(self, pitch_offset: int):
        '''
        Adjust the pitch of a note.

        If the pitch of the note becomes invalid (less than 0 or greater than 127),
        it will be deleted from the clip.
        '''
        self._proto.pitch = self._proto.pitch + pitch_offset
        if not Note.is_valid_pitch(self._proto.pitch):
            self.delete_from_parent()

    def get_start_time(self) -> float:
        return self._proto.start_time

    def get_end_time(self) -> float:
        return self._proto.end_time

    def get_clip(self):
        return self.clip

    def adjust_left(self, offset_tick: int):
        '''
        Adjusts the start tick of the note by an offset.
        '''
        if (offset_tick == 0):
            return

        clip = self.clip
        if clip is not None:
            self.delete_from_parent()

        self._proto.start_tick += offset_tick
        if (not self.is_range_valid()):
            # Note is out of valid range, delete it
            # by not inserting it back.
            return

        if (clip is not None):
            clip._ordered_insert_note(self)

    def adjust_left_to(self, tick: int):
        '''
        Adjusts the start tick of the note to a given tick.
        '''
        self.adjust_left(tick - self.get_start_tick())

    def adjust_right(self, offset_tick: int):
        '''
        Adjusts the end tick of the note by an offset.
        '''
        self._proto.end_tick += offset_tick
        if (not self.is_range_valid()):
            self.delete_from_parent()

    def adjust_right_to(self, tick: int):
        '''
        Adjusts the end tick of the note to a given tick.
        '''
        self.adjust_right(tick - self.get_end_tick())

    def is_range_valid(self):
        return Note.is_note_range_valid(self._proto.start_tick, self._proto.end_tick)

    def move_note(self, offset_tick: int):
        '''
        Moves the note by a given offset in terms of ticks.

        This will not update the clip's boundaries.
        '''
        if (offset_tick == 0):
            return
        clip = self.clip
        if clip is not None:
            self.delete_from_parent()

        self._proto.start_tick = max(0, self._proto.start_tick + offset_tick)
        self._proto.end_tick = self._proto.end_tick + offset_tick
        if not self.is_range_valid():
            # Note is out of valid range, delete it
            # by not inserting it back.
            return
        if clip is not None:
            clip._ordered_insert_note(self)

    def delete_from_parent(self):
        if self.clip is None:
            return

        self.clip.delete_note(self)
        self.clip = None

    def equals(self, note: Note):
        '''
        Returns true if the notes should sound the same.

        NOTE: This does not check note Ids or the clips they belong to.
        '''
        return (
            self.get_start_tick() == note.get_start_tick() and
            self.get_end_tick() == note.get_end_tick() and
            self.get_pitch() == note.get_pitch() and
            self.get_velocity() == note.get_velocity()
        )

    def __repr__(self) -> str:
        return str(self._proto)

    @staticmethod
    def is_valid_pitch(pitch: int):
        return pitch >= 0 and pitch <= 127 and isinstance(pitch, int)

    @staticmethod
    def is_note_range_valid(start_tick: int, end_tick: int):
        return (
            end_tick >= 0 and
            start_tick <= end_tick
        )

    @staticmethod
    def is_note_velocity_valid(velocity: int):
        return velocity >= 0 and velocity <= 127
