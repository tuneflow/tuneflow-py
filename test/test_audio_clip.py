from tuneflow_py import Song, Clip, Track, TrackType, Note, ClipType
from miditoolkit.midi import MidiFile
from pathlib import PurePath, Path
from io import BytesIO
from typing import List
import unittest

TEST_AUDIO_CLIP_DATA = {
    "audio_file_path": 'file1',
    "start_tick": 480,
    "duration": 1,
}

TEST_AUDIO_CLIP_DATA_WITH_AUDIO_DATA = {
    "audio_data": {
        "data": bytes(),
        "format": "wav"
    },
    "start_tick": 480,
    "duration": 1,
}


def create_song():
    song = Song()
    song.create_tempo_change(ticks=1440, bpm=60)
    audio_track = song.create_track(type=TrackType.AUDIO_TRACK)
    midi_track = song.create_track(type=TrackType.MIDI_TRACK)
    return song, audio_track, midi_track


class BaseTestCase(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        [song, audio_track, midi_track] = create_song()
        self.song = song
        self.audio_track = audio_track
        self.midi_track = midi_track


class TestCreateAudioClip(BaseTestCase):
    def test_create_audio_clip_by_default(self):
        clip1 = self.audio_track.create_audio_clip(
            clip_start_tick=0,
            audio_clip_data=TEST_AUDIO_CLIP_DATA,
        )
        self.assertEqual(clip1.get_type(), ClipType.AUDIO_CLIP)
        clip2 = self.midi_track.create_midi_clip(
            clip_start_tick=0,
        )
        self.assertEqual(clip2.get_type(), ClipType.MIDI_CLIP)
        clip3 = self.audio_track.create_midi_clip(
            clip_start_tick=0,
        )
        self.assertEqual(clip3.get_type(), ClipType.MIDI_CLIP)
        clip4 = self.midi_track.create_audio_clip(
            clip_start_tick=0,
            audio_clip_data=TEST_AUDIO_CLIP_DATA,
        )
        self.assertEqual(clip4.get_type(), ClipType.AUDIO_CLIP)


class TestAudioClipCannotCreateNotes(BaseTestCase):
    def test_cannot_create_note_in_audio_clip(self):
        clip1 = self.audio_track.create_audio_clip(
            clip_start_tick=0,
            audio_clip_data=TEST_AUDIO_CLIP_DATA,
        )
        self.assertEqual(clip1.get_raw_note_count(), 0)
        new_note = clip1.create_note(
            pitch=64,
            velocity=64,
            start_tick=0,
            end_tick=100,
        )
        self.assertIsNone(new_note)
        self.assertEqual(clip1.get_raw_note_count(), 0)


class TestBasicGetAndSetOperations(BaseTestCase):
    def test_get_audio_related_fields(self):
        clip1 = self.audio_track.create_audio_clip(
            clip_start_tick=480,
            audio_clip_data=TEST_AUDIO_CLIP_DATA,
        )
        self.assertEqual(clip1.get_clip_end_tick(), 1440)
        self.assertEqual(clip1.get_audio_duration(), 1)
        self.assertEqual(clip1.get_audio_end_tick(), 1440)
        self.assertEqual(clip1.get_audio_clip_data().audio_file_path, TEST_AUDIO_CLIP_DATA["audio_file_path"])
        self.assertEqual(clip1.get_audio_clip_data().start_tick, TEST_AUDIO_CLIP_DATA["start_tick"])
        self.assertAlmostEqual(clip1.get_audio_clip_data().duration, TEST_AUDIO_CLIP_DATA["duration"])

    def test_get_audio_related_fields_with_audio_data(self):
        clip1 = self.audio_track.create_audio_clip(
            clip_start_tick=480,
            audio_clip_data=TEST_AUDIO_CLIP_DATA_WITH_AUDIO_DATA,
        )
        self.assertEqual(clip1.get_clip_end_tick(), 1440)
        self.assertEqual(clip1.get_audio_duration(), 1)
        self.assertEqual(clip1.get_audio_end_tick(), 1440)
        self.assertEqual(clip1.get_audio_clip_data().audio_file_path, "")
        self.assertEqual(clip1.get_audio_clip_data().audio_data.format,
                         TEST_AUDIO_CLIP_DATA_WITH_AUDIO_DATA["audio_data"]["format"])
        self.assertEqual(clip1.get_audio_clip_data().audio_data.data,
                         TEST_AUDIO_CLIP_DATA_WITH_AUDIO_DATA["audio_data"]["data"])
        self.assertEqual(clip1.get_audio_clip_data().start_tick, TEST_AUDIO_CLIP_DATA_WITH_AUDIO_DATA["start_tick"])
        self.assertAlmostEqual(clip1.get_audio_clip_data().duration, TEST_AUDIO_CLIP_DATA_WITH_AUDIO_DATA["duration"])

    def test_set_and_get_custom_clip_start_and_end_tick_out_of_audio_range(self):
        clip1 = self.audio_track.create_audio_clip(
            clip_start_tick=120,
            clip_end_tick=9000,
            audio_clip_data=TEST_AUDIO_CLIP_DATA,
        )
        self.assertEqual(clip1.get_clip_start_tick(), 480)
        self.assertEqual(clip1.get_clip_end_tick(), 1440)
        self.assertEqual(clip1.get_audio_duration(), 1)
        self.assertEqual(clip1.get_audio_end_tick(), 1440)
        self.assertEqual(clip1.get_audio_clip_data().audio_file_path, TEST_AUDIO_CLIP_DATA["audio_file_path"])
        self.assertEqual(clip1.get_audio_clip_data().start_tick, TEST_AUDIO_CLIP_DATA["start_tick"])
        self.assertAlmostEqual(clip1.get_audio_clip_data().duration, TEST_AUDIO_CLIP_DATA["duration"])

    def test_set_and_get_custom_clip_start_and_end_tick_within_audio_range(self):
        clip1 = self.audio_track.create_audio_clip(
            clip_start_tick=960,
            clip_end_tick=1000,
            audio_clip_data=TEST_AUDIO_CLIP_DATA,
        )
        self.assertEqual(clip1.get_clip_start_tick(), 960)
        self.assertEqual(clip1.get_clip_end_tick(), 1000)
        self.assertEqual(clip1.get_audio_duration(), 1)
        self.assertEqual(clip1.get_audio_end_tick(), 1440)
        self.assertEqual(clip1.get_audio_clip_data().audio_file_path, TEST_AUDIO_CLIP_DATA["audio_file_path"])
        self.assertEqual(clip1.get_audio_clip_data().start_tick, TEST_AUDIO_CLIP_DATA["start_tick"])
        self.assertAlmostEqual(clip1.get_audio_clip_data().duration, TEST_AUDIO_CLIP_DATA["duration"])


class TestTrimLeftAndTrimRight(BaseTestCase):
    def test_trim_left_within_audio_range(self):
        clip1 = self.audio_track.create_audio_clip(
            clip_start_tick=960,
            clip_end_tick=1000,
            audio_clip_data=TEST_AUDIO_CLIP_DATA,
        )
        self.assertEqual(clip1.get_clip_start_tick(), 960)
        self.assertEqual(clip1.get_clip_end_tick(), 1000)
        clip1.adjust_clip_left(600)
        self.assertEqual(clip1.get_clip_start_tick(), 600)
        self.assertEqual(clip1.get_clip_end_tick(), 1000)

    def test_trim_left_out_of_audio_range(self):
        clip1 = self.audio_track.create_audio_clip(
            clip_start_tick=960,
            clip_end_tick=1000,
            audio_clip_data=TEST_AUDIO_CLIP_DATA,
        )
        self.assertEqual(clip1.get_clip_start_tick(), 960)
        self.assertEqual(clip1.get_clip_end_tick(), 1000)
        clip1.adjust_clip_left(-100)
        self.assertEqual(clip1.get_clip_start_tick(), 480)
        self.assertEqual(clip1.get_clip_end_tick(), 1000)

    def test_trim_right_within_audio_range(self):
        clip1 = self.audio_track.create_audio_clip(
            clip_start_tick=960,
            clip_end_tick=1000,
            audio_clip_data=TEST_AUDIO_CLIP_DATA,
        )
        self.assertEqual(clip1.get_clip_start_tick(), 960)
        self.assertEqual(clip1.get_clip_end_tick(), 1000)
        clip1.adjust_clip_right(980)
        self.assertEqual(clip1.get_clip_start_tick(), 960)
        self.assertEqual(clip1.get_clip_end_tick(), 980)

    def test_trim_right_out_of_audio_range(self):
        clip1 = self.audio_track.create_audio_clip(
            clip_start_tick=960,
            clip_end_tick=1000,
            audio_clip_data=TEST_AUDIO_CLIP_DATA,
        )
        self.assertEqual(clip1.get_clip_start_tick(), 960)
        self.assertEqual(clip1.get_clip_end_tick(), 1000)
        clip1.adjust_clip_right(2000)
        self.assertEqual(clip1.get_clip_start_tick(), 960)
        self.assertEqual(clip1.get_clip_end_tick(), 1440)


class TestMoveClip(BaseTestCase):
    def test_move_clip_within_tempo_range(self):
        clip1 = self.audio_track.create_audio_clip(
            clip_start_tick=960,
            clip_end_tick=1200,
            audio_clip_data={
                "audio_file_path": 'file1',
                "start_tick": 480,
                "duration": 1,
            },
        )
        self.assertEqual(clip1.get_clip_start_tick(), 960)
        self.assertEqual(clip1.get_clip_end_tick(), 1200)
        self.assertAlmostEqual(clip1.get_duration(), 0.25)
        self.assertEqual(clip1.get_audio_duration(), 1)
        self.assertEqual(clip1.get_audio_end_tick(), 1440)
        clip1.move_clip(-480, move_associated_track_automation_points=False)
        self.assertEqual(clip1.get_clip_start_tick(), 480)
        self.assertEqual(clip1.get_clip_end_tick(), 720)
        self.assertAlmostEqual(clip1.get_duration(), 0.25)
        self.assertEqual(clip1.get_audio_clip_data().audio_file_path, 'file1')
        self.assertEqual(clip1.get_audio_clip_data().duration, 1)
        self.assertEqual(clip1.get_audio_clip_data().start_tick, 0)
        self.assertEqual(clip1.get_audio_end_tick(), 960)

    def test_move_clip_to_the_right_cross_tempo_ranges(self):
        clip1 = self.audio_track.create_audio_clip(
            clip_start_tick=960,
            clip_end_tick=1200,
            audio_clip_data={
                "audio_file_path": 'file1',
                "start_tick": 480,
                "duration": 1,
            },
        )
        self.assertEqual(clip1.get_clip_start_tick(), 960)
        self.assertEqual(clip1.get_clip_end_tick(), 1200)
        self.assertAlmostEqual(clip1.get_duration(), 0.25)
        self.assertEqual(clip1.get_audio_duration(), 1)
        self.assertEqual(clip1.get_audio_end_tick(), 1440)
        clip1.move_clip(480, move_associated_track_automation_points=False)
        self.assertEqual(clip1.get_clip_start_tick(), 1440)
        self.assertEqual(clip1.get_clip_end_tick(), 1560)
        self.assertAlmostEqual(clip1.get_duration(), 0.25)
        self.assertEqual(clip1.get_audio_clip_data().audio_file_path, 'file1')
        self.assertEqual(clip1.get_audio_clip_data().duration, 1)
        self.assertEqual(clip1.get_audio_clip_data().start_tick, 960)
        self.assertEqual(clip1.get_audio_end_tick(), 1680)

    def test_move_clip_to_the_left_cross_tempo_ranges(self):
        clip1 = self.audio_track.create_audio_clip(
            clip_start_tick=1320,
            clip_end_tick=1560,
            audio_clip_data={
                "audio_file_path": 'file2',
                "start_tick": 1200,
                "duration": 1,
            },
        )
        self.assertEqual(clip1.get_audio_duration(), 1)
        self.assertEqual(clip1.get_audio_end_tick(), 1800)
        self.assertEqual(clip1.get_clip_start_tick(), 1320)
        self.assertEqual(clip1.get_clip_end_tick(), 1560)
        self.assertAlmostEqual(clip1.get_duration(), 0.375)
        clip1.move_clip(-120, move_associated_track_automation_points=False)
        self.assertEqual(clip1.get_clip_start_tick(), 1200)
        self.assertEqual(clip1.get_clip_end_tick(), 1500)
        self.assertAlmostEqual(clip1.get_duration(), 0.375)
        self.assertEqual(clip1.get_audio_clip_data().audio_file_path, 'file2')
        self.assertEqual(clip1.get_audio_clip_data().duration, 1)
        self.assertEqual(clip1.get_audio_clip_data().start_tick, 1080)
        self.assertEqual(clip1.get_audio_end_tick(), 1740)

    def test_move_clip_to_the_left_cross_0(self):
        clip1 = self.audio_track.create_audio_clip(
            clip_start_tick=1320,
            clip_end_tick=1560,
            audio_clip_data={
                "audio_file_path": 'file2',
                "start_tick": 1200,
                "duration": 1,
            },
        )
        self.assertEqual(clip1.get_audio_end_tick(), 1800)
        self.assertEqual(clip1.get_clip_start_tick(), 1320)
        self.assertEqual(clip1.get_clip_end_tick(), 1560)
        self.assertAlmostEqual(clip1.get_duration(), 0.375)
        clip1.move_clip(-1440, move_associated_track_automation_points=False)
        self.assertEqual(clip1.get_clip_start_tick(), 0)
        self.assertEqual(clip1.get_clip_end_tick(), 240)
        self.assertAlmostEqual(clip1.get_duration(), 0.25)
        self.assertEqual(clip1.get_audio_clip_data().audio_file_path, 'file2')
        self.assertEqual(clip1.get_audio_clip_data().duration, 1)
        self.assertEqual(clip1.get_audio_clip_data().start_tick, -240)
        self.assertEqual(clip1.get_audio_end_tick(), 720)

    def test_move_clip_to_the_left_cross_tempo_and_0(self):
        clip1 = self.audio_track.create_audio_clip(
            clip_start_tick=1920,
            clip_end_tick=2040,
            audio_clip_data={
                "audio_file_path": 'file3',
                "start_tick": 1680,
                "duration": 1,
            },
        )
        self.assertEqual(clip1.get_audio_end_tick(), 2160)
        self.assertEqual(clip1.get_clip_start_tick(), 1920)
        self.assertEqual(clip1.get_clip_end_tick(), 2040)
        self.assertAlmostEqual(clip1.get_duration(), 0.25)
        clip1.move_clip(-2040, move_associated_track_automation_points=False)
        self.assertEqual(clip1.get_clip_start_tick(), 0)
        self.assertEqual(clip1.get_clip_end_tick(), 120)
        self.assertAlmostEqual(clip1.get_duration(), 0.125)
        self.assertEqual(clip1.get_audio_clip_data().audio_file_path, 'file3')
        self.assertEqual(clip1.get_audio_clip_data().duration, 1)
        self.assertEqual(clip1.get_audio_clip_data().start_tick, -600)
        self.assertEqual(clip1.get_audio_end_tick(), 360)


class TestResolveConflict(BaseTestCase):
    def test_create_clip_in_the_middle_of_another_clip(self):
        self.audio_track.create_audio_clip(
            clip_start_tick=0,
            clip_end_tick=960,
            audio_clip_data={
                "audio_file_path": 'file1',
                "start_tick": 0,
                "duration": 1,
            },
        )
        self.audio_track.create_audio_clip(
            clip_start_tick=240,
            clip_end_tick=720,
            audio_clip_data={
                "audio_file_path": 'file2',
                "start_tick": 240,
                "duration": 0.5,
            },
        )
        self.assertEqual(self.audio_track.get_clip_count(), 3)
        self.assertEqual(self.audio_track.get_clip_at(0).get_clip_start_tick(), 0)
        self.assertEqual(self.audio_track.get_clip_at(0).get_clip_end_tick(), 239)
        self.assertEqual(self.audio_track.get_clip_at(0).get_audio_clip_data().audio_file_path, 'file1')
        self.assertEqual(self.audio_track.get_clip_at(0).get_audio_clip_data().duration, 1)
        self.assertEqual(self.audio_track.get_clip_at(0).get_audio_clip_data().start_tick, 0)
        self.assertEqual(self.audio_track.get_clip_at(1).get_clip_start_tick(), 240)
        self.assertEqual(self.audio_track.get_clip_at(1).get_clip_end_tick(), 720)
        self.assertEqual(self.audio_track.get_clip_at(1).get_audio_clip_data().audio_file_path, 'file2')
        self.assertAlmostEqual(self.audio_track.get_clip_at(1).get_audio_clip_data().duration, 0.5)
        self.assertEqual(self.audio_track.get_clip_at(1).get_audio_clip_data().start_tick, 240)
        self.assertEqual(self.audio_track.get_clip_at(2).get_clip_start_tick(), 721)
        self.assertEqual(self.audio_track.get_clip_at(2).get_clip_end_tick(), 960)
        self.assertEqual(self.audio_track.get_clip_at(2).get_audio_clip_data().audio_file_path, 'file1')
        self.assertAlmostEqual(self.audio_track.get_clip_at(2).get_audio_clip_data().duration, 1)
        self.assertEqual(self.audio_track.get_clip_at(2).get_audio_clip_data().start_tick, 0)

    def test_create_clip_to_the_left_of_another_clip(self):
        self.audio_track.create_audio_clip(
            clip_start_tick=0,
            clip_end_tick=960,
            audio_clip_data={
                "audio_file_path": 'file1',
                "start_tick": 0,
                "duration": 1,
            },
        )
        self.audio_track.create_audio_clip(
            clip_start_tick=0,
            clip_end_tick=240,
            audio_clip_data={
                "audio_file_path": 'file2',
                "start_tick": 0,
                "duration": 0.25,
            },
        )
        self.assertEqual(self.audio_track.get_clip_count(), 2)
        self.assertEqual(self.audio_track.get_clip_at(0).get_clip_start_tick(), 0)
        self.assertEqual(self.audio_track.get_clip_at(0).get_clip_end_tick(), 240)
        self.assertEqual(self.audio_track.get_clip_at(0).get_audio_clip_data().audio_file_path, 'file2')
        self.assertAlmostEqual(self.audio_track.get_clip_at(0).get_audio_clip_data().duration, 0.25)
        self.assertEqual(self.audio_track.get_clip_at(0).get_audio_clip_data().start_tick, 0)
        self.assertEqual(self.audio_track.get_clip_at(1).get_clip_start_tick(), 241)
        self.assertEqual(self.audio_track.get_clip_at(1).get_clip_end_tick(), 960)
        self.assertEqual(self.audio_track.get_clip_at(1).get_audio_clip_data().audio_file_path, 'file1')
        self.assertAlmostEqual(self.audio_track.get_clip_at(1).get_audio_clip_data().duration, 1)
        self.assertEqual(self.audio_track.get_clip_at(1).get_audio_clip_data().start_tick, 0)

    def test_create_clip_to_the_right_of_another_clip(self):
        self.audio_track.create_audio_clip(
            clip_start_tick=0,
            clip_end_tick=960,
            audio_clip_data={
                "audio_file_path": 'file1',
                "start_tick": 0,
                "duration": 1,
            },
        )
        self.audio_track.create_audio_clip(
            clip_start_tick=720,
            clip_end_tick=960,
            audio_clip_data={
                "audio_file_path": 'file2',
                "start_tick": 720,
                "duration": 0.25,
            },
        )
        self.assertEqual(self.audio_track.get_clip_count(), 2)
        self.assertEqual(self.audio_track.get_clip_at(0).get_clip_start_tick(), 0)
        self.assertEqual(self.audio_track.get_clip_at(0).get_clip_end_tick(), 719)
        self.assertEqual(self.audio_track.get_clip_at(0).get_audio_clip_data().audio_file_path, 'file1')
        self.assertAlmostEqual(self.audio_track.get_clip_at(0).get_audio_clip_data().duration, 1)
        self.assertEqual(self.audio_track.get_clip_at(0).get_audio_clip_data().start_tick, 0)

        self.assertEqual(self.audio_track.get_clip_at(1).get_clip_start_tick(), 720)
        self.assertEqual(self.audio_track.get_clip_at(1).get_clip_end_tick(), 960)
        self.assertEqual(self.audio_track.get_clip_at(1).get_audio_clip_data().audio_file_path, 'file2')
        self.assertAlmostEqual(self.audio_track.get_clip_at(1).get_audio_clip_data().duration, 0.25)
        self.assertEqual(self.audio_track.get_clip_at(1).get_audio_clip_data().start_tick, 720)

    def test_trim_left_edge_overlaps_with_another_clip(self):
        clip1 = self.audio_track.create_audio_clip(
            clip_start_tick=0,
            clip_end_tick=480,
            audio_clip_data={
                "audio_file_path": 'file1',
                "start_tick": 0,
                "duration": 0.5,
            },
        )
        clip2 = self.audio_track.create_audio_clip(
            clip_start_tick=720,
            clip_end_tick=960,
            audio_clip_data={
                "audio_file_path": 'file2',
                "start_tick": 360,
                "duration": 1,
            },
        )
        self.assertEqual(self.audio_track.get_clip_count(), 2)
        clip2.adjust_clip_left(240, resolve_conflict=True)
        self.assertEqual(clip1.get_clip_start_tick(), 0)
        self.assertEqual(clip1.get_clip_end_tick(), 359)
        self.assertEqual(clip1.get_audio_clip_data().audio_file_path, 'file1')
        self.assertAlmostEqual(clip1.get_audio_clip_data().duration, 0.5)
        self.assertEqual(clip1.get_audio_clip_data().start_tick, 0)
        self.assertEqual(clip2.get_clip_start_tick(), 360)
        self.assertEqual(clip2.get_clip_end_tick(), 960)
        self.assertEqual(clip2.get_audio_clip_data().audio_file_path, 'file2')
        self.assertAlmostEqual(clip2.get_audio_clip_data().duration, 1)
        self.assertEqual(clip2.get_audio_clip_data().start_tick, 360)

    def test_trim_right_edge_overlaps_with_another_clip(self):
        clip1 = self.audio_track.create_audio_clip(
            clip_start_tick=0,
            clip_end_tick=240,
            audio_clip_data={
                "audio_file_path": 'file1',
                "start_tick": 0,
                "duration": 0.75,
            },
        )
        clip2 = self.audio_track.create_audio_clip(
            clip_start_tick=480,
            clip_end_tick=960,
            audio_clip_data={
                "audio_file_path": 'file2',
                "start_tick": 360,
                "duration": 1,
            },
        )
        self.assertEqual(self.audio_track.get_clip_count(), 2)
        clip1.adjust_clip_right(800, resolve_conflict=True)
        self.assertEqual(clip1.get_clip_start_tick(), 0)
        self.assertEqual(clip1.get_clip_end_tick(), 720)
        self.assertEqual(clip1.get_audio_clip_data().audio_file_path, 'file1')
        self.assertAlmostEqual(clip1.get_audio_clip_data().duration, 0.75)
        self.assertEqual(clip1.get_audio_clip_data().start_tick, 0)
        self.assertEqual(clip2.get_clip_start_tick(), 721)
        self.assertEqual(clip2.get_clip_end_tick(), 960)
        self.assertEqual(clip2.get_audio_clip_data().audio_file_path, 'file2')
        self.assertAlmostEqual(clip2.get_audio_clip_data().duration, 1)
        self.assertEqual(clip2.get_audio_clip_data().start_tick, 360)


if __name__ == '__main__':
    unittest.main()
