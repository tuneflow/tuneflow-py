from tuneflow_py import Song, Clip, TrackType, Note
from typing import List
import unittest


def create_song():
    song = Song()
    song.create_tempo_change(ticks=1440, bpm=60)
    track = song.create_track(type=TrackType.MIDI_TRACK)
    clip1 = track.create_midi_clip(clip_start_tick=0)
    clip1.create_note(pitch=64, velocity=80, start_tick=0, end_tick=10)
    clip1.create_note(pitch=66, velocity=80, start_tick=15, end_tick=20)
    clip1.create_note(pitch=68, velocity=80, start_tick=14, end_tick=20)
    clip1.adjust_clip_left(0)
    clip1.adjust_clip_right(15)
    clip2 = track.create_midi_clip(clip_start_tick=21)
    clip2.create_note(pitch=66, velocity=80, start_tick=25, end_tick=30)
    clip2.create_note(pitch=64, velocity=80, start_tick=18, end_tick=35)
    clip2.create_note(pitch=68, velocity=80, start_tick=24, end_tick=35)
    clip2.adjust_clip_left(21)
    clip2.adjust_clip_right(30)
    clip3 = track.create_midi_clip(clip_start_tick=40)
    clip3.create_note(pitch=71, velocity=80, start_tick=55, end_tick=65)
    clip3.create_note(pitch=69, velocity=80, start_tick=45, end_tick=50)
    clip3.create_note(pitch=67, velocity=80, start_tick=40, end_tick=45)
    clip3.adjust_clip_left(40)
    clip3.adjust_clip_right(65)
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


