from tuneflow_py import Song, Clip, Track, TrackType, Note, ClipType
from miditoolkit.midi import MidiFile
from pathlib import PurePath, Path
from io import BytesIO
from typing import List
import unittest
import pytest


def create_song():
    song = Song()
    song.create_tempo_change(ticks=1440, bpm=60)
    track = song.create_track(type=TrackType.MIDI_TRACK)
    clip1 = track.create_midi_clip(clip_start_tick=0)
    clip1.create_note(pitch=68, velocity=80, start_tick=14, end_tick=20)
    clip1.create_note(pitch=66, velocity=80, start_tick=15, end_tick=20)
    clip1.create_note(pitch=64, velocity=80, start_tick=0, end_tick=10)
    clip1.adjust_clip_left(5)
    clip1.adjust_clip_right(15)
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

        self.song = create_song()


class TestBasicOperations(BaseTestCase):
    def test_get_data(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 1)
        clip1 = track.get_clip_at(0)
        self.assertIsNotNone(clip1)
        self.assertEqual(clip1.get_raw_note_count(), 3)
        self.assertEqual(len(list(clip1.get_notes())), 1)
        assert_notes_are_equal(
            list(clip1.get_raw_notes()),
            create_test_notes(
                [
                    {
                        "id": 3,
                        "pitch": 64,
                        "velocity": 80,
                        "start_tick": 0,
                        "end_tick": 10,
                    },
                    {
                        "id": 1,
                        "pitch": 68,
                        "velocity": 80,
                        "start_tick": 14,
                        "end_tick": 20,
                    },
                    {
                        "id": 2,
                        "pitch": 66,
                        "velocity": 80,
                        "start_tick": 15,
                        "end_tick": 20,
                    },
                ],
                clip1,
            ),
        )

        assert_notes_are_equal(
            list(clip1.get_notes()),
            create_test_notes(
                [
                    {
                        "id": 1,
                        "pitch": 68,
                        "velocity": 80,
                        "start_tick": 14,
                        "end_tick": 20,
                    },
                ],
                clip1,
            ),
        )

    def test_set_velocity(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 1)
        clip1 = track.get_clip_at(0)
        self.assertIsNotNone(clip1)
        self.assertEqual(clip1.get_raw_note_count(), 3)
        note1 = list(clip1.get_raw_notes())[0]
        note1.set_velocity(99)
        assert_notes_are_equal(
            [list(clip1.get_raw_notes())[0]],
            create_test_notes(
                [
                    {
                        "id": 3,
                        "pitch": 64,
                        "velocity": 99,
                        "start_tick": 0,
                        "end_tick": 10,
                    },
                ],
                clip1,
            ),
        )


