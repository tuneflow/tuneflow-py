import unittest
from unittest.mock import ANY
from tuneflow_py import Song, TrackType, AutomationTarget, AutomationTargetType, AutomationValue, AutomationData, AutomationPoint


def create_song():
    song = Song()
    midi_track = song.create_track(type=TrackType.MIDI_TRACK)
    return song, midi_track


class AnyInt(int):
    def __eq__(self, __value: object) -> bool:
        return True


class CloseFloat(float):
    def __eq__(self, __value: object) -> bool:
        return abs(self - __value) < 0.00001


def points_to_objects(points):
    return [{
        "id": point.id,
        "value": point.value,
        "tick": point.tick
    } for point in points]


class AutomationTargetTestCase(unittest.TestCase):
    def test_gets_and_sets_properties(self):
        target = AutomationTarget(type=AutomationTargetType.VOLUME)
        self.assertEqual(target.get_type(), AutomationTargetType.VOLUME)
        self.assertEqual(target.get_type(), AutomationTargetType.VOLUME)
        target = AutomationTarget(
            type=AutomationTargetType.AUDIO_PLUGIN,
            plugin_instance_id='someplugininstanceid',
            param_id='someparamid',
        )
        self.assertEqual(target.get_type(), AutomationTargetType.AUDIO_PLUGIN)
        self.assertEqual(target.get_plugin_instance_id(), 'someplugininstanceid')
        self.assertEqual(target.get_param_id(), 'someparamid')
        target.set_plugin_instance_id('anotherplugininstanceid')
        self.assertEqual(target.get_plugin_instance_id(), 'anotherplugininstanceid')
        target.set_param_id('anotherparamid')
        self.assertEqual(target.get_param_id(), 'anotherparamid')
        target.set_type(AutomationTargetType.PAN)
        self.assertEqual(target.get_type(), AutomationTargetType.PAN)

    def test_encodes_target(self):
        target1 = AutomationTarget(type=AutomationTargetType.VOLUME)
        self.assertEqual(target1.to_tf_automation_target_id(), '1')
        target2 = AutomationTarget(
            type=AutomationTargetType.AUDIO_PLUGIN,
            plugin_instance_id='pluginId1',
            param_id='paramId1',
        )
        self.assertEqual(target2.to_tf_automation_target_id(), '3^^pluginId1^^paramId1')

    def test_checks_equality(self):
        target1 = AutomationTarget(type=AutomationTargetType.PAN)
        target2 = AutomationTarget(type=AutomationTargetType.PAN)
        target3 = AutomationTarget(type=AutomationTargetType.VOLUME)
        target4 = AutomationTarget(
            AutomationTargetType.AUDIO_PLUGIN,
            'pluginId1',
            'paramId1',
        )
        target5 = AutomationTarget(
            AutomationTargetType.AUDIO_PLUGIN,
            'pluginId2',
            'paramId2',
        )
        target6 = AutomationTarget(
            AutomationTargetType.AUDIO_PLUGIN,
            'pluginId2',
            'paramId2',
        )
        self.assertEqual(target1.equals(target2), True)
        self.assertEqual(target1.equals(target3), False)
        self.assertEqual(target1.equals(target4), False)
        self.assertEqual(target4.equals(target5), False)
        self.assertEqual(target5.equals(target6), True)

    def test_clones_target(self):
        target1 = AutomationTarget(type=AutomationTargetType.VOLUME)
        target2 = target1.clone()
        self.assertEqual(target1 == target2, False)
        self.assertEqual(target1.equals(target2), True)


