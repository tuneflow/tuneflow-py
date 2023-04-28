from tuneflow_py.models.song import Song, TrackType
from tuneflow_py.models.note import Note
from tuneflow_py.models.clip import Clip
from tuneflow_py.models.audio_plugin import AudioPlugin
from tuneflow_py.utils import db_to_volume_value
from typing import List
import unittest


def create_song():
    song = Song()
    song.create_tempo_change(ticks=1440, bpm=60)
    return song


def assert_notes_are_equal(notes1: List[Note], notes2: List[Note]):
    if len(notes1) != len(notes2):
        raise Exception(
            f'Notes are not of equal length, {len(notes1)} vs {len(notes2)}')
    for i in range(0, len(notes1)):
        if not notes1[i].equals(notes2[i]) or notes1[i].get_id() != notes2[i].get_id():
            raise Exception(
                f'{i}th notes of the two lists are not equal, \n{str(notes1[i])}\n vs \n{str( notes2[i],)}',
            )


def create_test_notes(note_specs: List, clip: Clip):
    return [Note(**spec, clip=clip) for spec in note_specs]


class TestCreateTracks(unittest.TestCase):
    def test_create_midi_track(self):
        song = create_song()
        track = song.create_track(type=TrackType.MIDI_TRACK)
        self.assertAlmostEqual(track.get_volume(), db_to_volume_value(0))
        self.assertEqual(track.get_pan(), 0)
        self.assertEqual(track.get_solo(), False)
        self.assertEqual(track.get_muted(), False)
        self.assertEqual(track.get_type(), TrackType.MIDI_TRACK)

    def test_create_audio_track(self):
        song = create_song()
        track = song.create_track(type=TrackType.AUDIO_TRACK)
        self.assertAlmostEqual(track.get_volume(), db_to_volume_value(0))
        self.assertEqual(track.get_pan(), 0)
        self.assertEqual(track.get_solo(), False)
        self.assertEqual(track.get_muted(), False)
        self.assertEqual(track.get_type(), TrackType.AUDIO_TRACK)

    def test_create_track_returns_correct_reference(self):
        song = create_song()
        self.assertEqual(song.get_track_count(), 0)
        new_track = song.create_track(type=TrackType.MIDI_TRACK)
        self.assertEqual(new_track.get_instrument().program, 0)  # type:ignore
        self.assertEqual(song.get_track_at(0).get_instrument().program, 0)  # type:ignore
        new_track.get_instrument().program = 127  # type:ignore
        self.assertEqual(new_track.get_instrument().program, 127)  # type:ignore
        self.assertEqual(song.get_track_at(0).get_instrument().program, 127)  # type:ignore


class TestAudioTracks(unittest.TestCase):
    def test_cannot_set_instrument_or_suggested_instrument_or_sampler_plugin(self):
        song = create_song()
        track = song.create_track(type=TrackType.AUDIO_TRACK)
        self.assertFalse(track.has_instrument())
        self.assertFalse(track.has_sampler_plugin())
        self.assertEqual(track.get_suggested_instruments_count(), 0)
        track.set_instrument(program=32, is_drum=False)
        self.assertFalse(track.has_instrument())
        track.set_sampler_plugin(AudioPlugin(name="plugin1", manufacturer_name="manufacturer1",
                                 plugin_format_name="VST", plugin_version="1.1"))
        self.assertIsNone(track.get_sampler_plugin())
        self.assertFalse(track.has_sampler_plugin())
        track.create_suggested_instrument(program=64, is_drum=False)
        self.assertEqual(track.get_suggested_instruments_count(), 0)

    def test_clone_audio_track(self):
        # TODO: Test
        pass


class TestMIDITracks(unittest.TestCase):
    def test_clone_midi_track(self):
        # TODO: Test
        pass

    def test_get_visible_notes(self):
        song = create_song()
        track = song.create_track(type=TrackType.MIDI_TRACK)
        clip1 = track.create_midi_clip(clip_start_tick=10, clip_end_tick=20, insert_clip=True)
        clip2 = track.create_midi_clip(clip_start_tick=20, clip_end_tick=30, insert_clip=True)
        clip1.create_note(pitch=72, velocity=100, start_tick=10, end_tick=11)
        clip1.create_note(pitch=73, velocity=100, start_tick=11, end_tick=12)
        clip1.create_note(pitch=74, velocity=100, start_tick=12, end_tick=13)
        clip2.create_note(pitch=75, velocity=100, start_tick=20, end_tick=21)
        clip2.create_note(pitch=76, velocity=100, start_tick=21, end_tick=22)
        clip2.create_note(pitch=77, velocity=100, start_tick=22, end_tick=23)
        assert_notes_are_equal(track.get_visible_notes(), create_test_notes([
            {'pitch': 72, 'velocity': 100, 'start_tick': 10, 'end_tick': 11, 'id': 1},
            {'pitch': 73, 'velocity': 100, 'start_tick': 11, 'end_tick': 12, 'id': 2},
            {'pitch': 74, 'velocity': 100, 'start_tick': 12, 'end_tick': 13, 'id': 3},
            {'pitch': 75, 'velocity': 100, 'start_tick': 20, 'end_tick': 21, 'id': 1},
            {'pitch': 76, 'velocity': 100, 'start_tick': 21, 'end_tick': 22, 'id': 2},
            {'pitch': 77, 'velocity': 100, 'start_tick': 22, 'end_tick': 23, 'id': 3}
        ], clip1))


class TestCloneClip(unittest.TestCase):
    def test_clone_clip(self):
        song = create_song()
        track = song.create_track(type=TrackType.MIDI_TRACK)
        clip1 = track.create_midi_clip(clip_start_tick=10, clip_end_tick=20, insert_clip=True)
        clip1.create_note(pitch=72, velocity=100, start_tick=15, end_tick=16)
        clip2 = track.clone_clip(clip1)
        self.assertNotEqual(clip1.get_id(), clip2.get_id())
        self.assertEqual(clip2.get_clip_start_tick(), clip1.get_clip_start_tick())
        self.assertEqual(clip2.get_clip_end_tick(), clip1.get_clip_end_tick())
        self.assertEqual(clip2.get_raw_note_at(0).get_pitch(), 72)


if __name__ == '__main__':
    unittest.main()
