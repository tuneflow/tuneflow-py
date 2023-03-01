from __future__ import annotations
from tuneflow_py.descriptors.clip_descriptor import AudioClipData
from tuneflow_py.models.protos import song_pb2
from tuneflow_py.models.clip import Clip, ClipType
from tuneflow_py.models.audio_plugin import AudioPlugin
from tuneflow_py.utils import db_to_volume_value, volume_value_to_db, lower_equal, greater_equal, lower_than, decode_audio_plugin_tuneflow_id
import nanoid
from typing import List
from types import SimpleNamespace

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
        '''
        A track in the song that maps to an instrument.

        It contains clips, instrument information, play status(volume, muted, etc.), and more.

        IMPORTANT: Do not use the constructor directly, call create_track from a song instead.

        @param uuid The universal-unique identifier of the track. In most cases, leave it blank and it will be automatically assigned.
        @param instrument Information about the instrument to play this track.
        @param volume A float value indicating the track-level volume, ranging from 0 to 1.
        @param pan An integer value from -64 to 63, corresponding to the midi pan CC 0 - 127.
        @param solo Whether this track is in solo mode.
        @param muted Whether this track is muted.
        @param rank The rank of this track within the song.
        '''
        if song is None:
            raise Exception('song must be provided when creating a track')
        self.song = song
        if proto is not None:
            self._proto = proto
            return
        self._proto = song_pb2.Track()
        self._proto.type = type
        if instrument is not None:
            self._proto.instrument.program = instrument["program"]
            self._proto.instrument.is_drum = instrument["is_drum"]
        elif type == TrackType.MIDI_TRACK:
            self._proto.instrument.program = 0
            self._proto.instrument.is_drum = False
        if type == TrackType.AUX_TRACK:
            # TODO: Initialize aux track data.
            pass
        self._proto.uuid = uuid if uuid is not None else Track._generate_track_id()
        self._proto.volume = volume
        self._proto.solo = solo
        self._proto.muted = muted
        self._proto.rank = rank
        self._proto.pan = pan
        # TODO: Initialize automation data.

    def get_clip_count(self):
        return len(self._proto.clips)

    def get_clips(self):
        for i in range(len(self._proto.clips)):
            yield self.get_clip_at(i)

    def get_clip_at(self, clip_index: int):
        return self._create_clip_from_proto(proto=self._proto.clips[clip_index])

    def get_type(self) -> int:
        return self._proto.type

    def get_volume(self):
        '''
        Returns the fader position, ranging from 0 to 1.
        '''
        return self._proto.volume

    def get_volume_in_db(self):
        return volume_value_to_db(self.get_volume())

    def set_volume(self, volume: float):
        '''
        Sets the volume fader position.

        @param volume The track volume fader position, ranging from 0 to 1.
        '''
        self._proto.volume = volume

    def get_pan(self) -> int:
        '''
        A pan value from -64 to 63
        '''
        return self._proto.pan

    def set_pan(self, pan: int):
        '''
        Sets the track pan knob position.

        @param pan An integer value between -64 and 63. Setting to 0 means balanced.
        '''
        self._proto.pan = pan

    def get_solo(self) -> bool:
        '''
        Returns whether the track is being solo'ed.
        '''
        return self._proto.solo

    def set_solo(self, solo: bool):
        '''
        @param solo If set to true, track will be solo'ed and unmuted.
        '''
        self._proto.solo = solo

    def get_muted(self) -> bool:
        return self._proto.muted

    def set_muted(self, muted: bool):
        self._proto.muted = muted

    def get_rank(self):
        return self._proto.rank

    def has_instrument(self):
        return self._proto.HasField('instrument')

    def get_instrument(self):
        if not self.has_instrument():
            return None
        return self._proto.instrument

    def set_instrument(self, program: int, is_drum: bool):
        '''
        Set the midi instrument that this track corresponds to. This will also
        be the instrument to be used by the Minimal playback engine.

        @param program General MIDI program number(counting from 0, i.e. "Acoustic Grand Piano" === 0). 
            https://www.midi.org/specifications-old/item/gm-level-1-sound-set

        @param is_drum Whether this instrument is a drumset.
            '''
        if self.get_type() != TrackType.MIDI_TRACK:
            return
        self._proto.instrument.program = program
        self._proto.instrument.is_drum = is_drum

    def has_sampler_plugin(self):
        return self._proto.HasField('sampler_plugin')

    def get_sampler_plugin(self):
        '''
        Gets the synth/sampler plugin of this track.

        The sampler plugin generates sound from MIDI notes and will only work for MIDI tracks.
        '''
        if not self.has_sampler_plugin():
            return None
        return AudioPlugin(proto=self._proto.sampler_plugin)

    def set_sampler_plugin(self, plugin: AudioPlugin | None, clear_automation=True):
        '''
        Sets the synth/sampler plugin of this track.

        @param clear_automation Whether to remove existing track automation associated with the old plugin.
        '''
        if (self.get_type() != TrackType.MIDI_TRACK):
            return
        plugin_type_changed = (
            self.has_sampler_plugin() == False and plugin is not None) or (
            plugin is None and self.has_sampler_plugin()) or (
            plugin is not None and self.has_sampler_plugin() and not plugin.matches_tf_id(
                self.get_sampler_plugin().get_tuneflow_id()))  # type:ignore
        old_plugin = self.get_sampler_plugin()
        if plugin is not None:
            self._proto.sampler_plugin.MergeFrom(plugin._proto)
        else:
            self._proto.ClearField("sampler_plugin")
        if (plugin_type_changed and old_plugin is not None and clear_automation):
            # TODO: Remove automation of plugin
            pass
            # self.automation.remove_automation_of_plugin(old_plugin.get_instance_id())

    def get_audio_plugin_count(self):
        return len(self._proto.audio_plugin)

    def get_audio_plugin_at(self, index):
        return AudioPlugin(proto=self._proto.audio_plugin[index])

    def get_suggested_instruments_count(self):
        return len(self._proto.suggested_instruments)

    def get_suggested_instrument_at(self, index: int):
        self._proto.suggested_instruments[index]

    def create_suggested_instrument(self, program: int, is_drum: bool):
        '''
        Adds a suggested instrument and returns it.

        @param program General MIDI program number(counting from 0, i.e. "Acoustic Grand Piano" === 0). 
            https://www.midi.org/specifications-old/item/gm-level-1-sound-set

        @param is_drum Whether this instrument is a percussion instrument
            (or using channel 9(counting from 0) if you know what it means).
        '''
        if (self.get_type() != TrackType.MIDI_TRACK):
            return
        instrument_info = self._proto.suggested_instruments.add(
            program=program, is_drum=is_drum)
        return instrument_info

    def clear_suggested_instruments(self):
        del self._proto.suggested_instruments[:]

    def get_track_start_tick(self):
        if self.get_clip_count() == 0:
            return 0
        return self.get_clip_at(0).get_clip_start_tick()

    def get_track_end_tick(self):
        if self.get_clip_count() == 0:
            return 0
        return self.get_clip_at(self.get_clip_count() - 1).get_clip_end_tick()

    def get_clip_by_id(self, clip_id: str):
        for clip_proto in self._proto.clips:
            if clip_proto.id == clip_id:
                return self._create_clip_from_proto(proto=clip_proto)
        return None

    def create_midi_clip(self, clip_start_tick: int, clip_end_tick: int | None = None, insert_clip=True):
        '''
        Creates a MIDI clip and optionally inserts it into the track.

        @param clip_start_tick The start of the clip, must be specified.
        @param insert_clip Whether to insert the created clip into the track.
        '''
        if clip_start_tick is None:
            raise Exception(
                'clip_start_tick must be specified when creating a clip.')

        new_clip_end_tick = clip_start_tick + \
            1 if clip_end_tick is None else clip_end_tick
        if new_clip_end_tick < clip_start_tick:
            raise Exception(
                f'clip_end_tick must be greater or equal to clip_start_tick, got clip_start_tick: {clip_start_tick}, clip_end_tick: {clip_end_tick}'
            )

        clip = Clip(
            id=Clip._generate_clip_id(),
            type=ClipType.MIDI_CLIP,
            song=self.song,
            track=None,
            clip_start_tick=clip_start_tick,
            clip_end_tick=new_clip_end_tick,
        )
        if insert_clip:
            self.insert_clip(clip)

        return clip

    def create_audio_clip(
            self, clip_start_tick: int, audio_clip_data: AudioClipData, clip_end_tick: int | None = None, insert_clip=True):
        '''
        Creates an audio clip and optionally inserts it into the track.

        @param clip_start_tick The start of the clip, must be specified.
        @param audio_clip_data A dict of audio-related data.
        @param insert_clip Whether to insert the created clip into the track.
        '''
        if clip_start_tick is None:
            raise Exception(
                'clip_start_tick must be specified when creating a clip.')

        clip = Clip(
            id=Clip._generate_clip_id(),
            type=ClipType.AUDIO_CLIP,
            song=self.song,
            track=None,
            clip_start_tick=clip_start_tick,
            clip_end_tick=clip_end_tick,
            audio_clip_data=audio_clip_data,
        )
        if (insert_clip):
            self.insert_clip(clip)

        return clip

    def insert_clip(self, clip: Clip):
        if clip.get_track() != self:
            if clip.get_track() is not None:
                # Clip belongs to another track.
                clip.delete_from_parent(
                    delete_associated_track_automation=False)
            clip.track = self
        else:
            # Clip already belongs to the track.
            return

        # Resolve conflict before inserting a new clip
        # to preserve the current order of clips.
        self._resolve_clip_conflict(
            clip.get_id(), clip.get_clip_start_tick(), clip.get_clip_end_tick())
        self._ordered_insert_clip(clip)

    def get_clip_index(self, clip: Clip):
        '''
        Get the index of the clip within the clip list.

        NOTE: This assumes the clip list is sorted.
        '''
        start_index = lower_equal(
            self._proto.clips,
            clip._proto,
            key=lambda x: x.clip_start_tick,
        )

        for i in range(max(0, start_index), len(self._proto.clips)):
            if self._proto.clips[i].id == clip.get_id():
                return i
        return -1

    def delete_clip(self, clip: Clip, delete_associated_track_automation: bool):
        index = self.get_clip_index(clip)
        if index >= 0 and index < self.get_clip_count():
            self.delete_clip_at(index, delete_associated_track_automation)
            clip.track = None

    def delete_clip_at(self, index: int, delete_associated_track_automation: bool):
        if (index < 0):
            return

        if delete_associated_track_automation:
            if index < 0 or index >= len(self._proto.clips):
                return

            # TODO: Remove automation points within range
            # self.get_automation().remove_all_points_within_range(clip.get_clip_start_tick(), clip.get_clip_end_tick())

        self._proto.clips.pop(index)

    def get_clips_overlapping_with(self, start_tick: int, end_tick: int):
        '''
        Gets the clips whose range overlaps with the given range.
        '''
        overlapping_clips: List[Clip] = []
        target_clip = SimpleNamespace()
        target_clip.clip_start_tick = start_tick
        start_index = lower_than(
            self._proto.clips,
            target_clip,
            key=lambda x: x.clip_start_tick,
        )
        for i in range(max(start_index, 0), len(self._proto.clips)):
            current_clip_proto = self._proto.clips[i]
            if (current_clip_proto.clip_end_tick < start_tick):
                continue

            if current_clip_proto.clip_start_tick > end_tick:
                break

            overlapping_clips.append(self._create_clip_from_proto(proto=current_clip_proto))

        return overlapping_clips

    def create_audio_plugin(self, tf_id: str):
        plugin_info = decode_audio_plugin_tuneflow_id(tf_id)
        plugin = AudioPlugin(
            name=plugin_info["name"],
            manufacturer_name=plugin_info["manufacturer_name"],
            plugin_format_name=plugin_info["plugin_format_name"],
            plugin_version=plugin_info["plugin_version"],
        )
        return plugin

    def _resolve_clip_conflict(self, clip_id: str, start_tick: int, end_tick: int):
        overlapping_clips = self.get_clips_overlapping_with(
            start_tick, end_tick)
        for clip in overlapping_clips:
            if clip.get_id() == clip_id:
                continue
            clip._trim_conflict_part(start_tick, end_tick)

    def _ordered_insert_clip(self, new_clip: Clip):
        insert_index = greater_equal(
            self._proto.clips,
            new_clip._proto,
            key=lambda x: x.clip_start_tick,
        )

        self._proto.clips.insert(insert_index, new_clip._proto)
        # Re-assign proto since protobuf created a new copy for the inserted proto
        new_clip._proto = self._proto.clips[insert_index]

    def _create_clip_from_proto(self, proto: song_pb2.Clip):
        return Clip(song=self.song, track=self, proto=proto)

    def __repr__(self) -> str:
        return str(self._proto)

    @staticmethod
    def _generate_track_id():
        return nanoid.generate()
