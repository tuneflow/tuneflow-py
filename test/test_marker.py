from tuneflow_py.models.song import Song
from tuneflow_py.models.marker import StructureType
import unittest


def create_song():
    song = Song()
    song.create_tempo_change(ticks=1440, bpm=60)
    return song


class TestStructure(unittest.TestCase):
    def test_get_structure_at_index(self):
        song = create_song()
        assert song.get_structure_at_index(0) is None

        song.create_structure(tick=0, type=StructureType.INTRO)
        song.create_structure(tick=480, type=StructureType.VERSE)

        assert song.get_structure_at_index(0).get_tick() == 0
        assert song.get_structure_at_index(0).get_type() == StructureType.INTRO

        assert song.get_structure_at_index(1).get_tick() == 480
        assert song.get_structure_at_index(1).get_type() == StructureType.VERSE

    def test_get_structure_at_tick(self):
        song = create_song()
        assert song.get_structure_at_tick(0) is None
        assert song.get_structure_at_tick(-1) is None

        song.create_structure(tick=0, type=StructureType.INTRO)
        song.create_structure(tick=480, type=StructureType.VERSE)

        assert song.get_structure_at_tick(-1).get_tick() == 0
        assert song.get_structure_at_tick(-1).get_type() == StructureType.INTRO

        assert song.get_structure_at_tick(0).get_tick() == 0
        assert song.get_structure_at_tick(0).get_type() == StructureType.INTRO

        assert song.get_structure_at_tick(240).get_tick() == 0
        assert song.get_structure_at_tick(240).get_type() == StructureType.INTRO

        assert song.get_structure_at_tick(480).get_tick() == 480
        assert song.get_structure_at_tick(480).get_type() == StructureType.VERSE

        assert song.get_structure_at_tick(960).get_tick() == 480
        assert song.get_structure_at_tick(960).get_type() == StructureType.VERSE

    def test_create_first_structure_from_non_zero_tick(self):
        song = create_song()
        song.create_structure(tick=480, type=StructureType.INTRO)
        assert song.get_structure_at_index(0).get_tick() == 0
        assert song.get_structure_at_index(0).get_type() == StructureType.INTRO

    def test_sort_created_structures_correctly(self):
        song = create_song()
        song.create_structure(tick=480, type=StructureType.INTRO)
        song.create_structure(tick=960, type=StructureType.VERSE)
        song.create_structure(tick=480, type=StructureType.OUTRO)
        assert song.get_structure_at_index(0).get_tick() == 0
        assert song.get_structure_at_index(0).get_type() == StructureType.INTRO
        assert song.get_structure_at_index(1).get_tick() == 480
        assert song.get_structure_at_index(1).get_type() == StructureType.OUTRO
        assert song.get_structure_at_index(2).get_tick() == 960
        assert song.get_structure_at_index(2).get_type() == StructureType.VERSE

    def test_move_structure_non_overlapping_correctly(self):
        song = create_song()
        song.create_structure(tick=0, type=StructureType.INTRO)
        song.create_structure(tick=480, type=StructureType.VERSE)
        song.create_structure(tick=960, type=StructureType.CHORUS)
        assert len(song.get_structures()) == 3
        song.move_structure(1, 240)
        assert len(song.get_structures()) == 3
        assert song.get_structures()[0].get_type() == StructureType.INTRO
        assert song.get_structures()[0].get_tick() == 0
        assert song.get_structures()[1].get_type() == StructureType.VERSE
        assert song.get_structures()[1].get_tick() == 240
        assert song.get_structures()[2].get_type() == StructureType.CHORUS
        assert song.get_structures()[2].get_tick() == 960

    def test_move_structure_past_another_correctly(self):
        song = create_song()
        song.create_structure(tick=0, type=StructureType.INTRO)
        song.create_structure(tick=480, type=StructureType.VERSE)
        song.create_structure(tick=960, type=StructureType.CHORUS)
        assert len(song.get_structures()) == 3
        song.move_structure(1, 1920)
        assert len(song.get_structures()) == 3
        assert song.get_structures()[0].get_type() == StructureType.INTRO
        assert song.get_structures()[0].get_tick() == 0
        assert song.get_structures()[1].get_type() == StructureType.CHORUS
        assert song.get_structures()[1].get_tick() == 960
        assert song.get_structures()[2].get_type() == StructureType.VERSE
        assert song.get_structures()[2].get_tick() == 1920

    def test_move_structure_overwrite_correctly(self):
        song = create_song()
        song.create_structure(tick=0, type=StructureType.INTRO)
        song.create_structure(tick=480, type=StructureType.VERSE)
        song.create_structure(tick=960, type=StructureType.CHORUS)
        assert len(song.get_structures()) == 3
        song.move_structure(1, 960)
        assert len(song.get_structures()) == 2
        assert song.get_structures()[0].get_type() == StructureType.INTRO
        assert song.get_structures()[0].get_tick() == 0
        assert song.get_structures()[1].get_type() == StructureType.VERSE
        assert song.get_structures()[1].get_tick() == 960

    def test_move_structure_overwrite_first_correctly(self):
        song = create_song()
        song.create_structure(tick=0, type=StructureType.INTRO)
        song.create_structure(tick=480, type=StructureType.VERSE)
        song.create_structure(tick=960, type=StructureType.CHORUS)
        assert len(song.get_structures()) == 3
        song.move_structure(1, 0)
        assert len(song.get_structures()) == 2
        assert song.get_structures()[0].get_type() == StructureType.VERSE
        assert song.get_structures()[0].get_tick() == 0
        assert song.get_structures()[1].get_type() == StructureType.CHORUS
        assert song.get_structures()[1].get_tick() == 960

    def test_remove_structure_correctly(self):
        song = create_song()
        song.create_structure(tick=0, type=StructureType.INTRO)
        song.create_structure(tick=480, type=StructureType.VERSE)
        song.create_structure(tick=960, type=StructureType.CHORUS)
        assert len(song.get_structures()) == 3
        song.remove_structure(1)
        assert song.get_tempo_event_count() == 2
        assert song.get_structures()[0].get_type() == StructureType.INTRO
        assert song.get_structures()[0].get_tick() == 0
        assert song.get_structures()[1].get_type() == StructureType.CHORUS
        assert song.get_structures()[1].get_tick() == 960
        song.remove_structure(3)
        song.remove_structure(-1)
        assert song.get_tempo_event_count() == 2

    def test_create_custom_marker(self):
        song = create_song()
        song.create_structure(tick=0, type=StructureType.INTRO)
        song.create_structure(tick=480, type=StructureType.CUSTOM, custom_name='myStructure')
        song.create_structure(tick=960, type=StructureType.OUTRO, custom_name='myStructure')
        self.assertEqual(song.get_structure_at_index(0).get_type(), StructureType.INTRO)
        self.assertEqual(song.get_structure_at_index(1).get_type(), StructureType.CUSTOM)
        self.assertEqual(song.get_structure_at_index(1).get_custom_name(), 'myStructure')
        self.assertEqual(song.get_structure_at_index(2).get_custom_name(), '')

    def test_update_custom_marker(self):
        song = create_song()
        song.create_structure(tick=0, type=StructureType.INTRO)
        song.create_structure(tick=480, type=StructureType.CUSTOM, custom_name='myStructure')
        song.create_structure(tick=960, type=StructureType.OUTRO, custom_name='myStructure')
        self.assertEqual(song.get_structure_at_index(1).get_type(), StructureType.CUSTOM)
        self.assertEqual(song.get_structure_at_index(1).get_custom_name(), 'myStructure')

        song.get_structure_at_index(1).set_custom_name('myNewStructureName')
        self.assertEqual(song.get_structure_at_index(1).get_custom_name(), 'myNewStructureName')


if __name__ == '__main__':
    unittest.main()