class TestAdjustPitch(BaseTestCase):
    def test_reject_if_setting_invalid_pitches(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 1)
        clip1 = track.get_clip_at(0)
        self.assertIsNotNone(clip1)
        self.assertEqual(clip1.get_raw_note_count(), 3)

        note1 = list(clip1.get_raw_notes())[0]
        with pytest.raises(Exception) as e_info:
            note1.set_pitch(128)
        with pytest.raises(Exception) as e_info:
            note1.set_pitch(-1)

    def test_deletes_note_if_adjusting_the_note_to_invalid_pitch(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 1)
        clip1 = track.get_clip_at(0)
        self.assertIsNotNone(clip1)
        self.assertEqual(clip1.get_raw_note_count(), 3)

        note1 = list(clip1.get_raw_notes())[0]
        note1.adjust_pitch(999)
        self.assertEqual(clip1.get_raw_note_count(), 2)
        # Check if the note is deleted from the clip.
        assert_notes_are_equal(
            list(clip1.get_raw_notes()),
            create_test_notes(
                [
                    {
                        "id": 1,
                        "pitch": 68,
                        "velocity": 80,
                        "start_tick": 14,
                        "end_tick": 20,
                    },
                    {
                        "id": 2,
                        "pitch": 66,
                        "velocity": 80,
                        "start_tick": 15,
                        "end_tick": 20,
                    },
                ],
                clip1,
            ),
        )

    def test_adjusts_pitch_withint_valid_range(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 1)
        clip1 = track.get_clip_at(0)
        self.assertIsNotNone(clip1)
        self.assertEqual(clip1.get_raw_note_count(), 3)

        note1 = list(clip1.get_raw_notes())[0]
        note1.adjust_pitch(-9)
        self.assertEqual(clip1.get_raw_note_count(), 3)
        assert_notes_are_equal(
            list(clip1.get_raw_notes()),
            create_test_notes(
                [
                    {
                        "id": 3,
                        "pitch": 64 - 9,
                        "velocity": 80,
                        "start_tick": 0,
                        "end_tick": 10,
                    },
                    {
                        "id": 1,
                        "pitch": 68,
                        "velocity": 80,
                        "start_tick": 14,
                        "end_tick": 20,
                    },
                    {
                        "id": 2,
                        "pitch": 66,
                        "velocity": 80,
                        "start_tick": 15,
                        "end_tick": 20,
                    },
                ],
                clip1,
            ),
        )
        note1.adjust_pitch(10)
        self.assertEqual(clip1.get_raw_note_count(), 3)
        assert_notes_are_equal(
            list(clip1.get_raw_notes()),
            create_test_notes(
                [
                    {
                        "id": 3,
                        "pitch": 64 - 9 + 10,
                        "velocity": 80,
                        "start_tick": 0,
                        "end_tick": 10,
                    },
                    {
                        "id": 1,
                        "pitch": 68,
                        "velocity": 80,
                        "start_tick": 14,
                        "end_tick": 20,
                    },
                    {
                        "id": 2,
                        "pitch": 66,
                        "velocity": 80,
                        "start_tick": 15,
                        "end_tick": 20,
                    },
                ],
                clip1,
            ),
        )


class TestDeleteFromParent(BaseTestCase):
    def test_delete_note(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 1)
        clip1 = track.get_clip_at(0)
        self.assertIsNotNone(clip1)
        self.assertEqual(clip1.get_raw_note_count(), 3)
        self.assertEqual(len(list(clip1.get_notes())), 1)

        note2 = list(clip1.get_raw_notes())[1]
        note2.delete_from_parent()
        self.assertEqual(clip1.get_raw_note_count(), 2)
        assert_notes_are_equal(
            list(clip1.get_raw_notes()),
            create_test_notes(
                [
                    {
                        "id": 3,
                        "pitch": 64,
                        "velocity": 80,
                        "start_tick": 0,
                        "end_tick": 10,
                    },
                    {
                        "id": 2,
                        "pitch": 66,
                        "velocity": 80,
                        "start_tick": 15,
                        "end_tick": 20,
                    },
                ],
                clip1,
            ),
        )
        self.assertEqual(len(list(clip1.get_notes())), 0)