class BaseTestCase(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        song = create_song()
        self.song = song

    def assert_clip_range(self, clip: Clip, start_tick: int, end_tick: int):
        self.assertEqual(clip.get_clip_start_tick(), start_tick)
        self.assertEqual(clip.get_clip_end_tick(), end_tick)

# class TestIsNoteInClip(BaseTestCase):
#     def test_is_note_in_clip(self):
#         self.assertFalse(Clip.is_note_in_clip(note_start_tick=4, note_end_tick=5,clip_start_tick=6,clip_end_tick=12))
#         self.assertFalse(Clip.is_note_in_clip(note_start_tick=5, note_end_tick=10,clip_start_tick=6,clip_end_tick=12))
#         self.assertTrue(Clip.is_note_in_clip(note_start_tick=6, note_end_tick=10,clip_start_tick=6,clip_end_tick=12))
#         self.assertTrue(Clip.is_note_in_clip(note_start_tick=6, note_end_tick=12,clip_start_tick=6,clip_end_tick=12))
#         self.assertTrue(Clip.is_note_in_clip(note_start_tick=7, note_end_tick=12,clip_start_tick=6,clip_end_tick=12))
#         self.assertTrue(Clip.is_note_in_clip(note_start_tick=7, note_end_tick=13,clip_start_tick=6,clip_end_tick=12))
#         self.assertFalse(Clip.is_note_in_clip(note_start_tick=12, note_end_tick=13,clip_start_tick=6,clip_end_tick=12))
#         self.assertFalse(Clip.is_note_in_clip(note_start_tick=13, note_end_tick=15,clip_start_tick=6,clip_end_tick=12))
#         self.assertFalse(Clip.is_note_in_clip(note_start_tick=5, note_end_tick=15,clip_start_tick=6,clip_end_tick=12))
#         self.assertTrue(Clip.is_note_in_clip(note_start_tick=-13, note_end_tick=5,clip_start_tick=0,clip_end_tick=12))


class TestBasicOperations(BaseTestCase):
    def test_gets_clip_ranges(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 3)
        clip1 = track.get_clip_at(0)
        self.assertEqual(clip1.get_clip_start_tick(), 0)
        self.assertEqual(clip1.get_clip_end_tick(), 15)

    def test_get_notes_within_clip_range(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 3)
        clip1 = track.get_clip_at(0)
        clip2 = track.get_clip_at(1)
        clip3 = track.get_clip_at(2)
        # Notes that are at the edge are included.
        assert_notes_are_equal(
            list(clip1.get_notes()),
            create_test_notes(
                [
                    {
                        "id": 1,
                        "pitch": 64,
                        "velocity": 80,
                        "start_tick": 0,
                        "end_tick": 10,
                    },
                    {
                        "id": 3,
                        "pitch": 68,
                        "velocity": 80,
                        "start_tick": 14,
                        "end_tick": 20,
                    },
                ],
                clip1,
            ),
        )
        # Note that start before the clip start are excluded.
        assert_notes_are_equal(
            list(clip2.get_notes()),
            create_test_notes(
                [
                    {
                        "pitch": 68,
                        "velocity": 80,
                        "start_tick": 24,
                        "end_tick": 35,
                        "id": 3
                    },
                    {
                        "pitch": 66,
                        "velocity": 80,
                        "start_tick": 25,
                        "end_tick": 30,
                        "id": 1
                    },
                ],
                clip2,
            ),
        )
        # Note are sorted and all notes that are within clip are returned.
        assert_notes_are_equal(
            list(clip3.get_notes()),
            create_test_notes(
                [
                    {
                        "pitch": 67,
                        "velocity": 80,
                        "start_tick": 40,
                        "end_tick": 45,
                        "id": 3
                    },
                    {
                        "pitch": 69,
                        "velocity": 80,
                        "start_tick": 45,
                        "end_tick": 50,
                        "id": 2
                    },
                    {
                        "pitch": 71,
                        "velocity": 80,
                        "start_tick": 55,
                        "end_tick": 65,
                        "id": 1
                    },
                ],
                clip3,
            ),
        )


class TestCreateClip(BaseTestCase):
    def test_create_clip_returns_correct_reference(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 3)
        clip3 = self.song.get_track_at(0).create_midi_clip(
            clip_start_tick=999, clip_end_tick=1000)
        self.assertEqual(track.get_clip_at(3).get_clip_end_tick(), 1000)
        self.assertEqual(clip3.get_clip_end_tick(), 1000)
        clip3.adjust_clip_right(1200)
        self.assertEqual(track.get_clip_at(3).get_clip_end_tick(), 1200)
        self.assertEqual(clip3.get_clip_end_tick(), 1200)


class TestCreateNotes(BaseTestCase):
    def test_reject_creating_note_with_invalid_pitch(self):
        clip1 = self.song.get_track_at(0).get_clip_at(0)
        self.assertEqual(clip1.get_raw_note_count(), 3)
        assert_notes_are_equal(
            list(clip1.get_raw_notes()),
            create_test_notes(
                [
                    {
                        "pitch": 64,
                        "velocity": 80,
                        "start_tick": 0,
                        "end_tick": 10,
                        "id": 1
                    },
                    {
                        "pitch": 68,
                        "velocity": 80,
                        "start_tick": 14,
                        "end_tick": 20,
                        "id": 3
                    },
                    {
                        "pitch": 66,
                        "velocity": 80,
                        "start_tick": 15,
                        "end_tick": 20,
                        "id": 2
                    },
                ],
                clip1,
            ),
        )

        # Create notes with invalid pitch.
        created_note1 = clip1.create_note(
            pitch=128,
            velocity=80,
            start_tick=2,
            end_tick=8,
        )
        self.assertIsNone(created_note1)
        created_note2 = clip1.create_note(
            pitch=-1,
            velocity=80,
            start_tick=2,
            end_tick=8,
        )
        self.assertIsNone(created_note2)
        self.assertEqual(clip1.get_raw_note_count(), 3)
        assert_notes_are_equal(
            list(clip1.get_raw_notes()),
            create_test_notes(
                [
                    {
                        "pitch": 64,
                        "velocity": 80,
                        "start_tick": 0,
                        "end_tick": 10,
                        "id": 1
                    },
                    {
                        "pitch": 68,
                        "velocity": 80,
                        "start_tick": 14,
                        "end_tick": 20,
                        "id": 3
                    },
                    {
                        "pitch": 66,
                        "velocity": 80,
                        "start_tick": 15,
                        "end_tick": 20,
                        "id": 2
                    },
                ],
                clip1,
            ),
        )

    def test_reject_creating_note_with_invalid_velocity(self):
        clip1 = self.song.get_track_at(0).get_clip_at(0)
        self.assertEqual(clip1.get_raw_note_count(), 3)
        assert_notes_are_equal(
            list(clip1.get_raw_notes()),
            create_test_notes(
                [
                    {
                        "pitch": 64,
                        "velocity": 80,
                        "start_tick": 0,
                        "end_tick": 10,
                        "id": 1
                    },
                    {
                        "pitch": 68,
                        "velocity": 80,
                        "start_tick": 14,
                        "end_tick": 20,
                        "id": 3
                    },
                    {
                        "pitch": 66,
                        "velocity": 80,
                        "start_tick": 15,
                        "end_tick": 20,
                        "id": 2
                    },
                ],
                clip1,
            ),
        )

        # Create notes with invalid pitch.
        created_note1 = clip1.create_note(
            pitch=58,
            velocity=128,
            start_tick=2,
            end_tick=8,
        )
        self.assertIsNone(created_note1)
        created_note2 = clip1.create_note(
            pitch=56,
            velocity=-1,
            start_tick=2,
            end_tick=8,
        )
        self.assertIsNone(created_note2)
        self.assertEqual(clip1.get_raw_note_count(), 3)
        assert_notes_are_equal(
            list(clip1.get_raw_notes()),
            create_test_notes(
                [
                    {
                        "pitch": 64,
                        "velocity": 80,
                        "start_tick": 0,
                        "end_tick": 10,
                        "id": 1
                    },
                    {
                        "pitch": 68,
                        "velocity": 80,
                        "start_tick": 14,
                        "end_tick": 20,
                        "id": 3
                    },
                    {
                        "pitch": 66,
                        "velocity": 80,
                        "start_tick": 15,
                        "end_tick": 20,
                        "id": 2
                    },
                ],
                clip1,
            ),
        )

    def test_reject_creating_note_with_invalid_range(self):
        clip1 = self.song.get_track_at(0).get_clip_at(0)
        self.assertEqual(clip1.get_raw_note_count(), 3)
        assert_notes_are_equal(
            list(clip1.get_raw_notes()),
            create_test_notes(
                [
                    {
                        "pitch": 64,
                        "velocity": 80,
                        "start_tick": 0,
                        "end_tick": 10,
                        "id": 1
                    },
                    {
                        "pitch": 68,
                        "velocity": 80,
                        "start_tick": 14,
                        "end_tick": 20,
                        "id": 3
                    },
                    {
                        "pitch": 66,
                        "velocity": 80,
                        "start_tick": 15,
                        "end_tick": 20,
                        "id": 2
                    },
                ],
                clip1,
            ),
        )

        # Create notes with invalid pitch.
        created_note1 = clip1.create_note(
            pitch=58,
            velocity=80,
            start_tick=-20,
            end_tick=-1,
        )
        self.assertIsNone(created_note1)
        created_note2 = clip1.create_note(
            pitch=56,
            velocity=80,
            start_tick=9,
            end_tick=8,
        )
        self.assertIsNone(created_note2)
        self.assertEqual(clip1.get_raw_note_count(), 3)
        assert_notes_are_equal(
            list(clip1.get_raw_notes()),
            create_test_notes(
                [
                    {
                        "pitch": 64,
                        "velocity": 80,
                        "start_tick": 0,
                        "end_tick": 10,
                        "id": 1
                    },
                    {
                        "pitch": 68,
                        "velocity": 80,
                        "start_tick": 14,
                        "end_tick": 20,
                        "id": 3
                    },
                    {
                        "pitch": 66,
                        "velocity": 80,
                        "start_tick": 15,
                        "end_tick": 20,
                        "id": 2
                    },
                ],
                clip1,
            ),
        )

    def test_create_note_with_valid_params(self):
        clip1 = self.song.get_track_at(0).get_clip_at(0)
        self.assertEqual(clip1.get_raw_note_count(), 3)
        assert_notes_are_equal(
            list(clip1.get_raw_notes()),
            create_test_notes(
                [
                    {
                        "pitch": 64,
                        "velocity": 80,
                        "start_tick": 0,
                        "end_tick": 10,
                        "id": 1
                    },
                    {
                        "pitch": 68,
                        "velocity": 80,
                        "start_tick": 14,
                        "end_tick": 20,
                        "id": 3
                    },
                    {
                        "pitch": 66,
                        "velocity": 80,
                        "start_tick": 15,
                        "end_tick": 20,
                        "id": 2
                    },
                ],
                clip1,
            ),
        )

        # Create notes with invalid pitch.
        created_note1 = clip1.create_note(
            pitch=58,
            velocity=80,
            start_tick=12,
            end_tick=14,
        )
        assert_notes_are_equal(
            [created_note1],
            create_test_notes(
                [
                    {
                        "pitch": 58,
                        "velocity": 80,
                        "start_tick": 12,
                        "end_tick": 14,
                        "id": 4
                    },
                ],
                clip1,
            ),
        )
        self.assertEqual(clip1.get_raw_note_count(), 4)
        assert_notes_are_equal(
            list(clip1.get_raw_notes()),
            create_test_notes(
                [
                    {
                        "pitch": 64,
                        "velocity": 80,
                        "start_tick": 0,
                        "end_tick": 10,
                        "id": 1
                    },
                    {
                        "pitch": 58,
                        "velocity": 80,
                        "start_tick": 12,
                        "end_tick": 14,
                        "id": 4
                    },
                    {
                        "pitch": 68,
                        "velocity": 80,
                        "start_tick": 14,
                        "end_tick": 20,
                        "id": 3
                    },
                    {
                        "pitch": 66,
                        "velocity": 80,
                        "start_tick": 15,
                        "end_tick": 20,
                        "id": 2
                    },
                ],
                clip1,
            ),
        )

    def test_create_note_returns_correct_reference(self):
        clip1 = self.song.get_track_at(0).get_clip_at(0)
        self.assertEqual(clip1.get_raw_note_count(), 3)

        # Create notes with invalid pitch.
        created_note1 = clip1.create_note(
            pitch=127,
            velocity=80,
            start_tick=999,
            end_tick=1000,
        )

        self.assertEqual(clip1.get_raw_note_at(3).get_pitch(), 127)
        self.assertEqual(created_note1.get_pitch(), 127)  # type:ignore
        created_note1.set_pitch(1)  # type:ignore
        self.assertEqual(clip1.get_raw_note_at(3).get_pitch(), 1)
        self.assertEqual(created_note1.get_pitch(), 1)  # type:ignore


class TestMoveClips(BaseTestCase):
    def test_move_clips_no_overlapping(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 3)
        clip1 = track.get_clip_at(0)
        self.assert_clip_range(clip1, 0, 15)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip2, 21, 30)
        clip3 = track.get_clip_at(2)
        self.assert_clip_range(clip3, 40, 65)
        clip1.move_clip_to(70, move_associated_track_automation_points=False)
        self.assert_clip_range(clip1, 70, 85)
        self.assert_clip_range(clip2, 21, 30)
        self.assert_clip_range(clip3, 40, 65)

    def test_move_clips_overlaps_on_the_left_side(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 3)
        clip1 = track.get_clip_at(0)
        self.assert_clip_range(clip1, 0, 15)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip2, 21, 30)
        clip3 = track.get_clip_at(2)
        self.assert_clip_range(clip3, 40, 65)
        clip1.move_clip_to(10, move_associated_track_automation_points=False)
        self.assert_clip_range(clip1, 10, 25)
        self.assert_clip_range(clip2, 26, 30)
        self.assert_clip_range(clip3, 40, 65)

    def test_move_clips_overlaps_on_the_right_side(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 3)
        clip1 = track.get_clip_at(0)
        self.assert_clip_range(clip1, 0, 15)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip2, 21, 30)
        clip3 = track.get_clip_at(2)
        self.assert_clip_range(clip3, 40, 65)
        clip1.move_clip_to(60, move_associated_track_automation_points=False)
        self.assert_clip_range(clip1, 60, 75)
        self.assert_clip_range(clip2, 21, 30)
        self.assert_clip_range(clip3, 40, 59)

    def test_move_clips_overlaps_on_the_left_and_right_side(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 3)
        clip1 = track.get_clip_at(0)
        self.assert_clip_range(clip1, 0, 15)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip2, 21, 30)
        clip3 = track.get_clip_at(2)
        self.assert_clip_range(clip3, 40, 65)
        clip1.move_clip_to(28, move_associated_track_automation_points=False)
        self.assert_clip_range(clip1, 28, 43)
        self.assert_clip_range(clip2, 21, 27)
        self.assert_clip_range(clip3, 44, 65)

    def test_move_clips_overlaps_in_the_middle(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 3)
        clip1 = track.get_clip_at(0)
        self.assert_clip_range(clip1, 0, 15)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip2, 21, 30)
        clip3 = track.get_clip_at(2)
        self.assert_clip_range(clip3, 40, 65)
        clip2.move_clip_to(42, move_associated_track_automation_points=False)
        self.assertEqual(track.get_clip_count(), 4)
        clip1 = track.get_clip_at(0)
        self.assert_clip_range(clip1, 0, 15)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip2, 40, 41)
        clip3 = track.get_clip_at(2)
        self.assert_clip_range(clip3, 42, 51)
        clip4 = track.get_clip_at(3)
        self.assert_clip_range(clip4, 52, 65)

    def test_move_clips_delete_out_of_range_clip(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 3)
        clip1 = track.get_clip_at(0)
        self.assert_clip_range(clip1, 0, 15)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip2, 21, 30)
        clip3 = track.get_clip_at(2)
        self.assert_clip_range(clip3, 40, 65)
        clip1.move_clip(-99999, move_associated_track_automation_points=False)
        self.assertEqual(track.get_clip_count(), 2)
        clip1 = track.get_clip_at(0)
        self.assert_clip_range(clip1, 21, 30)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip2, 40, 65)

    def test_move_clips_move_associated_track_automation_points(self):
        # TODO: Add tests
        pass