class AutomationValueTestCase(unittest.TestCase):
    def test_sets_and_gets_disabled(self):
        automation_value = AutomationValue()
        self.assertEqual(automation_value.get_disabled(), False)
        automation_value.set_disabled(True)
        self.assertEqual(automation_value.get_disabled(), True)

    def test_adds_and_gets_points(self):
        automation_value = AutomationValue()
        self.assertEqual([{
            "id": point.id,
            "tick": point.tick,
            "value": point.value
        } for point in automation_value.get_points()], [])
        automation_value.add_point(tick=3, value=0.5)
        automation_value.add_point(tick=1, value=0.25)
        automation_value.add_point(tick=2, value=0.75)
        self.assertEqual(points_to_objects(automation_value.get_points()), [
            {
                "id": 2,
                "tick": 1,
                "value": CloseFloat(0.25),
            },
            {
                "id": 3,
                "tick": 2,
                "value": CloseFloat(0.75),
            },
            {
                "id": 1,
                "tick": 3,
                "value": CloseFloat(0.5),
            },
        ])
        automation_value.add_point(tick=2, value=1)
        self.assertEqual(points_to_objects(automation_value.get_points()), [
            {
                "id": 2,
                "tick": 1,
                "value": CloseFloat(0.25),
            },
            {
                "id": 4,
                "tick": 2,
                "value": CloseFloat(1),
            },
            {
                "id": 3,
                "tick": 2,
                "value": CloseFloat(0.75),
            },
            {
                "id": 1,
                "tick": 3,
                "value": CloseFloat(0.5),
            },
        ])
        automation_value.add_point(tick=2, value=0.1, overwrite=True)
        self.assertEqual(points_to_objects(automation_value.get_points()), [
            {
                "id": 2,
                "tick": 1,
                "value": CloseFloat(0.25),
            },
            {
                "id": 5,
                "tick": 2,
                "value": CloseFloat(0.1),
            },
            {
                "id": 1,
                "tick": 3,
                "value": CloseFloat(0.5),
            },
        ])

    def test_get_points_within_range(self):
        automation_value = AutomationValue()
        self.assertEqual([{
            "id": point.id,
            "tick": point.tick,
            "value": point.value
        } for point in automation_value.get_points()], [])
        automation_value.add_point(tick=3, value=0.5)
        automation_value.add_point(tick=3, value=0.65)
        automation_value.add_point(tick=1, value=0.25)
        automation_value.add_point(tick=2, value=0.75)
        automation_value.add_point(tick=2, value=0.55)
        automation_value.add_point(tick=4, value=0.15)
        self.assertEqual(points_to_objects(automation_value.get_points_in_range(2, 3)), [
            {
                "id": 5,
                "tick": 2,
                "value": CloseFloat(0.55),
            },
            {
                "id": 4,
                "tick": 2,
                "value": CloseFloat(0.75),
            },
            {
                "id": 2,
                "tick": 3,
                "value": CloseFloat(0.65),
            },
            {
                "id": 1,
                "tick": 3,
                "value": CloseFloat(0.5),
            },
        ])

        self.assertEqual(points_to_objects(automation_value.get_points_in_range(4, 3)), [])

        self.assertEqual(points_to_objects(automation_value.get_points_in_range(5, 6)), [])

        self.assertEqual(points_to_objects(automation_value.get_points_in_range(4, 5)), [
            {
                "id": 6,
                "tick": 4,
                "value": CloseFloat(0.15),
            },
        ])
        self.assertEqual(points_to_objects(automation_value.get_points_in_range(0, 1)), [
            {
                "id": 3,
                "tick": 1,
                "value": CloseFloat(0.25),
            },
        ])

    def test_removes_points(self):
        automation_value = AutomationValue()
        self.assertEqual(points_to_objects(automation_value.get_points()), [])
        automation_value.add_point(tick=3, value=0.5)
        automation_value.add_point(tick=1, value=0.25)
        automation_value.add_point(tick=2, value=0.75)
        automation_value.add_point(tick=4, value=0.15)
        self.assertEqual(points_to_objects(automation_value.get_points()), [
            {
                "id": 2,
                "tick": 1,
                "value": CloseFloat(0.25),
            },
            {
                "id": 3,
                "tick": 2,
                "value": CloseFloat(0.75),
            },
            {
                "id": 1,
                "tick": 3,
                "value": CloseFloat(0.5),
            },
            {
                "id": 4,
                "tick": 4,
                "value": CloseFloat(0.15),
            },
        ])
        points = automation_value.get_points()
        point2Id = points[2].id
        automation_value.remove_points([points[0].id, points[1].id, points[3].id])
        self.assertEqual(points_to_objects(automation_value.get_points()), [
            {
                "id": point2Id,
                "tick": 3,
                "value": CloseFloat(0.5),
            },
        ])

    def test_remove_points_in_range(self):
        automation_value = AutomationValue()
        self.assertEqual(points_to_objects(automation_value.get_points()), [])
        automation_value.add_point(tick=3, value=0.5)
        automation_value.add_point(tick=3, value=0.65)
        automation_value.add_point(tick=1, value=0.25)
        automation_value.add_point(tick=2, value=0.75)
        automation_value.add_point(tick=2, value=0.55)
        automation_value.add_point(tick=4, value=0.15)
        self.assertEqual(points_to_objects(automation_value.get_points()), [
            {
                "id": 3,
                "tick": 1,
                "value": CloseFloat(0.25),
            },
            {
                "id": 5,
                "tick": 2,
                "value": CloseFloat(0.55),
            },
            {
                "id": 4,
                "tick": 2,
                "value": CloseFloat(0.75),
            },
            {
                "id": 2,
                "tick": 3,
                "value": CloseFloat(0.65),
            },
            {
                "id": 1,
                "tick": 3,
                "value": CloseFloat(0.5),
            },
            {
                "id": 6,
                "tick": 4,
                "value": CloseFloat(0.15),
            },
        ])
        automation_value.remove_points_in_range(2, 3)
        self.assertEqual(points_to_objects(automation_value.get_points()), [
            {
                "id": 3,
                "tick": 1,
                "value": CloseFloat(0.25),
            },
            {
                "id": 6,
                "tick": 4,
                "value": CloseFloat(0.15),
            },
        ])

    def test_moves_multiple_points_to_left_overwrite(self):
        automation_value = AutomationValue()
        self.assertEqual(points_to_objects(automation_value.get_points()), [])
        automation_value.add_point(tick=3, value=0.5)
        automation_value.add_point(tick=1, value=0.25)
        automation_value.add_point(tick=1, value=0.65)
        automation_value.add_point(tick=1, value=0.95)
        automation_value.add_point(tick=2, value=0.75)
        automation_value.add_point(tick=2, value=0.85)
        automation_value.add_point(tick=2, value=0.35)
        automation_value.add_point(tick=4, value=0.15)
        self.assertEqual(points_to_objects(automation_value.get_points()), [
            {
                "id": 4,
                "tick": 1,
                "value": CloseFloat(0.95),
            },
            {
                "id": 3,
                "tick": 1,
                "value": CloseFloat(0.65),
            },
            {
                "id": 2,
                "tick": 1,
                "value": CloseFloat(0.25),
            },
            {
                "id": 7,
                "tick": 2,
                "value": CloseFloat(0.35),
            },
            {
                "id": 6,
                "tick": 2,
                "value": CloseFloat(0.85),
            },
            {
                "id": 5,
                "tick": 2,
                "value": CloseFloat(0.75),
            },
            {
                "id": 1,
                "tick": 3,
                "value": CloseFloat(0.5),
            },
            {
                "id": 8,
                "tick": 4,
                "value": CloseFloat(0.15),
            },
        ])
        points = automation_value.get_points()
        automation_value.move_points([points[1].id, points[2].id, points[3].id, points[4].id], -1, 0.3)
        self.assertEqual(points_to_objects(automation_value.get_points()), [
            {
                "id": 3,
                "tick": 0,
                "value": CloseFloat(0.95),
            },
            {
                "id": 2,
                "tick": 0,
                "value": CloseFloat(0.55),
            },
            {
                "id": 7,
                "tick": 1,
                "value": CloseFloat(0.65),
            },
            {
                "id": 6,
                "tick": 1,
                "value": 1,
            },
            {
                "id": 5,
                "tick": 2,
                "value": CloseFloat(0.75),
            },
            {
                "id": 1,
                "tick": 3,
                "value": CloseFloat(0.5),
            },
            {
                "id": 8,
                "tick": 4,
                "value": CloseFloat(0.15),
            },
        ])

    def test_moves_multiple_points_to_right_overwrite(self):
        automation_value = AutomationValue()
        self.assertEqual(points_to_objects(automation_value.get_points()), [])
        automation_value.add_point(tick=3, value=0.5)
        automation_value.add_point(tick=1, value=0.25)
        automation_value.add_point(tick=1, value=0.65)
        automation_value.add_point(tick=1, value=0.95)
        automation_value.add_point(tick=2, value=0.75)
        automation_value.add_point(tick=2, value=0.85)
        automation_value.add_point(tick=2, value=0.35)
        automation_value.add_point(tick=4, value=0.15)
        self.assertEqual(points_to_objects(automation_value.get_points()), [
            {
                "id": 4,
                "tick": 1,
                "value": CloseFloat(0.95),
            },
            {
                "id": 3,
                "tick": 1,
                "value": CloseFloat(0.65),
            },
            {
                "id": 2,
                "tick": 1,
                "value": CloseFloat(0.25),
            },
            {
                "id": 7,
                "tick": 2,
                "value": CloseFloat(0.35),
            },
            {
                "id": 6,
                "tick": 2,
                "value": CloseFloat(0.85),
            },
            {
                "id": 5,
                "tick": 2,
                "value": CloseFloat(0.75),
            },
            {
                "id": 1,
                "tick": 3,
                "value": CloseFloat(0.5),
            },
            {
                "id": 8,
                "tick": 4,
                "value": CloseFloat(0.15),
            },
        ])
        points = automation_value.get_points()
        automation_value.move_points([points[1].id, points[2].id, points[3].id, points[4].id], 2, -0.3)
        self.assertEqual(points_to_objects(automation_value.get_points()), [
            {
                "id": 4,
                "tick": 1,
                "value": CloseFloat(0.95),
            },
            {
                "id": 3,
                "tick": 3,
                "value": CloseFloat(0.35),
            },
            {
                "id": 2,
                "tick": 3,
                "value": 0,
            },
            {
                "id": 7,
                "tick": 4,
                "value": CloseFloat(0.05),
            },
            {
                "id": 6,
                "tick": 4,
                "value": CloseFloat(0.55),
            },
            {
                "id": 8,
                "tick": 4,
                "value": CloseFloat(0.15),
            },
        ])

    def test_moves_single_point_no_overwrite(self):
        automation_value = AutomationValue()
        self.assertEqual(points_to_objects(automation_value.get_points()), [])
        automation_value.add_point(tick=3, value=0.5)
        automation_value.add_point(tick=1, value=0.25)
        automation_value.add_point(tick=2, value=0.75)
        automation_value.add_point(tick=4, value=0.15)
        self.assertEqual(points_to_objects(automation_value.get_points()), [
            {
                "id": 2,
                "tick": 1,
                "value": CloseFloat(0.25),
            },
            {
                "id": 3,
                "tick": 2,
                "value": CloseFloat(0.75),
            },
            {
                "id": 1,
                "tick": 3,
                "value": CloseFloat(0.5),
            },
            {
                "id": 4,
                "tick": 4,
                "value": CloseFloat(0.15),
            },
        ])
        points = automation_value.get_points()
        automation_value.move_points([points[2].id], -2, 0.3,  overwrite_values_in_drag_area=False)
        self.assertEqual(points_to_objects(automation_value.get_points()), [
            {
                "id": 2,
                "tick": 1,
                "value": CloseFloat(0.25),
            },
            {
                "id": 1,
                "tick": 1,
                "value": CloseFloat(0.8),
            },
            {
                "id": 3,
                "tick": 2,
                "value": CloseFloat(0.75),
            },

            {
                "id": 4,
                "tick": 4,
                "value": CloseFloat(0.15),
            },
        ])

    def test_moves_single_point_overwrite(self):
        automation_value = AutomationValue()
        self.assertEqual(points_to_objects(automation_value.get_points()), [])
        automation_value.add_point(tick=3, value=0.5)
        automation_value.add_point(tick=1, value=0.25)
        automation_value.add_point(tick=1, value=0.65)
        automation_value.add_point(tick=1, value=0.85)
        automation_value.add_point(tick=2, value=0.75)
        automation_value.add_point(tick=4, value=0.15)
        self.assertEqual(points_to_objects(automation_value.get_points()), [
            {
                "id": 4,
                "tick": 1,
                "value": CloseFloat(0.85),
            },
            {
                "id": 3,
                "tick": 1,
                "value": CloseFloat(0.65),
            },
            {
                "id": 2,
                "tick": 1,
                "value": CloseFloat(0.25),
            },
            {
                "id": 5,
                "tick": 2,
                "value": CloseFloat(0.75),
            },
            {
                "id": 1,
                "tick": 3,
                "value": CloseFloat(0.5),
            },
            {
                "id": 6,
                "tick": 4,
                "value": CloseFloat(0.15),
            },
        ])
        points = automation_value.get_points()
        automation_value.move_points([points[1].id], 3, -0.3)
        self.assertEqual(points_to_objects(automation_value.get_points()), [
            {
                "id": 4,
                "tick": 1,
                "value": CloseFloat(0.85),
            },
            {
                "id": 3,
                "tick": 4,
                "value": CloseFloat(0.35),
            },
            {
                "id": 6,
                "tick": 4,
                "value": CloseFloat(0.15),
            },
        ])

    def test_moves_points_in_range_no_overwrite(self):
        automation_value = AutomationValue()
        self.assertEqual(points_to_objects(automation_value.get_points()), [])
        automation_value.add_point(tick=3, value=0.5)
        automation_value.add_point(tick=1, value=0.25)
        automation_value.add_point(tick=2, value=0.75)
        automation_value.add_point(tick=4, value=0.15)
        self.assertEqual(points_to_objects(automation_value.get_points()), [
            {
                "id": 2,
                "tick": 1,
                "value": CloseFloat(0.25),
            },
            {
                "id": 3,
                "tick": 2,
                "value": CloseFloat(0.75),
            },
            {
                "id": 1,
                "tick": 3,
                "value": CloseFloat(0.5),
            },
            {
                "id": 4,
                "tick": 4,
                "value": CloseFloat(0.15),
            },
        ])
        automation_value.move_points_in_range(2, 3, 4, 0, overwrite_values_in_drag_area=False)
        self.assertEqual(points_to_objects(automation_value.get_points()), [
            {
                "id": 2,
                "tick": 1,
                "value": CloseFloat(0.25),
            },
            {
                "id": 4,
                "tick": 4,
                "value": CloseFloat(0.15),
            },
            {
                "id": 3,
                "tick": 6,
                "value": CloseFloat(0.75),
            },
            {
                "id": 1,
                "tick": 7,
                "value": CloseFloat(0.5),
            },
        ])


