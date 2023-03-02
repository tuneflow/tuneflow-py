from tuneflow_py import Song, TrackType
from miditoolkit.midi import MidiFile
from pathlib import PurePath, Path
import unittest
import pytest


def create_song():
    song = Song()
    song.create_tempo_change(
        ticks=1440,
        bpm=60,
    )
    song.create_time_signature(ticks=0, numerator=4, denominator=4)
    song.create_time_signature(ticks=2880, numerator=7, denominator=8)
    return song


class BaseTest(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

        self.song = create_song()


class TestImportExportMIDI(unittest.TestCase):
    def test_import_midi(self):
        midi_obj = MidiFile(filename=PurePath(
            Path(__file__).parent, Path('caravan.test.golden.mid')))
        song = Song.from_midi(midi_obj=midi_obj)
        # Test tempos
        self.assertEqual(song.get_tempo_event_count(), 8)
        self.assertAlmostEqual(song.get_duration(), 595.0945734687816)
        # Test time signatures
        self.assertEqual(song.get_time_signature_event_count(), 3)
        self.assertEqual(
            song.get_time_signature_event_at(1).get_numerator(), 4)
        self.assertEqual(song.get_time_signature_event_at(
            1).get_denominator(), 2)
        # Test tracks
        first_track = song.get_track_at(0)
        self.assertEqual(first_track.get_clip_count(), 1)
        # Test non-piano track
        # Test track volume, pan
        self.assertAlmostEqual(
            first_track.get_volume_in_db(), -0.6665511534374842)
        self.assertAlmostEqual(song.get_track_at(7).get_pan(), 63)
        # Test track instrument
        self.assertEqual(first_track.get_instrument().program, 65)  # type:ignore
        self.assertEqual(first_track.get_instrument().is_drum, False)  # type:ignore
        # Test drum track
        last_track = song.get_track_at(song.get_track_count()-1)
        self.assertEqual(last_track.get_instrument().program, 0)  # type:ignore
        self.assertEqual(last_track.get_instrument().is_drum, True)  # type:ignore
        # TODO: Test track automation
        first_clip = first_track.get_clip_at(0)
        self.assertEqual(first_clip.get_raw_note_count(), 673)
        self.assertEqual(first_clip.get_clip_start_tick(), 107520)
        self.assertEqual(first_clip.get_clip_end_tick(), 1326719)
        first_note = first_clip.get_raw_note_at(0)
        self.assertEqual(first_note.get_pitch(), 52)
        self.assertEqual(first_note.get_start_tick(), 107520)
        self.assertEqual(first_note.get_end_tick(), 108159)
        self.assertEqual(first_note.get_velocity(), 115)
        self.assertEqual(first_note.get_start_time(), 47.659584045410156)
        self.assertAlmostEqual(first_note.get_end_time(), 47.94282913208008)
        self.assertEqual(song.last_tick, 1327199)
        self.assertAlmostEqual(song.duration, 595.0945734687816)

    def test_export_midi(self):
        golden_midi_path = PurePath(
            Path(__file__).parent, Path('caravan.test.golden.mid'))
        export_midi_path = PurePath(
            Path(__file__).parent, Path('caravan.test.test.mid'))
        midi_obj = MidiFile(filename=golden_midi_path)
        song = Song.from_midi(midi_obj=midi_obj)
        export_file = open(export_midi_path, 'wb')
        exported_midi = song.to_midi()
        exported_midi.dump(file=export_file)
        export_file.close()

        self.assertEqual(len(midi_obj.tempo_changes),
                         len(exported_midi.tempo_changes))
        for i in range(len(midi_obj.tempo_changes)):
            expected_tempo = midi_obj.tempo_changes[i]
            actual_tempo = exported_midi.tempo_changes[i]
            self.assertEqual(expected_tempo.time, actual_tempo.time)
            self.assertAlmostEqual(expected_tempo.tempo,
                                   actual_tempo.tempo, places=4)
        self.assertEqual(len(midi_obj.time_signature_changes),
                         len(exported_midi.time_signature_changes))
        for i in range(len(midi_obj.time_signature_changes)):
            expected_time_signature = midi_obj.time_signature_changes[i]
            actual_time_signature = exported_midi.time_signature_changes[i]
            self.assertEqual(expected_time_signature.time,
                             actual_time_signature.time)
            self.assertEqual(expected_time_signature.numerator,
                             actual_time_signature.numerator)
            self.assertEqual(expected_time_signature.denominator,
                             actual_time_signature.denominator)

        self.assertEqual(len(midi_obj.instruments),
                         len(exported_midi.instruments))
        for i in range(len(midi_obj.instruments)):
            expected_track = midi_obj.instruments[i]
            actual_track = exported_midi.instruments[i]
            self.assertEqual(expected_track.program, actual_track.program)
            self.assertEqual(expected_track.is_drum, actual_track.is_drum)
            self.assertEqual(len(expected_track.notes),
                             len(actual_track.notes))
            for j in range(len(expected_track.notes)):
                expected_note = expected_track.notes[j]
                actual_note = actual_track.notes[j]
                self.assertEqual(expected_note.start, actual_note.start)
                self.assertEqual(expected_note.end, actual_note.end)
                self.assertEqual(expected_note.velocity, actual_note.velocity)
                self.assertEqual(expected_note.pitch, actual_note.pitch)
            # TODO: Test track automation.


class TestBasicOperations(BaseTest):
    def test_get_track_index(self):
        track = self.song.create_track(type=TrackType.MIDI_TRACK)
        track2 = self.song.create_track(type=TrackType.MIDI_TRACK)
        self.assertEqual(self.song.get_track_index(track.get_id()), 0)
        self.assertEqual(self.song.get_track_index(track2.get_id()), 1)


class TestTempo(BaseTest):
    def test_get_tempo_at(self):
        song = self.song
        self.assertEqual(song.get_tempo_event_at(0).get_ticks(), 0)  # type:ignore
        self.assertEqual(song.get_tempo_event_at(0).get_bpm(), 120)  # type:ignore
        self.assertEqual(song.get_tempo_event_at(1).get_ticks(), 1440)  # type:ignore
        self.assertEqual(song.get_tempo_event_at(1).get_bpm(), 60)  # type:ignore
        self.assertIsNone(song.get_tempo_event_at(-1))
        self.assertIsNone(song.get_tempo_event_at(2))

    def test_get_tempo_at_tick(self):
        song = self.song
        self.assertEqual(song.get_tempo_event_at_tick(-10).get_ticks(), 0)
        self.assertEqual(song.get_tempo_event_at_tick(-10).get_bpm(), 120)
        self.assertEqual(song.get_tempo_event_at_tick(0).get_ticks(), 0)
        self.assertEqual(song.get_tempo_event_at_tick(0).get_bpm(), 120)
        self.assertEqual(song.get_tempo_event_at_tick(10).get_ticks(), 0)
        self.assertEqual(song.get_tempo_event_at_tick(10).get_bpm(), 120)
        self.assertEqual(song.get_tempo_event_at_tick(1439).get_ticks(), 0)
        self.assertEqual(song.get_tempo_event_at_tick(1439).get_bpm(), 120)
        self.assertEqual(song.get_tempo_event_at_tick(1440).get_ticks(), 1440)
        self.assertEqual(song.get_tempo_event_at_tick(1440).get_bpm(), 60)
        self.assertEqual(song.get_tempo_event_at_tick(1441).get_ticks(), 1440)
        self.assertEqual(song.get_tempo_event_at_tick(1441).get_bpm(), 60)
        self.assertEqual(song.get_tempo_event_at_tick(9999).get_ticks(), 1440)
        self.assertEqual(song.get_tempo_event_at_tick(9999).get_bpm(), 60)

    def test_move_tempo_non_overlapping(self):
        song = self.song
        song.create_tempo_change(
            ticks=2880,
            bpm=240,
        )
        self.assertEqual(song.get_tempo_event_count(), 3)
        with pytest.raises(Exception) as exception:
            song.move_tempo(1, 0)
        self.assertIsNotNone(exception)
        song.move_tempo(1, 480)
        self.assertEqual(song.get_tempo_event_count(), 3)
        self.assertEqual(song.get_tempo_event_at(0).get_bpm(), 120)  # type:ignore
        self.assertEqual(song.get_tempo_event_at(0).get_time(), 0)  # type:ignore
        self.assertEqual(song.get_tempo_event_at(1).get_bpm(), 60)  # type:ignore
        self.assertAlmostEqual(song.get_tempo_event_at(1).get_time(), 0.5)  # type:ignore
        self.assertEqual(song.get_tempo_event_at(2).get_bpm(), 240)  # type:ignore
        self.assertAlmostEqual(song.get_tempo_event_at(2).get_time(), 5.5)  # type:ignore

    def test_move_tempo_past_another(self):
        song = self.song
        song.create_tempo_change(
            ticks=2880,
            bpm=240,
        )
        self.assertEqual(song.get_tempo_event_count(), 3)
        song.move_tempo(1, 3360)
        self.assertEqual(song.get_tempo_event_count(), 3)
        self.assertEqual(song.get_tempo_event_at(0).get_bpm(), 120)  # type:ignore
        self.assertEqual(song.get_tempo_event_at(0).get_time(), 0)  # type:ignore
        self.assertEqual(song.get_tempo_event_at(1).get_bpm(), 240)  # type:ignore
        self.assertAlmostEqual(song.get_tempo_event_at(1).get_time(), 3)  # type:ignore
        self.assertEqual(song.get_tempo_event_at(2).get_bpm(), 60)  # type:ignore
        self.assertAlmostEqual(song.get_tempo_event_at(2).get_time(), 3.25)  # type:ignore

    def test_move_tempo_overwrite(self):
        song = self.song
        song.create_tempo_change(
            ticks=2880,
            bpm=240,
        )
        self.assertEqual(song.get_tempo_event_count(), 3)
        with pytest.raises(Exception) as exception:
            song.move_tempo(1, 0)
        self.assertIsNotNone(exception)
        song.move_tempo(2, 1440)
        self.assertEqual(song.get_tempo_event_count(), 2)
        self.assertEqual(song.get_tempo_event_at(0).get_bpm(), 120)  # type:ignore
        self.assertEqual(song.get_tempo_event_at(1).get_bpm(), 240)  # type:ignore

    def test_remove_tempo(self):
        song = self.song
        with pytest.raises(Exception) as exception:
            song.remove_tempo_change_at(0)
        self.assertIsNotNone(exception)
        song.remove_tempo_change_at(1)
        self.assertEqual(song.get_tempo_event_count(), 1)
        self.assertEqual(song.get_tempo_event_at(0).get_bpm(), 120)  # type:ignore
        with pytest.raises(Exception) as exception2:
            song.remove_tempo_change_at(0)
        self.assertIsNotNone(exception2)


if __name__ == '__main__':
    unittest.main()