class TestMoveNote(BaseTestCase):
    def test_move_note_if_note_is_not_in_any_clip(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 1)
        clip1 = track.get_clip_at(0)
        self.assertIsNotNone(clip1)
        self.assertEqual(clip1.get_raw_note_count(), 3)

        note2 = list(clip1.get_raw_notes())[1]
        note2.delete_from_parent()

        self.assertIsNone(note2.get_clip())
        note2.move_note(100)
        self.assertEqual(note2.get_start_tick(), 114)
        self.assertEqual(note2.get_end_tick(), 120)

    def test_delete_note_if_moved_to_the_left_of_0(self):
        # TODO: Re-evaluate whether we should delete the notes
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 1)
        clip1 = track.get_clip_at(0)
        self.assertIsNotNone(clip1)
        self.assertEqual(clip1.get_raw_note_count(), 3)
        self.assertEqual(len(list(clip1.get_notes())), 1)

        note2 = list(clip1.get_raw_notes())[1]
        note2.move_note(-9999)

        self.assertLess(note2.get_end_tick(), 0)

        # Verify the the note is deleted.
        self.assertEqual(clip1.get_raw_note_count(), 2)
        self.assertEqual(len(list(clip1.get_notes())), 0)
        assert_notes_are_equal(
            list(clip1.get_raw_notes()),
            create_test_notes(
                [
                    {
                        "id": 3,
                        "pitch": 64,
                        "velocity": 80,
                        "start_tick": 0,
                        "end_tick": 10,
                    },
                    {
                        "id": 2,
                        "pitch": 66,
                        "velocity": 80,
                        "start_tick": 15,
                        "end_tick": 20,
                    },
                ],
                clip1,
            ),
        )

    def test_do_not_delete_note_if_moved_to_the_left_of_the_clip(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 1)
        clip1 = track.get_clip_at(0)
        self.assertIsNotNone(clip1)
        self.assertEqual(clip1.get_raw_note_count(), 3)
        self.assertEqual(len(list(clip1.get_notes())), 1)
        self.assertEqual(clip1.get_clip_start_tick(), 5)

        note2 = list(clip1.get_raw_notes())[1]
        note2.move_note(-16)

        # Verify the range of the note.
        self.assertEqual(note2.get_start_tick(), 0)
        self.assertEqual(note2.get_end_tick(), 4)

        # Verify the note is not deleted and is not included in the clip's range.
        self.assertEqual(clip1.get_raw_note_count(), 3)
        self.assertEqual(len(list(clip1.get_notes())), 0)
        assert_notes_are_equal(
            list(clip1.get_raw_notes()),
            create_test_notes(
                [
                    {
                        "id": 1,
                        "pitch": 68,
                        "velocity": 80,
                        "start_tick": 0,
                        "end_tick": 4,
                    },
                    {
                        "id": 3,
                        "pitch": 64,
                        "velocity": 80,
                        "start_tick": 0,
                        "end_tick": 10,
                    },
                    {
                        "id": 2,
                        "pitch": 66,
                        "velocity": 80,
                        "start_tick": 15,
                        "end_tick": 20,
                    },
                ],
                clip1,
            ),
        )

    def test_do_not_delete_note_if_moved_to_the_right_of_the_clip(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 1)
        clip1 = track.get_clip_at(0)
        self.assertIsNotNone(clip1)
        self.assertEqual(clip1.get_raw_note_count(), 3)
        self.assertEqual(len(list(clip1.get_notes())), 1)
        self.assertEqual(clip1.get_clip_start_tick(), 5)
        self.assertEqual(clip1.get_clip_end_tick(), 15)

        note2 = list(clip1.get_raw_notes())[1]
        self.assertEqual(note2.get_start_tick(), 14)
        note2.move_note(2)

        # Verify the range of the note.
        self.assertEqual(note2.get_start_tick(), 16)
        self.assertEqual(note2.get_end_tick(), 22)

        # Verify the the note is not deleted and that it is not
        # included in the clip's range.
        self.assertEqual(clip1.get_raw_note_count(), 3)
        self.assertEqual(len(list(clip1.get_notes())), 0)
        assert_notes_are_equal(
            list(clip1.get_raw_notes()),
            create_test_notes(
                [
                    {
                        "id": 3,
                        "pitch": 64,
                        "velocity": 80,
                        "start_tick": 0,
                        "end_tick": 10,
                    },
                    {
                        "id": 2,
                        "pitch": 66,
                        "velocity": 80,
                        "start_tick": 15,
                        "end_tick": 20,
                    },
                    {
                        "id": 1,
                        "pitch": 68,
                        "velocity": 80,
                        "start_tick": 16,
                        "end_tick": 22,
                    },
                ],
                clip1,
            ),
        )

    def test_move_not_and_change_the_order_of_notes(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 1)
        clip1 = track.get_clip_at(0)
        self.assertIsNotNone(clip1)
        self.assertEqual(clip1.get_raw_note_count(), 3)
        self.assertEqual(clip1.get_clip_start_tick(), 5)
        self.assertEqual(clip1.get_clip_end_tick(), 15)

        note3 = list(clip1.get_raw_notes())[2]
        self.assertEqual(note3.get_start_tick(), 15)
        self.assertEqual(note3.get_end_tick(), 20)
        note3.move_note(-2)

        # Verify the range of the note.
        self.assertEqual(note3.get_start_tick(), 13)
        self.assertEqual(note3.get_end_tick(), 18)

        # Verify the changed notes.
        self.assertEqual(clip1.get_raw_note_count(), 3)
        self.assertEqual(len(list(clip1.get_notes())), 2)
        assert_notes_are_equal(
            list(clip1.get_raw_notes()),
            create_test_notes(
                [
                    {
                        "id": 3,
                        "pitch": 64,
                        "velocity": 80,
                        "start_tick": 0,
                        "end_tick": 10,
                    },
                    {
                        "id": 2,
                        "pitch": 66,
                        "velocity": 80,
                        "start_tick": 13,
                        "end_tick": 18,
                    },
                    {
                        "id": 1,
                        "pitch": 68,
                        "velocity": 80,
                        "start_tick": 14,
                        "end_tick": 20,
                    },
                ],
                clip1,
            ),
        )
        assert_notes_are_equal(
            list(clip1.get_notes()),
            create_test_notes(
                [
                    {
                        "id": 2,
                        "pitch": 66,
                        "velocity": 80,
                        "start_tick": 13,
                        "end_tick": 18,
                    },
                    {
                        "id": 1,
                        "pitch": 68,
                        "velocity": 80,
                        "start_tick": 14,
                        "end_tick": 20,
                    },
                ],
                clip1,
            ),
        )

    def test_set_note_start_to_0_if_moved_cross_0(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 1)
        clip1 = track.get_clip_at(0)
        self.assertIsNotNone(clip1)
        self.assertEqual(clip1.get_raw_note_count(), 3)
        self.assertEqual(clip1.get_clip_start_tick(), 5)
        self.assertEqual(clip1.get_clip_end_tick(), 15)

        note3 = list(clip1.get_raw_notes())[2]
        self.assertEqual(note3.get_start_tick(), 15)
        self.assertEqual(note3.get_end_tick(), 20)
        note3.move_note(-20)

        # Verify the range of the note.
        self.assertEqual(note3.get_start_tick(), 0)
        self.assertEqual(note3.get_end_tick(), 0)

        # Verify the changed notes.
        self.assertEqual(clip1.get_raw_note_count(), 3)
        self.assertEqual(len(list(clip1.get_notes())), 1)
        assert_notes_are_equal(
            list(clip1.get_raw_notes()),
            create_test_notes(
                [
                    {
                        "id": 2,
                        "pitch": 66,
                        "velocity": 80,
                        "start_tick": 0,
                        "end_tick": 0,
                    },
                    {
                        "id": 3,
                        "pitch": 64,
                        "velocity": 80,
                        "start_tick": 0,
                        "end_tick": 10,
                    },
                    {
                        "id": 1,
                        "pitch": 68,
                        "velocity": 80,
                        "start_tick": 14,
                        "end_tick": 20,
                    },
                ],
                clip1,
            ),
        )
        assert_notes_are_equal(
            list(clip1.get_notes()),
            create_test_notes(
                [
                    {
                        "id": 1,
                        "pitch": 68,
                        "velocity": 80,
                        "start_tick": 14,
                        "end_tick": 20,
                    },
                ],
                clip1,
            ),
        )


