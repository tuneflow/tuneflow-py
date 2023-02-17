from __future__ import annotations
from base64 import b64encode, b64decode
from tuneflow_py.models.protos import song_pb2
from tuneflow_py.models.track import Track, TrackType
from tuneflow_py.models.clip import Clip, ClipType
from tuneflow_py.models.tempo import TempoEvent
from tuneflow_py.models.time_signature import TimeSignatureEvent
from tuneflow_py.models.automation import AutomationTarget, AutomationTargetType
from tuneflow_py.utils import db_to_volume_value, greater_equal, lower_than
from miditoolkit.midi import MidiFile, TempoChange as ToolkitTempoChange, TimeSignature as ToolkitTimeSignature, Instrument, Note as ToolkitNote
from types import SimpleNamespace
from typing import List


class Song:
    def __init__(self, proto: song_pb2.Song | None = None) -> None:
        if proto is not None:
            self._proto = proto
        else:
            self._proto = song_pb2.Song()
            self._proto.PPQ = Song.get_default_resolution()
            self._proto.tempos.append(
                song_pb2.TempoEvent(ticks=0, time=0, bpm=120))
            self._proto.time_signatures.append(
                song_pb2.TimeSignatureEvent(ticks=0, numerator=4, denominator=4))
            self._proto.last_tick = 0
            self._proto.duration = 0
            self._proto.master_track.uuid = Track._generate_track_id()
            self._proto.master_track.type = TrackType.MASTER_TRACK
            self._proto.master_track.volume = db_to_volume_value(0.0)

    def get_last_tick(self):
        '''
        @returns End tick of the last note.
        '''
        if self.get_track_count() == 0:
            return 0
        return max([track.get_track_end_tick() for track in self.get_tracks()])

    def get_duration(self):
        return self.tick_to_seconds(self.get_last_tick())

    def get_track_count(self):
        return len(self._proto.tracks)

    def get_tracks(self):
        for track_proto in self._proto.tracks:
            yield Track(song=self, proto=track_proto)

    def get_track_by_id(self, track_id: str) -> Track | None:
        for track_proto in self._proto.tracks:
            if track_proto.uuid == track_id:
                return Track(song=self, proto=track_proto)
        return None

    def get_track_at(self, index):
        return Track(song=self, proto=self._proto.tracks[index])

    def serialize(self):
        # type: ignore
        return b64encode(self._proto.SerializeToString()).decode('ascii')

    @staticmethod
    def deserialize(serialized_song_string: str):
        song_proto = song_pb2.Song()
        song_proto.ParseFromString(
            b64decode(serialized_song_string))  # type: ignore
        return Song(proto=song_proto)

    @staticmethod
    def from_midi(midi_obj: MidiFile):
        '''
        TODO: Replace proto operations with builtin methods.
        '''
        def scale_int_by(value, scale_factor):
            return round(value*scale_factor)
        song = Song()
        song_proto = song._proto
        ppq_scale_factor = float(song_proto.PPQ) / \
            float(midi_obj.ticks_per_beat)
        # Add tempos and time signatures
        song.overwrite_tempo_changes([TempoEvent(ticks=scale_int_by(
            tempo_change.time, ppq_scale_factor), bpm=tempo_change.tempo) for tempo_change in midi_obj.tempo_changes])
        song.overwrite_time_signature_changes([TimeSignatureEvent(ticks=scale_int_by(
            time_signature_change.time, ppq_scale_factor), numerator=time_signature_change.numerator, denominator=time_signature_change.denominator) for time_signature_change in midi_obj.time_signature_changes])

        # Add tracks and notes.
        song_last_tick = 0
        for index, instrument in enumerate(midi_obj.instruments):
            song_track_proto = song_proto.tracks.add(
                uuid=Track._generate_track_id(), rank=index, type=TrackType.MIDI_TRACK)
            song_track_proto.instrument.program = instrument.program
            song_track_proto.instrument.is_drum = instrument.is_drum
            track_clip_proto = song_track_proto.clips.add(
                id=Clip._generate_clip_id(), type=ClipType.MIDI_CLIP, clip_start_tick=0)
            # Add notes.
            for note in instrument.notes:
                start_tick = scale_int_by(
                    note.start, ppq_scale_factor)
                end_tick = scale_int_by(note.end, ppq_scale_factor)
                track_clip_proto.notes.add(pitch=note.pitch, velocity=note.velocity, start_tick=start_tick, start_time=song.tick_to_seconds(
                    start_tick), end_tick=end_tick, end_time=song.tick_to_seconds(end_tick))
            track_clip_proto.clip_start_tick = min(
                track_clip_proto.notes, key=lambda x: x.start_tick).start_tick
            track_clip_proto.clip_end_tick = max(
                track_clip_proto.notes, key=lambda x: x.end_tick).end_tick
            song_last_tick = max(
                song_last_tick, track_clip_proto.clip_end_tick)
            # Add automation.
            volume_ccs = []
            pan_ccs = []
            for control_change in instrument.control_changes:
                if control_change.number == 7:
                    # Volume CC
                    volume_ccs.append(control_change)
                elif control_change.number == 10:
                    # Pan CC
                    pan_ccs.append(control_change)
            if len(volume_ccs) == 1:
                song_track_proto.volume = volume_ccs[0].value/127.0
            elif len(volume_ccs) > 1:
                volume_target = AutomationTarget(AutomationTargetType.VOLUME)
                volume_target_id = volume_target.to_tf_automation_target_id()
                song_track_proto.automation.targets.append(
                    volume_target._proto)
                volume_target_value = song_pb2.AutomationValue()
                song_track_proto.automation.target_values[volume_target_id] = volume_target_value
                for index, cc in enumerate(sorted(volume_ccs, key=lambda x: x.time)):
                    volume_target_value.points.add(tick=scale_int_by(
                        cc.time, ppq_scale_factor), value=cc.value/127.0, id=index+1)
            else:
                # Volume data missing from midi, set it to default.
                song_track_proto.volume = db_to_volume_value(0.0)

            if len(pan_ccs) == 1:
                song_track_proto.pan = pan_ccs[0].value - 64
            elif len(pan_ccs) > 1:
                pan_target = AutomationTarget(AutomationTargetType.PAN)
                pan_target_id = pan_target.to_tf_automation_target_id()
                song_track_proto.automation.targets.append(pan_target._proto)
                pan_target_value = song_pb2.AutomationValue()
                song_track_proto.automation.target_values[pan_target_id] = pan_target_value
                for index, cc in enumerate(sorted(pan_ccs, key=lambda x: x.time)):
                    pan_target_value.points.add(tick=scale_int_by(
                        cc.time, ppq_scale_factor), value=cc.value/127.0, id=index+1)

        song.last_tick = song_last_tick
        song.duration = song.tick_to_seconds(song_last_tick)
        return song

    def to_midi(self):
        '''
        TODO: Replace proto operations with builtin methods.
        '''
        midi_obj = MidiFile()
        midi_obj.ticks_per_beat = self.get_resolution()
        for tempo_proto in self._proto.tempos:
            midi_obj.tempo_changes.append(ToolkitTempoChange(
                tempo=tempo_proto.bpm, time=tempo_proto.ticks))
        for time_signature_proto in self._proto.time_signatures:
            midi_obj.time_signature_changes.append(ToolkitTimeSignature(
                numerator=time_signature_proto.numerator, denominator=time_signature_proto.denominator, time=time_signature_proto.ticks))
        for track_proto in self._proto.tracks:
            if track_proto.type != TrackType.MIDI_TRACK or len(track_proto.clips) == 0:
                continue
            instrument = Instrument(program=track_proto.instrument.program,
                                    is_drum=track_proto.instrument.is_drum, name=f'Track {track_proto.rank}')
            midi_obj.instruments.append(instrument)
            # Export clips
            for clip_proto in track_proto.clips:
                if clip_proto.type != ClipType.MIDI_CLIP:
                    continue
                for note_proto in clip_proto.notes:
                    if not Clip.is_note_in_clip(note_start_tick=note_proto.start_tick, note_end_tick=note_proto.end_tick, clip_start_tick=clip_proto.clip_start_tick, clip_end_tick=clip_proto.clip_end_tick):
                        continue
                    instrument.notes.append(ToolkitNote(
                        pitch=note_proto.pitch, velocity=note_proto.velocity, start=note_proto.start_tick, end=note_proto.end_tick))
            # TODO: Export automation
        return midi_obj

    def get_resolution(self):
        return self._proto.PPQ

    def get_tempo_event_count(self):
        return len(self._proto.tempos)

    def create_tempo_change(self, ticks: int, bpm: float):
        '''
        Adds a tempo change event into the song and returns it.

        @param ticks The tick at which this event happens.
        @param bpm The new tempo in BPM(Beats-per-minute) format.
        '''
        if self.get_resolution() <= 0:
            raise Exception(
                'Song resolution must be provided before creating tempo changes.')

        if self.get_tempo_event_count() == 0 and ticks != 0:
            raise Exception('The first tempo event must be at tick 0')

        # Calculate time BEFORE the new tempo event is inserted.
        tempo_change = TempoEvent(
            ticks=ticks, bpm=bpm, time=self.tick_to_seconds(ticks))
        insert_index = greater_equal(
            self._proto.tempos,
            tempo_change._proto,
            lambda x: x.ticks
        )
        if insert_index < 0:
            self._proto.tempos.append(tempo_change._proto)
        else:
            self._proto.tempos.insert(insert_index, tempo_change._proto)

        self.retiming_tempo_events()
        return tempo_change

    def retiming_tempo_events(self):
        sorted_tempos = sorted(
            self._proto.tempos, key=lambda tempo: tempo.ticks)
        del self._proto.tempos[:]
        self._proto.tempos.extend(sorted_tempos)
        # Re-calculate all tempo event time.
        for tempo_event_proto in self._proto.tempos:
            tempo_event_proto.time = self.tick_to_seconds(
                tempo_event_proto.ticks)

    def tick_to_seconds(self, tick: int):
        if tick == 0:
            return 0

        target_tempo = SimpleNamespace()
        target_tempo.ticks = tick
        base_tempo_index = lower_than(
            self._proto.tempos,
            target_tempo,
            lambda x: x.ticks
        )
        if base_tempo_index == -1:
            # If no tempo is found before the tick, use the first tempo.
            base_tempo_index = 0

        base_tempo_change = self._proto.tempos[base_tempo_index]
        ticks_delta = tick - base_tempo_change.ticks
        ticks_per_second_since_last_tempo_change = Song._tempo_bpm_to_ticks_per_second(
            base_tempo_change.bpm,
            self.get_resolution(),
        )
        return base_tempo_change.time + ticks_delta / ticks_per_second_since_last_tempo_change

    def overwrite_tempo_changes(self, tempo_events: List[TempoEvent]):
        if len(tempo_events) == 0:
            raise Exception('Cannot clear all the tempo events.')
        sorted_tempo_events = sorted(
            tempo_events, key=lambda tempo_event: tempo_event.get_ticks())
        first_tempo_event = sorted_tempo_events[0]
        if first_tempo_event.get_ticks() > 0:
            raise Exception('The first tempo event needs to start from tick 0')
        del self._proto.tempos[:]
        self._proto.tempos.append(song_pb2.TempoEvent(
            ticks=0, time=0, bpm=first_tempo_event.get_bpm()))
        for i in range(1, len(sorted_tempo_events)):
            tempo_event = sorted_tempo_events[i]
            self.create_tempo_change(
                ticks=tempo_event.get_ticks(), bpm=tempo_event.get_bpm())
        self.retiming_tempo_events()

    def overwrite_time_signature_changes(self, time_signatures: List[TimeSignatureEvent]):
        if len(time_signatures) == 0:
            raise Exception('At least one time signature needs to be present.')
        del self._proto.time_signatures[:]
        for time_signature_change in time_signatures:
            self._proto.time_signatures.add(
                ticks=time_signature_change.get_ticks(), numerator=time_signature_change.get_numerator(), denominator=time_signature_change.get_denominator())

    def get_time_signature_event_count(self):
        return len(self._proto.time_signatures)

    def get_time_signature_event_at(self, index: int):
        return TimeSignatureEvent(proto=self._proto.time_signatures[index])

    def create_track(self, type: int,
                     index: int,
                     rank: int | None = None):
        new_track = Track(
            type=type, song=self, rank=rank if rank is not None else self.get_next_track_rank())
        self._proto.tracks.insert(index, new_track._proto)
        return new_track

    def get_next_track_rank(self):
        return 1 if len(self._proto.tracks) == 0 else max([track.rank for track in self._proto.tracks]) + 1

    @staticmethod
    def _tempo_bpm_to_ticks_per_second(tempo_bpm: float, PPQ: int):
        return (tempo_bpm * PPQ) / 60

    @staticmethod
    def get_default_resolution():
        '''
        Returns the default Pulse-per-Quater-Note used in TuneFlow.
        '''
        return 480
