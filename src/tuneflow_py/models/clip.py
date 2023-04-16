from __future__ import annotations
from tuneflow_py.descriptors.clip_descriptor import AudioClipData
from tuneflow_py.models.protos import song_pb2
from tuneflow_py.models.note import Note
from tuneflow_py.utils import lower_than, greater_than, greater_equal
from nanoid import generate as generate_nanoid
from typing import List
from types import SimpleNamespace


ClipType = song_pb2.ClipType


class Clip:
    def __init__(self, song, type: int | None = None, clip_start_tick: int | None = None, id: str | None = None, track=None,
                 clip_end_tick: int | None = None, audio_clip_data: AudioClipData | None = None, proto: song_pb2.Clip |
                 None = None) -> None:
        '''
        A clip is a piece in a track, and it contains notes and the clip range.
        One track can contain one or many non-overlapping clips.

        IMPORTANT: Do not use the constructor directly, call `createClip` from tracks instead.

        @param song The song that the clip belongs to, should always be provided.
        @param track If the clip is dettached from any track, this field is going to be None.
        @param clip_start_tick Inclusive start tick.
        @param clip_end_tick Inclusive end tick.
        @param audio_clip_data Audio related data if the clip type is AUDIO_CLIP.
        '''
        self.song = song
        self.track = track
        self._next_note_id = None
        if proto is not None:
            self._proto = proto
            return
        self._proto = song_pb2.Clip()
        self._proto.id = id if id is not None else Clip._generate_clip_id()
        self._proto.type = type
        if type == ClipType.AUDIO_CLIP:
            if audio_clip_data is None:
                raise Exception(
                    'Audio clip data must be provided for audio clips.')

            if "audio_file_path" in audio_clip_data and audio_clip_data["audio_file_path"] is not None and audio_clip_data["audio_file_path"] != "":
                self._proto.audio_clip_data.audio_file_path = audio_clip_data["audio_file_path"]
            if "audio_data" in audio_clip_data and audio_clip_data["audio_data"] is not None:
                self._proto.audio_clip_data.audio_data.format = audio_clip_data["audio_data"]["format"]
                self._proto.audio_clip_data.audio_data.data = audio_clip_data["audio_data"]["data"]
            self._proto.audio_clip_data.start_tick = audio_clip_data["start_tick"]
            self._proto.audio_clip_data.duration = audio_clip_data["duration"]
            if "pitch_offset" in audio_clip_data:
                self._proto.audio_clip_data.pitch_offset = audio_clip_data["pitch_offset"]
            if "speed_ratio" in audio_clip_data:
                self._proto.audio_clip_data.speed_ratio = audio_clip_data["speed_ratio"]

            clip_start_tick = max(
                clip_start_tick, audio_clip_data["start_tick"]) if clip_start_tick is not None else audio_clip_data["start_tick"]
            audio_end_tick = self.get_audio_end_tick()
            if (clip_end_tick is None or audio_end_tick < clip_end_tick):  # type:ignore
                clip_end_tick = audio_end_tick

            self._proto.clip_start_tick = clip_start_tick
            self._proto.clip_end_tick = clip_end_tick
        elif (type == ClipType.MIDI_CLIP):
            self._proto.clip_start_tick = clip_start_tick
            if clip_end_tick is None:
                raise Exception(
                    'clip end tick must be provided when creating MIDI clip.')

            self._proto.clip_end_tick = clip_end_tick

    def get_id(self):
        return self._proto.id

    def get_track(self):
        return self.track

    def get_audio_end_tick(self) -> int | None:
        '''
        Gets the current clip audio's end tick.

        Returns None if the clip is not audio clip or audio clip data is missing.
        '''
        if self.get_type() != ClipType.AUDIO_CLIP or not self.has_audio_clip_data():
            return None

        duration = self.get_audio_duration()
        if duration is None:
            return None

        audio_start_time = self.song.tick_to_seconds(
            self._proto.audio_clip_data.start_tick)
        return self.song.seconds_to_tick(audio_start_time + duration)

    def get_duration(self):
        '''
        Duration from the clip start to clip end, in seconds.
        '''
        return self.song.tick_to_seconds(
            self.get_clip_end_tick()) - self.song.tick_to_seconds(
            self.get_clip_start_tick())

    def get_audio_duration(self) -> float | None:
        '''
        Gets the STRETCHED, FULL audio duration if the clip is AUDIO_CLIP, this takes speed ratio into consideration.

        Returns None if the clip is not AUDIO_CLIP or audio clip data is missing.
        '''
        if self.get_type() != ClipType.AUDIO_CLIP or not self.has_audio_clip_data():
            return None
        return self._proto.audio_clip_data.duration / self.get_audio_speed_ratio()

    def get_raw_audio_duration(self) -> float | None:
        '''
        Gets the UNSTRETCHED, FULL audio duration if the clip is AUDIO_CLIP, this DOES NOT consider speed ratio.

        Returns undefined if the clip is not AUDIO_CLIP or audio clip data is missing.
        '''
        if self.get_type() != ClipType.AUDIO_CLIP or not self.has_audio_clip_data():
            return None
        return self._proto.audio_clip_data.duration

    def get_audio_speed_ratio(self) -> float:
        if self.get_type() != ClipType.AUDIO_CLIP or not self.has_audio_clip_data() or self._proto.audio_clip_data.speed_ratio is None or self._proto.audio_clip_data.speed_ratio == 0:
            return 1
        return self._proto.audio_clip_data.speed_ratio

    def time_stretch_from_clip_left(self, to_left_tick: int, resolve_clip_conflict=True):
        '''
        Time-stretch the clip by adjusting the start tick of the clip.

        NOTE: This could delete the clip if the clip range becomes empty after
        this call.

        @param `to_left_tick` The new start tick to stretch the clip to.
        '''
        if (to_left_tick >= self.get_clip_end_tick()):
            self.delete_from_parent(delete_associated_track_automation=True)
            return
        stretch_factor = (self.get_clip_end_tick(
        ) - to_left_tick) / (self.get_clip_end_tick() - self.get_clip_start_tick())
        # Resolve conflict before changing the clip's range
        # to preserve the current order of clips.
        if (resolve_clip_conflict and self.track is not None):
            self.track._resolve_clip_conflict(
                self.get_id(),
                min(self.get_clip_start_tick(), to_left_tick),
                self.get_clip_end_tick(),
            )

        if self.get_type() == ClipType.MIDI_CLIP:
            self._time_stretch_midi_clip(stretch_factor=stretch_factor, reference_tick=self.get_clip_end_tick())
            self.move_clip_to(to_left_tick, move_associated_track_automation_points=False)
        elif (self.get_type() == ClipType.AUDIO_CLIP):
            self._time_stretch_audio_clip(to_left_tick, self.get_clip_end_tick(), self.get_clip_end_tick())
        # TODO: Scale the associated automation points accordingly.

    def time_stretch_from_clip_right(self, to_right_tick: int, resolve_clip_conflict=True):
        '''
        Time-stretch the clip by adjusting the end tick of the clip.

        NOTE: This could delete the clip if the range becomes empty after
        this call.
        @param to_right_tick The new end tick to stretch the clip to.
        '''
        if (to_right_tick <= self.get_clip_start_tick()):
            self.delete_from_parent(delete_associated_track_automation=True)
            return

        # Resolve conflict before changing the clip's range
        # to preserve the current order of clips.
        if resolve_clip_conflict and self.track:
            self.track._resolve_clip_conflict(
                self.get_id(),
                self.get_clip_start_tick(),
                max(self.get_clip_end_tick(), to_right_tick),
            )

        if (self.get_type() == ClipType.MIDI_CLIP):
            stretch_factor = (to_right_tick - self.get_clip_start_tick()
                              ) / (self.get_clip_end_tick() - self.get_clip_start_tick())
            self._time_stretch_midi_clip(stretch_factor=stretch_factor, reference_tick=self.get_clip_start_tick())
        elif (self.get_type() == ClipType.AUDIO_CLIP):
            self._time_stretch_audio_clip(self.get_clip_start_tick(), to_right_tick, self.get_clip_start_tick())

        # TODO: Scale the associated automation points accordingly.

    def _time_stretch_midi_clip(self, stretch_factor: float, reference_tick: int):
        for note in self.get_raw_notes():
            note.set_start_tick(
                Clip._calculate_scaled_new_tick(
                    note.get_start_tick(),
                    reference_tick, stretch_factor))
            note.set_end_tick(
                Clip._calculate_scaled_new_tick(
                    note.get_end_tick(),
                    reference_tick, stretch_factor))

        self._proto.clip_start_tick = Clip._calculate_scaled_new_tick(
            self.get_clip_start_tick(),
            reference_tick,
            stretch_factor,
        )
        self._proto.clip_end_tick = Clip._calculate_scaled_new_tick(
            self.get_clip_end_tick(), reference_tick, stretch_factor)

    def _time_stretch_audio_clip(
            self,
        new_left_tick: int,
        new_right_tick: int,
        reference_tick: int,
    ):
        if (self.get_type() != ClipType.AUDIO_CLIP):
            return

        audio_clip_data = self.get_audio_clip_data()
        if (audio_clip_data is None):
            raise Exception(f"Audio clip data is missing for audio clip {self.get_id()}")
        old_speed_ratio = audio_clip_data.speed_ratio if audio_clip_data.speed_ratio is not None and audio_clip_data.speed_ratio > 0 else 1
        old_duratoin = self.song.tick_to_seconds(
            self.get_clip_end_tick()) - self.song.tick_to_seconds(self.get_clip_start_tick())
        new_duration = self.song.tick_to_seconds(new_right_tick) - self.song.tick_to_seconds(new_left_tick)
        time_stretch_factor = new_duration / old_duratoin
        speed_ratio = old_speed_ratio / time_stretch_factor
        Clip.validate_audio_speed_ratio(speed_ratio)
        old_audio_start_time = self.song.tick_to_seconds(audio_clip_data.start_tick)
        reference_tick_time = self.song.tick_to_seconds(reference_tick)
        new_audio_start_to_reference_distance_in_time = (
            reference_tick_time - old_audio_start_time) * time_stretch_factor
        new_audio_start_time = reference_tick_time - new_audio_start_to_reference_distance_in_time
        new_audio_start_tick = self.song.seconds_to_tick(new_audio_start_time)
        audio_clip_data.speed_ratio = speed_ratio
        audio_clip_data.start_tick = new_audio_start_tick
        self._proto.clip_start_tick = new_left_tick
        self._proto.clip_end_tick = new_right_tick

    @staticmethod
    def validate_audio_speed_ratio(speed_ratio: float):
        if (
            speed_ratio is None or
            speed_ratio < Clip.MIN_AUDIO_SPEED_RATIO or
            speed_ratio > Clip.MAX_AUDIO_SPEED_RATIO
        ):
            raise Exception(
                f'Speed ratio must be >= {Clip.MIN_AUDIO_SPEED_RATIO} and <= {Clip.MAX_AUDIO_SPEED_RATIO}, you are changing to {speed_ratio}',
            )

    @staticmethod
    def _calculate_scaled_new_tick(
        old_tick: int,
        reference_tick: int,
        scale_factor: float,
    ):
        distance = (reference_tick - old_tick) * scale_factor
        return round(reference_tick - distance)

    def get_audio_pitch_offset(self):
        '''
        @returns The pitch offset of this audio in semitones, comparing to the raw audio.
        '''
        if (
            self.get_type() != ClipType.AUDIO_CLIP or
            not self.has_audio_clip_data() or
            self.get_audio_clip_data().pitch_offset is None  # type: ignore
        ):
            return 0
        return self.get_audio_clip_data().pitch_offset  # type: ignore

    def set_audio_pitch_offset(self, offset_in_semitones: float):
        '''
        Sets the pitch offset of this audio in semitones, the offset is compared to the raw audio.
        * @param offset_in_semitones Ranging from `Clip.MIN_AUDIO_PITCH_OFFSET` to `Clip.MAX_AUDIO_PITCH_OFFSET`, step 1, inclusive.
        * @returns
        '''
        if (self.get_type() != ClipType.AUDIO_CLIP):
            return

        Clip.validate_audio_pitch_offset(offset_in_semitones)
        self.get_audio_clip_data().pitch_offset = offset_in_semitones  # type: ignore

    @staticmethod
    def validate_audio_pitch_offset(offset_in_semitones: float):
        if (
            offset_in_semitones is None or
            offset_in_semitones < Clip.MIN_AUDIO_PITCH_OFFSET or
            offset_in_semitones > Clip.MAX_AUDIO_PITCH_OFFSET
        ):
            raise Exception(
                f'Pitch offset must be >= {Clip.MIN_AUDIO_PITCH_OFFSET} and <= {Clip.MAX_AUDIO_PITCH_OFFSET}, you are setting to {offset_in_semitones}',
            )

    def get_audio_start_tick(self):
        '''
        Gets the current clip audio's start tick.

        Note that this differs from the clip's start tick in that the user can trim
        the clip to only play part of the audio.

        Returns None if the clip is not audio clip or audio clip data is missing.
        '''
        if (self.get_type() != ClipType.AUDIO_CLIP or not self.has_audio_clip_data()):
            return None

        return self.get_audio_clip_data().start_tick  # type: ignore

    def get_raw_note_count(self):
        return len(self._proto.notes)

    def get_raw_notes(self):
        '''
        @returns All notes contained by the clip, including those that
        are not within the clip's range.
        '''
        for i in range(len(self._proto.notes)):
            yield self.get_raw_note_at(i)

    def get_raw_note_at(self, index: int):
        return Note(proto=self._proto.notes[index], clip=self)

    def get_notes(self):
        '''
        @returns Notes within the clip's range.
        '''

        note_protos = Clip._get_notes_in_range(
            raw_notes=self._proto.notes, start_tick=self.get_clip_start_tick(),
            end_tick=self.get_clip_end_tick())
        for note_proto in note_protos:
            yield Note(proto=note_proto, clip=self)

    def create_note(
        self,
        pitch: int,
        velocity: int,
        start_tick: int,
        end_tick: int,
        update_clip_range: bool = True,
        resolve_clip_conflict: bool = True
    ):
        '''
        Adds a note to the clip and returns it.

        @param pitch An integer value between 0 - 127
        @param velocity An integer value between 0 - 127
        @param start_tick An integer value indicating the start tick.
        @param end_tick An integer value indicating the end tick.
        @param update_clip_range Whether to update the clip's range if the note stretches outside the clip.
        @param resolve_clip_conflict Whether to resolve clip conflict if the clip range is updated.
        '''
        if self.get_type() != ClipType.MIDI_CLIP:
            # Only MIDI clips can create notes.
            return None
        if (
            not Note.is_valid_pitch(pitch) or
            not Note.is_note_range_valid(start_tick, end_tick) or
            not Note.is_note_velocity_valid(velocity)
        ):
            return None

        note = Note(
            pitch=pitch,
            velocity=velocity,
            start_tick=start_tick,
            end_tick=end_tick,
            id=self._get_next_note_id(),
        )
        if (start_tick < self.get_clip_start_tick() and update_clip_range):
            self.adjust_clip_left(start_tick, resolve_clip_conflict)

        if (end_tick > self.get_clip_end_tick() and update_clip_range):
            self.adjust_clip_right(end_tick, resolve_clip_conflict)

        self._ordered_insert_note(note)
        return note

    def get_type(self) -> int:
        return self._proto.type

    def delete_note(self, note: Note):
        note_index = self._get_note_index(note)
        if (note_index >= 0):
            self.delete_note_at(note_index)
            note.clip = None

    def delete_note_at(self, index: int):
        if (index >= 0 and index < len(self._proto.notes)):
            self._proto.notes.pop(index)

    def get_clip_start_tick(self) -> int:
        return self._proto.clip_start_tick

    def get_clip_end_tick(self) -> int:
        return self._proto.clip_end_tick

    def has_audio_clip_data(self) -> bool:
        return self._proto.HasField("audio_clip_data")

    def get_audio_clip_data(self) -> AudioClipData | None:
        if not self.has_audio_clip_data():
            return None
        return self._proto.audio_clip_data

    def set_audio_file(self, file_path: str, start_tick: int, duration: float):
        '''
        Sets a new audio file.
        '''
        self._proto.audio_clip_data.audio_file_path = file_path
        self._proto.audio_clip_data.start_tick = start_tick
        self._proto.audio_clip_data.duration = duration
        self._proto.audio_clip_data.speed_ratio = 1
        self._proto.audio_clip_data.pitch_offset = 0

    def clear_notes(self):
        del self._proto.notes[:]

    def delete_from_parent(self, delete_associated_track_automation: bool):
        if self.track is not None:
            self.track.delete_clip(self, delete_associated_track_automation)
            self.track = None

    def adjust_clip_left(self, clip_start_tick: int, resolve_conflict=True):
        '''
        Adjust the left boundary of the clip.

        NOTE: This could delete the clip if the range becomes empty after
        this call.

        @param clip_start_tick The new start tick (inclusive) of the clip.
        '''
        clip_start_tick = max(0, clip_start_tick)
        if self.get_type() == ClipType.AUDIO_CLIP and self.has_audio_clip_data():
            # Clip boundary cannot exceed the audio's boundary.
            clip_start_tick = max(
                clip_start_tick, self._proto.audio_clip_data.start_tick)

        if clip_start_tick > self.get_clip_end_tick():
            self.delete_from_parent(delete_associated_track_automation=True)
        else:
            # Resolve conflict before changing the clip's range
            # to preserve the current order of clips.
            if (resolve_conflict and self.track is not None):
                self.track._resolve_clip_conflict(
                    self.get_id(),
                    min(self.get_clip_start_tick(), clip_start_tick),
                    self.get_clip_end_tick(),
                )
            self._proto.clip_start_tick = clip_start_tick

    def adjust_clip_right(self, clip_end_tick: int, resolve_conflict=True):
        '''
        Adjust the right boundary of the clip.

        NOTE: This could delete the clip if the range becomes empty after
        this call.

        @param clipEndTick  The new end tick (inclusive) of the clip.
        '''
        if self.get_type() == ClipType.AUDIO_CLIP:
            # Clip right boundary cannot exceed the audio's right boundary.
            audio_end_tick = self.get_audio_end_tick()
            if audio_end_tick is not None:
                clip_end_tick = min(clip_end_tick, audio_end_tick)
        if clip_end_tick < self.get_clip_start_tick() or clip_end_tick < 0:
            self.delete_from_parent(delete_associated_track_automation=True)
        else:
            # Resolve conflict before changing the clip's range
            # to preserve the current order of clips.
            if (resolve_conflict and self.track is not None):
                self.track._resolve_clip_conflict(
                    self.get_id(),
                    self.get_clip_start_tick(),
                    max(self.get_clip_end_tick(), clip_end_tick),
                )

            self._proto.clip_end_tick = clip_end_tick

    def move_clip(self, offset_tick: int, move_associated_track_automation_points: bool):
        '''
        Move the clip by the given offset ticks.

        NOTE: Moving a clip can break the order of clips,
        so the clip must be re-positioned to the correct index.
        '''
        new_clip_start_tick = max(0, self.get_clip_start_tick() + offset_tick)
        new_clip_end_tick = self.get_clip_end_tick() + offset_tick
        if (new_clip_end_tick < 0):
            self.delete_from_parent(delete_associated_track_automation=True)
            return
        if self.track is not None:
            # Resolve conflict before changing the clip's range
            # to preserve the current order of clips.
            self.track._resolve_clip_conflict(self.get_id(), new_clip_start_tick, new_clip_end_tick)

        # The track's clip order will be invalidated after the move, and deleting the clip
        # requires the clips to be sorted, so delete the clip before the move happens.
        if self.track is not None:
            clip_index = self.track.get_clip_index(self)
            self.track.delete_clip_at(clip_index, delete_associated_track_automation=False)

        # Move the clip.
        original_start_tick = self.get_clip_start_tick()
        original_end_tick = self.get_clip_end_tick()

        if self.get_type() == ClipType.MIDI_CLIP:
            self._proto.clip_start_tick = new_clip_start_tick
            self._proto.clip_end_tick = new_clip_end_tick
            for note in self.get_raw_notes():
                note.set_start_tick(note.get_start_tick() + offset_tick)
                note.set_end_tick(note.get_end_tick() + offset_tick)

        elif (self.get_type() == ClipType.AUDIO_CLIP):
            if (not self.has_audio_clip_data()):
                raise Exception('Cannot move audio clip without audio data')

            # Let the content of the audio at the original clip start be S
            # Let the clip start tick before move be T1, after move be T2.
            # Moving an audio clip means:
            # 1. S must be at T2 after move
            # 2. Duration of the playable audio must remain unchanged.
            song = self.song
            # The clip's end position's time relative to the audio's start time should remain
            # unchanged.
            original_audio_start_time = song.tick_to_seconds(self.get_audio_clip_data().start_tick)  # type:ignore
            original_start_time = song.tick_to_seconds(original_start_tick)
            original_end_time = song.tick_to_seconds(original_end_tick)
            playable_audio_duration = original_end_time - original_start_time
            clip_start_relative_to_audio_start = original_start_time - original_audio_start_time
            # Use the raw updated clip tick here.
            new_clip_start_time = song.tick_to_seconds(self.get_clip_start_tick() + offset_tick)
            new_audio_start_time = new_clip_start_time - clip_start_relative_to_audio_start
            new_clip_end_time = new_clip_start_time + playable_audio_duration
            self._proto.clip_start_tick = new_clip_start_tick
            self._proto.clip_end_tick = song.seconds_to_tick(new_clip_end_time)
            self._proto.audio_clip_data.start_tick = song.seconds_to_tick(new_audio_start_time)
            if (self.get_clip_end_tick() < 0):
                self.delete_from_parent(delete_associated_track_automation=True)
                return

        if (self.track is not None):
            # Ordered insert back the clip.
            self.track._ordered_insert_clip(self)

            # Move track automation points if required.
            if (move_associated_track_automation_points):
                self.track.get_automation().move_all_points_within_range(
                    original_start_tick,
                    original_end_tick,
                    offset_tick,
                    offset_value=0,
                )

    def move_clip_to(self, tick: int, move_associated_track_automation_points: bool):
        '''
        Move the clip to a given tick.

        @param tick The tick that this clip will start at.
        '''
        offsetTick = tick - self.get_clip_start_tick()
        self.move_clip(offsetTick, move_associated_track_automation_points)

    @staticmethod
    def _get_notes_in_range(raw_notes: List[song_pb2.Note], start_tick: int, end_tick: int):
        '''
        Gets notes that are playable in a range.

        Performs two O(logn) searches and some extra while loops to narrow down range.
        '''
        # Find the first note that is within the clip.
        # IMPORTANT: Assuming that a note cannot be within the Clip if it starts before the clip.
        target_start_note = SimpleNamespace()
        target_start_note.start_tick = start_tick
        start_index = max(
            0,
            lower_than(
                raw_notes,
                target_start_note,
                key=lambda x: x.start_tick,
            ),
        )
        while (
            start_index >= 0 and start_index < len(raw_notes) and
            not Clip.is_note_in_clip(
                raw_notes[start_index].start_tick,
                raw_notes[start_index].end_tick,
                start_tick,
                end_tick,
            )
        ):
            start_index += 1

        if (start_index >= len(raw_notes)):
            return []

        # Find the last note that is within the clip.
        target_end_note = SimpleNamespace()
        target_end_note.start_tick = end_tick
        end_index = min(
            len(raw_notes) - 1,
            greater_than(
                raw_notes,
                target_end_note,
                lambda x: x.start_tick
            ),
        )
        while (
            end_index >= 0 and end_index < len(raw_notes) and
            not Clip.is_note_in_clip(
                raw_notes[end_index].start_tick,
                raw_notes[end_index].end_tick,
                start_tick,
                end_tick,
            )
        ):
            end_index -= 1

        if (end_index < 0):
            return []

        if (end_index < start_index):
            return []

        return raw_notes[start_index:(end_index + 1)]

    def _trim_conflict_part(self, start_tick: int, end_tick: int):
        '''
        Trim the conflict part from the clip.

        Anything within the given range (inclusive), will be removed from the current clip.
        '''
        overlapping_start_tick = max(start_tick, self.get_clip_start_tick())
        overlapping_end_tick = min(end_tick, self.get_clip_end_tick())
        if (overlapping_start_tick > overlapping_end_tick):
            # Overlapping range is empty.
            return
        if (
            overlapping_start_tick > self.get_clip_end_tick() or
            overlapping_end_tick < self.get_clip_start_tick()
        ):
            # No overlapping.
            return

        if (
            overlapping_end_tick >= self.get_clip_end_tick() and
            overlapping_start_tick <= self.get_clip_start_tick()
        ):
            # The whole clip overlaps with the given range.
            # Delete the clip.
            self.delete_from_parent(delete_associated_track_automation=True)
            return

        if (
            overlapping_end_tick < self.get_clip_end_tick() and
            overlapping_start_tick > self.get_clip_start_tick()
        ):
            # Overlapping part is in the middle of the clip.
            # Trim the clip into the left part and create a new clip for the right part.
            right_clip_start_tick = overlapping_end_tick + 1
            right_clip_end_tick = self.get_clip_end_tick()

            self.adjust_clip_right(
                overlapping_start_tick - 1, resolve_conflict=False)

            if self.track is not None:
                if self.get_type() == ClipType.MIDI_CLIP:
                    right_clip = self.track.create_midi_clip(
                        clip_start_tick=right_clip_start_tick,
                        clip_end_tick=right_clip_end_tick,
                    )

                    right_note_protos = Clip._get_notes_in_range(
                        raw_notes=self._proto.notes, start_tick=right_clip_start_tick, end_tick=right_clip_end_tick)
                    for right_note_proto in right_note_protos:
                        right_clip.create_note(
                            pitch=right_note_proto.pitch,
                            velocity=right_note_proto.velocity,
                            start_tick=right_note_proto.start_tick,
                            end_tick=right_note_proto.end_tick,
                            update_clip_range=False,
                            resolve_clip_conflict=False,
                        )

                elif (self.get_type() == ClipType.AUDIO_CLIP):
                    audio_clip_data = self._proto.audio_clip_data
                    self.track.create_audio_clip(
                        clip_start_tick=right_clip_start_tick,
                        clip_end_tick=right_clip_end_tick,
                        audio_clip_data={
                            "audio_file_path": audio_clip_data.audio_file_path if audio_clip_data.HasField("audio_file_path") else None,
                            "start_tick": audio_clip_data.start_tick,
                            "duration": audio_clip_data.duration,
                            "audio_data": {
                                "format": audio_clip_data.audio_data.format,
                                "data": audio_clip_data.audio_data.data
                            } if audio_clip_data.HasField("audio_data") else None
                        },
                    )
            return

        # Overlapping part is on the side.
        if (
            overlapping_start_tick > self.get_clip_start_tick() and
            overlapping_start_tick <= self.get_clip_end_tick()
        ):
            # Do not resolve conflict here since it will
            # cause a bad loop.
            self.adjust_clip_right(
                overlapping_start_tick - 1, resolve_conflict=False)
        elif (
            overlapping_end_tick < self.get_clip_end_tick() and
            overlapping_end_tick >= self.get_clip_start_tick()
        ):
            # Do not resolve conflict here since it will
            # cause a bad loop.
            self.adjust_clip_left(overlapping_end_tick +
                                  1, resolve_conflict=False)

    def _get_next_note_id(self):
        if self._next_note_id is None:
            if len(self._proto.notes) == 0:
                self._next_note_id = 1
            else:
                self._next_note_id = max([note_proto.id for note_proto in self._proto.notes]) + 1

        note_id = self._next_note_id
        if (self._next_note_id >= 2147483647):
            self._next_note_id = 1
        else:
            self._next_note_id += 1

        return note_id

    def _ordered_insert_note(self, new_note: Note):
        if (self.get_type() != ClipType.MIDI_CLIP):
            # Only MIDI clips can insert notes.
            return
        if (new_note.get_clip() == self):
            # Do not insert if the note is already in the list.
            return
        insert_index = greater_equal(
            self._proto.notes,
            new_note._proto,
            key=lambda x: x.start_tick,
        )
        if (insert_index < 0):
            self._proto.notes.append(new_note._proto)
            # Reassign proto since protobuf created a new copy
            new_note._proto = self._proto.notes[-1]
        else:
            self._proto.notes.insert(insert_index, new_note._proto)
            # Reassign proto since protobuf created a new copy
            new_note._proto = self._proto.notes[insert_index]
        new_note.clip = self

    def _get_note_index(self, note: Note):
        start_index = lower_than(
            self._proto.notes,
            note._proto,
            lambda x: x.start_tick,
        )

        for index in range(max(0, start_index), len(self._proto.notes)):
            current_note_proto = self._proto.notes[index]
            if current_note_proto.id == note.get_id():
                return index
            if (current_note_proto.start_tick > note.get_start_tick()):
                # We have searched past all possible notes.
                break
        return -1

    def __repr__(self) -> str:
        return str(self._proto)

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

    MIN_AUDIO_SPEED_RATIO = 0.05
    MAX_AUDIO_SPEED_RATIO = 20
    MIN_AUDIO_PITCH_OFFSET = -24
    MAX_AUDIO_PITCH_OFFSET = 24