class TestTrimNote(BaseTestCase):
    def test_trim_note_if_note_is_not_in_any_clip(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 1)
        clip1 = track.get_clip_at(0)
        self.assertIsNotNone(clip1)
        self.assertEqual(clip1.get_raw_note_count(), 3)

        note2 = list(clip1.get_raw_notes())[1]
        note2.delete_from_parent()

        self.assertIsNone(note2.get_clip())
        note2.adjust_left_to(10)
        note2.adjust_right_to(100)
        self.assertEqual(note2.get_start_tick(), 10)
        self.assertEqual(note2.get_end_tick(), 100)

    def test_delete_note_if_note_is_trimmed_to_be_invalid(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 1)
        clip1 = track.get_clip_at(0)
        self.assertIsNotNone(clip1)
        self.assertEqual(clip1.get_raw_note_count(), 3)

        note2 = list(clip1.get_raw_notes())[1]

        self.assertIsNotNone(note2.get_clip())
        note2.adjust_right_to(1)
        self.assertEqual(note2.get_start_tick(), 14)
        self.assertEqual(note2.get_end_tick(), 1)
        self.assertIsNone(note2.get_clip())
        # Verify clip notes.
        self.assertEqual(clip1.get_raw_note_count(), 2)
        assert_notes_are_equal(
            list(clip1.get_raw_notes()),
            create_test_notes(
                [
                    {
                        "id": 3,
                        "pitch": 64,
                        "velocity": 80,
                        "start_tick": 0,
                        "end_tick": 10,
                    },
                    {
                        "id": 2,
                        "pitch": 66,
                        "velocity": 80,
                        "start_tick": 15,
                        "end_tick": 20,
                    },
                ],
                clip1,
            ),
        )

    def test_adjust_left_and_reorder_notes(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 1)
        clip1 = track.get_clip_at(0)
        self.assertIsNotNone(clip1)
        self.assertEqual(clip1.get_raw_note_count(), 3)

        note2 = list(clip1.get_raw_notes())[1]

        self.assertIsNotNone(note2.get_clip())
        note2.adjust_left_to(16)
        self.assertEqual(note2.get_start_tick(), 16)
        self.assertEqual(note2.get_end_tick(), 20)
        self.assertIsNotNone(note2.get_clip())
        # Verify clip notes.
        self.assertEqual(clip1.get_raw_note_count(), 3)
        assert_notes_are_equal(
            list(clip1.get_raw_notes()),
            create_test_notes(
                [
                    {
                        "id": 3,
                        "pitch": 64,
                        "velocity": 80,
                        "start_tick": 0,
                        "end_tick": 10,
                    },
                    {
                        "id": 2,
                        "pitch": 66,
                        "velocity": 80,
                        "start_tick": 15,
                        "end_tick": 20,
                    },
                    {
                        "id": 1,
                        "pitch": 68,
                        "velocity": 80,
                        "start_tick": 16,
                        "end_tick": 20,
                    },
                ],
                clip1,
            ),
        )

    def test_adjust_right(self):
        track = self.song.get_track_at(0)
        self.assertEqual(track.get_clip_count(), 1)
        clip1 = track.get_clip_at(0)
        self.assertIsNotNone(clip1)
        self.assertEqual(clip1.get_raw_note_count(), 3)

        note2 = list(clip1.get_raw_notes())[1]

        self.assertIsNotNone(note2.get_clip())
        note2.adjust_right_to(16)
        self.assertEqual(note2.get_start_tick(), 14)
        self.assertEqual(note2.get_end_tick(), 16)
        self.assertIsNotNone(note2.get_clip())
        # Verify clip notes.
        self.assertEqual(clip1.get_raw_note_count(), 3)
        assert_notes_are_equal(
            list(clip1.get_raw_notes()),
            create_test_notes(
                [
                    {
                        "id": 3,
                        "pitch": 64,
                        "velocity": 80,
                        "start_tick": 0,
                        "end_tick": 10,
                    },
                    {
                        "id": 1,
                        "pitch": 68,
                        "velocity": 80,
                        "start_tick": 14,
                        "end_tick": 16,
                    },
                    {
                        "id": 2,
                        "pitch": 66,
                        "velocity": 80,
                        "start_tick": 15,
                        "end_tick": 20,
                    },
                ],
                clip1,
            ),
        )


if __name__ == '__main__':
    unittest.main()