class TestAdjustClipRanges(BaseTestCase):
    def test_adjust_clip_left_no_overlapping(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 3)
        clip1 = track.get_clip_at(0)
        self.assert_clip_range(clip1, 0, 15)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip2, 21, 30)
        clip3 = track.get_clip_at(2)
        self.assert_clip_range(clip3, 40, 65)
        clip3.adjust_clip_left(35)
        self.assert_clip_range(clip1, 0, 15)
        self.assert_clip_range(clip2, 21, 30)
        self.assert_clip_range(clip3, 35, 65)

    def test_adjust_clip_left_overlaps_on_the_right_side(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 3)
        clip1 = track.get_clip_at(0)
        self.assert_clip_range(clip1, 0, 15)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip2, 21, 30)
        clip3 = track.get_clip_at(2)
        self.assert_clip_range(clip3, 40, 65)
        clip3.adjust_clip_left(25)
        self.assert_clip_range(clip1, 0, 15)
        self.assert_clip_range(clip2, 21, 24)
        self.assert_clip_range(clip3, 25, 65)

    def test_adjust_clip_left_overlaps_on_the_whole_clip_and_on_the_right(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 3)
        clip1 = track.get_clip_at(0)
        self.assert_clip_range(clip1, 0, 15)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip2, 21, 30)
        clip3 = track.get_clip_at(2)
        self.assert_clip_range(clip3, 40, 65)
        clip3.adjust_clip_left(10)
        self.assertEqual(track.get_clip_count(), 2)
        clip1 = track.get_clip_at(0)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip1, 0, 9)
        self.assert_clip_range(clip2, 10, 65)

    def test_adjust_clip_left_overlaps_two_whole_clips(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 3)
        clip1 = track.get_clip_at(0)
        self.assert_clip_range(clip1, 0, 15)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip2, 21, 30)
        clip3 = track.get_clip_at(2)
        self.assert_clip_range(clip3, 40, 65)
        clip3.adjust_clip_left(-10)
        self.assertEqual(track.get_clip_count(), 1)
        clip1 = track.get_clip_at(0)
        self.assert_clip_range(clip1, 0, 65)

    def test_adjust_clip_right_no_overlapping(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 3)
        clip1 = track.get_clip_at(0)
        self.assert_clip_range(clip1, 0, 15)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip2, 21, 30)
        clip3 = track.get_clip_at(2)
        self.assert_clip_range(clip3, 40, 65)
        clip1.adjust_clip_right(18)
        self.assert_clip_range(clip1, 0, 18)
        self.assert_clip_range(clip2, 21, 30)
        self.assert_clip_range(clip3, 40, 65)

    def test_adjust_clip_right_overlaps_on_the_left_side(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 3)
        clip1 = track.get_clip_at(0)
        self.assert_clip_range(clip1, 0, 15)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip2, 21, 30)
        clip3 = track.get_clip_at(2)
        self.assert_clip_range(clip3, 40, 65)
        clip1.adjust_clip_right(25)
        self.assert_clip_range(clip1, 0, 25)
        self.assert_clip_range(clip2, 26, 30)
        self.assert_clip_range(clip3, 40, 65)

    def test_adjust_clip_right_overlaps_on_the_whole_clip_and_on_the_left(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 3)
        clip1 = track.get_clip_at(0)
        self.assert_clip_range(clip1, 0, 15)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip2, 21, 30)
        clip3 = track.get_clip_at(2)
        self.assert_clip_range(clip3, 40, 65)
        clip1.adjust_clip_right(50)
        self.assertEqual(track.get_clip_count(), 2)
        clip1 = track.get_clip_at(0)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip1, 0, 50)
        self.assert_clip_range(clip2, 51, 65)

    def test_adjust_clip_right_overlaps_two_whole_clips(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 3)
        clip1 = track.get_clip_at(0)
        self.assert_clip_range(clip1, 0, 15)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip2, 21, 30)
        clip3 = track.get_clip_at(2)
        self.assert_clip_range(clip3, 40, 65)
        clip1.adjust_clip_right(1000)
        self.assertEqual(track.get_clip_count(), 1)
        clip1 = track.get_clip_at(0)
        self.assert_clip_range(clip1, 0, 1000)

    def test_adjust_clip_range_no_overlapping(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 3)
        clip1 = track.get_clip_at(0)
        self.assert_clip_range(clip1, 0, 15)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip2, 21, 30)
        clip3 = track.get_clip_at(2)
        self.assert_clip_range(clip3, 40, 65)
        clip2.adjust_clip_left(18)
        clip2.adjust_clip_right(35)
        self.assert_clip_range(clip1, 0, 15)
        self.assert_clip_range(clip2, 18, 35)
        self.assert_clip_range(clip3, 40, 65)

    def test_adjust_clip_range_overlaps_on_the_left_side(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 3)
        clip1 = track.get_clip_at(0)
        self.assert_clip_range(clip1, 0, 15)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip2, 21, 30)
        clip3 = track.get_clip_at(2)
        self.assert_clip_range(clip3, 40, 65)
        clip2.adjust_clip_left(10)
        clip2.adjust_clip_right(35)
        self.assert_clip_range(clip1, 0, 9)
        self.assert_clip_range(clip2, 10, 35)
        self.assert_clip_range(clip3, 40, 65)

    def test_adjust_clip_range_overlaps_on_the_whole_clip_to_the_left(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 3)
        clip1 = track.get_clip_at(0)
        self.assert_clip_range(clip1, 0, 15)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip2, 21, 30)
        clip3 = track.get_clip_at(2)
        self.assert_clip_range(clip3, 40, 65)
        clip2.adjust_clip_left(0)
        clip2.adjust_clip_right(35)
        self.assertEqual(track.get_clip_count(), 2)
        clip1 = track.get_clip_at(0)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip1, 0, 35)
        self.assert_clip_range(clip2, 40, 65)

    def test_adjust_clip_range_overlaps_on_the_right_side(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 3)
        clip1 = track.get_clip_at(0)
        self.assert_clip_range(clip1, 0, 15)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip2, 21, 30)
        clip3 = track.get_clip_at(2)
        self.assert_clip_range(clip3, 40, 65)
        clip2.adjust_clip_left(21)
        clip2.adjust_clip_right(45)
        self.assert_clip_range(clip1, 0, 15)
        self.assert_clip_range(clip2, 21, 45)
        self.assert_clip_range(clip3, 46, 65)

    def test_adjust_clip_range_overlaps_on_the_whole_clip_to_the_right(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 3)
        clip1 = track.get_clip_at(0)
        self.assert_clip_range(clip1, 0, 15)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip2, 21, 30)
        clip3 = track.get_clip_at(2)
        self.assert_clip_range(clip3, 40, 65)
        clip2.adjust_clip_left(21)
        clip2.adjust_clip_right(1000)
        self.assertEqual(track.get_clip_count(), 2)
        clip1 = track.get_clip_at(0)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip1, 0, 15)
        self.assert_clip_range(clip2, 21, 1000)

    def test_adjust_clip_range_overlaps_on_the_left_and_right_side(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 3)
        clip1 = track.get_clip_at(0)
        self.assert_clip_range(clip1, 0, 15)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip2, 21, 30)
        clip3 = track.get_clip_at(2)
        self.assert_clip_range(clip3, 40, 65)
        clip2.adjust_clip_left(10)
        clip2.adjust_clip_right(45)
        self.assert_clip_range(clip1, 0, 9)
        self.assert_clip_range(clip2, 10, 45)
        self.assert_clip_range(clip3, 46, 65)

    def test_adjust_clip_range_overlaps_two_whole_clips(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 3)
        clip1 = track.get_clip_at(0)
        self.assert_clip_range(clip1, 0, 15)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip2, 21, 30)
        clip3 = track.get_clip_at(2)
        self.assert_clip_range(clip3, 40, 65)
        clip2.adjust_clip_left(0)
        clip2.adjust_clip_right(1000)
        self.assertEqual(track.get_clip_count(), 1)
        clip1 = track.get_clip_at(0)
        self.assert_clip_range(clip1, 0, 1000)


