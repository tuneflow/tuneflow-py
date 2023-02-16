from tuneflow_py.models.song import Song
from miditoolkit.midi import MidiFile
from pathlib import PurePath, Path
from io import BytesIO
import unittest


class TestSong(unittest.TestCase):
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
        self.assertEqual(first_track.get_instrument().program, 65)
        self.assertEqual(first_track.get_instrument().is_drum, False)
        # Test drum track
        last_track = song.get_track_at(song.get_track_count()-1)
        self.assertEqual(last_track.get_instrument().program, 0)
        self.assertEqual(last_track.get_instrument().is_drum, True)
        # TODO: Test track automation
        first_clip = first_track.get_clip_at(0)
        self.assertEqual(first_clip.get_note_count(), 673)
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


if __name__ == '__main__':
    unittest.main()