class AutomationDataTestCase(unittest.TestCase):
    def test_adds_automation(self):
        song, track = create_song()
        target = AutomationTarget(
            AutomationTargetType.AUDIO_PLUGIN,
            'pluginId1',
            'paramId1',
        )
        self.assertEqual(list(track.get_automation().get_automation_targets()), [])
        self.assertIsNone(
            track.get_automation().get_automation_value_by_id(target.to_tf_automation_target_id()),
        )

        track.get_automation().add_automation(target)
        self.assertEqual(len(list(track.get_automation().get_automation_targets())), 1)
        self.assertIsNotNone(track.get_automation().get_automation_value_by_target(target))
        self.assertTrue(track.get_automation().get_automation_value_by_id(
            target.to_tf_automation_target_id()) == track.get_automation().get_automation_value_by_target(target))

    def test_removes_automation(self):
        song, track = create_song()
        target = AutomationTarget(
            AutomationTargetType.AUDIO_PLUGIN,
            'pluginId1',
            'paramId1',
        )

        track.get_automation().add_automation(target)
        track.get_automation().add_automation(target)
        self.assertEqual(len(list(track.get_automation().get_automation_targets())), 2)
        self.assertIsNotNone(track.get_automation().get_automation_value_by_target(target))
        track.get_automation().remove_automation(target)
        self.assertEqual(len(list(track.get_automation().get_automation_targets())), 0)
        self.assertIsNone(track.get_automation().get_automation_value_by_target(target))

    def test_multiple_automation_targets_update_the_same_value(self):
        song, track = create_song()
        target1 = AutomationTarget(
            AutomationTargetType.AUDIO_PLUGIN,
            'pluginId1',
            'paramId1',
        )
        target2 = AutomationTarget(
            AutomationTargetType.AUDIO_PLUGIN,
            'pluginId1',
            'paramId1',
        )

        track.get_automation().add_automation(target1)
        track.get_automation().add_automation(target2)
        self.assertEqual(len(list(track.get_automation().get_automation_targets())), 2)
        self.assertFalse(
            track.get_automation().get_automation_value_by_target(target1).get_disabled(),  # type:ignore
        )
        self.assertFalse(track.get_automation().get_automation_value_by_target(target2).get_disabled())  # type:ignore
        track.get_automation().get_automation_value_by_target(target1).set_disabled(True)  # type:ignore
        self.assertTrue(track.get_automation().get_automation_value_by_target(target2).get_disabled())  # type:ignore


if __name__ == '__main__':
    unittest.main()