class TestInsertClip(BaseTestCase):
    def test_insert_clip_no_overlapping(self):
        track = self.song.get_track_at(0)
        track.create_midi_clip(
            clip_start_tick=32,
            clip_end_tick=38,
        )
        self.assertEqual(track.get_clip_count(), 4)
        clip1 = track.get_clip_at(0)
        self.assert_clip_range(clip1, 0, 15)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip2, 21, 30)
        clip3 = track.get_clip_at(2)
        self.assert_clip_range(clip3, 32, 38)
        clip4 = track.get_clip_at(3)
        self.assert_clip_range(clip4, 40, 65)

    def test_insert_clip_overalaps_with_left_and_right(self):
        track = self.song.get_track_at(0)
        track.create_midi_clip(
            clip_start_tick=25,
            clip_end_tick=45,
        )
        self.assertEqual(track.get_clip_count(), 4)
        clip1 = track.get_clip_at(0)
        self.assert_clip_range(clip1, 0, 15)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip2, 21, 24)
        clip3 = track.get_clip_at(2)
        self.assert_clip_range(clip3, 25, 45)
        clip4 = track.get_clip_at(3)
        self.assert_clip_range(clip4, 46, 65)

    def test_insert_clip_overlaps_with_whole_clips(self):
        track = self.song.get_track_at(0)
        track.create_midi_clip(
            clip_start_tick=21,
            clip_end_tick=65,
        )
        self.assertEqual(track.get_clip_count(), 2)
        clip1 = track.get_clip_at(0)
        self.assert_clip_range(clip1, 0, 15)
        clip2 = track.get_clip_at(1)
        self.assert_clip_range(clip2, 21, 65)


class TestDeleteClip(BaseTestCase):
    # TODO: Add tests
    pass


if __name__ == '__main__':
    unittest.main()
