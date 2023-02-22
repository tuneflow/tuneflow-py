from tuneflow_py.models.song import Song, TrackType
from tuneflow_py.models.audio_plugin import AudioPlugin
from tuneflow_py.utils import db_to_volume_value
from miditoolkit.midi import MidiFile
from pathlib import PurePath, Path
from io import BytesIO
import unittest


def create_song():
    song = Song()
    song.create_tempo_change(ticks=1440, bpm=60)
    return song


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


if __name__ == '__main__':
    unittest.main()
