from __future__ import annotations
from tuneflow_py.models.protos import song_pb2
from tuneflow_py.utils import greater_equal, greater_than, lower_than
from types import SimpleNamespace
from typing import List
from typing_extensions import TypedDict, Required, Any

AutomationTargetType = song_pb2.AutomationTarget.TargetType


class AutomationTarget:
    def __init__(
            self, type: AutomationTargetType | None = None, plugin_instance_id: str | None = None, param_id: str | None = None,
            proto: song_pb2.AutomationTarget | None = None) -> None:
        if proto is not None:
            self._proto = proto
        else:
            self._proto = song_pb2.AutomationTarget(
                type=type, audio_plugin_id=plugin_instance_id, param_id=param_id)

    def get_type(self):
        return self._proto.type

    def set_type(self, type: AutomationTargetType):
        self._proto.type = type

    def get_plugin_instance_id(self):
        return self._proto.audio_plugin_id

    def set_plugin_instance_id(self, plugin_instance_id: str | None = None):
        if plugin_instance_id is None:
            self._proto.ClearField("audio_plugin_id")
        else:
            self._proto.audio_plugin_id = plugin_instance_id

    def get_param_id(self):
        return self._proto.param_id

    def set_param_id(self, param_id: str | None = None):
        if param_id is None:
            self._proto.ClearField("param_id")
        else:
            self._proto.param_id = param_id

    def equals(self, target: AutomationTarget):
        return AutomationTarget.are_automation_targets_equal(
            self.get_type(),
            target.get_type(),
            self.get_plugin_instance_id(),
            target.get_plugin_instance_id(),
            self.get_param_id(),
            target.get_param_id(),
        )

    def clone(self):
        new_proto = song_pb2.AutomationTarget()
        new_proto.CopyFrom(self._proto)
        return AutomationTarget(proto=new_proto)

    def to_tf_automation_target_id(self):
        '''
        Gets a unique string id that identifies this target type.
        '''
        return AutomationTarget.encode_automation_target(
            self.get_type(),
            self.get_plugin_instance_id(),
            self.get_param_id())

    def __repr__(self) -> str:
        return str(self._proto)

    @staticmethod
    def encode_automation_target(
        target_type: AutomationTargetType,
        plugin_instance_id: str | None,
        param_id: str | None,
    ):
        if target_type == AutomationTargetType.AUDIO_PLUGIN:
            return f'{target_type}^^{plugin_instance_id}^^{param_id}'

        return f'{target_type}'

    @staticmethod
    def decode_automation_target(encoded_target: str):
        parts = encoded_target.split('^^')
        if len(parts) == 0:
            raise Exception(f'Invalid automation target id: {encoded_target}')

        type = int(parts[0])
        if len(parts) > 2:
            AutomationTarget(type, parts[1], parts[2])

        return AutomationTarget(type)

    @staticmethod
    def are_automation_targets_equal(
        target_type1: AutomationTargetType,
        target_type2: AutomationTargetType,
        plugin_instance_id1: str | None,
        plugin_instance_id2: str | None,
        param_id1: str | None,
        param_id2: str | None
    ):
        return (
            AutomationTarget.encode_automation_target(target_type1, plugin_instance_id1, param_id1) ==
            AutomationTarget.encode_automation_target(target_type2, plugin_instance_id2, param_id2)
        )


class AutomationPoint(TypedDict):
    '''
    A single point in an automation curve.
    '''
    id: Required[int]
    tick:  Required[int]
    value:  Required[float]


class AutomationValue:
    '''
    The points and settings of an automation param.
    '''

    def __init__(self, proto: song_pb2.AutomationValue | None = None):
        if proto is not None:
            self._proto = proto
        else:
            self._proto = song_pb2.AutomationValue()
            self._proto.disabled = False
        self._next_point_id = None

    def get_disabled(self):
        return self._proto.disabled

    def set_disabled(self, is_disabled: bool):
        self._proto.disabled = is_disabled

    def get_points(self) -> List[AutomationPoint]:
        return self._proto.points

    def get_points_in_range(self, start_tick: int, end_tick: int):
        target_point = SimpleNamespace()
        target_point.tick = start_tick
        start_index = greater_equal(
            self._proto.points,
            target_point,
            lambda x: x.tick,
        )
        results = []
        for i in range(start_index, len(self._proto.points)):
            point = self._proto.points[i]
            if (point.tick > end_tick):
                break
            results.append(point)

        return results

    def add_point(self, tick: int, value: float, overwrite=False):
        '''
        @param overwrite Whether to overwrite the points at the insert tick.
        '''
        new_point = song_pb2.AutomationValue.ParamValue(
            tick=tick,
            value=max(0, min(1, value)),
            id=self._get_next_point_id(),
        )
        return self._ordered_insert_point(self._proto.points, new_point, overwrite)

    def remove_points(self, point_ids: List[int]):
        '''
        Remove points that match the given ids.
        '''
        id_set = set(point_ids)
        for i in range(len(self._proto.points)-1, -1, -1):
            point = self._proto.points[i]
            if point.id in id_set:
                self._proto.points.pop(i)

    def remove_points_in_range(self, start_tick: int, end_tick: int):
        '''
        Removes all points within the given time range.
        @param start_tick Inclusive
        @param end_tick Inclusive
        '''
        target_point = SimpleNamespace()
        target_point.tick = start_tick
        start_index = greater_equal(
            self._proto.points,
            target_point,
            lambda x: x.tick,
        )
        if start_index >= len(self._proto.points):
            return

        end_index = start_index
        while (end_index + 1 < len(self._proto.points) and self._proto.points[end_index + 1].tick <= end_tick):
            end_index += 1
        del self._proto.points[start_index:end_index+1]

    def move_points_in_range(
        self,
        start_tick: int,
        end_tick: int,
        offset_tick: int,
        offset_value: float,
        overwrite_values_in_drag_area=True,
    ):
        points = self.get_points_in_range(start_tick, end_tick)
        self.move_points(
            [point.id for point in points],
            offset_tick,
            offset_value,
            overwrite_values_in_drag_area,
        )

    def move_all_points(self, offset_tick: int, offset_value: float, overwrite_values_in_drag_area=True):
        self.move_points(
            [point.id for point in self._proto.points],
            offset_tick,
            offset_value,
            overwrite_values_in_drag_area,
        )

    def move_points(
            self,
        point_ids: List[int],
        offset_tick: int,
        offset_value: float,
        overwrite_values_in_drag_area=True,
    ):
        '''
        @param overwrite_values_in_drag_area If true, all values in between the moved points' old and new indexes will be removed.
        '''
        if (len(point_ids) == 0):
            return

        point_id_set = set(point_ids)
        drag_area_left_index = None
        drag_area_right_index = None
        selected_points = []
        for i in range(len(self._proto.points)):
            point = self._proto.points[i]
            if point.id not in point_id_set:
                continue

            selected_points.append(point)
            if drag_area_left_index is None:
                drag_area_left_index = i

            drag_area_right_index = i

        if drag_area_left_index is None or drag_area_right_index is None:
            # None of the given points are not in the automation.
            return

        if overwrite_values_in_drag_area:
            # Remove values in drag area.
            if (offset_tick < 0):
                # Move left, remove values to the left.
                selected_points_left_after_move = max(
                    0,
                    self._proto.points[drag_area_left_index].tick + offset_tick,
                )
                target_point = SimpleNamespace()
                target_point.tick = selected_points_left_after_move
                start_remove_index = greater_than(
                    self._proto.points,
                    target_point,
                    lambda x: x.tick,
                )
                if (start_remove_index < drag_area_left_index):
                    del self._proto.points[start_remove_index:drag_area_left_index]
            elif (offset_tick > 0):
                # Move right, remove values to the right.
                selected_points_right_after_move = self._proto.points[drag_area_right_index].tick + offset_tick
                target_point = SimpleNamespace()
                target_point.tick = selected_points_right_after_move
                end_remove_index = lower_than(
                    self._proto.points,
                    target_point,
                    lambda x: x.tick,
                )
                if (end_remove_index > drag_area_right_index):
                    del self._proto.points[drag_area_right_index + 1:end_remove_index+1]

        for point in selected_points:
            point.tick = max(0, point.tick + offset_tick)
            point.value = max(0, min(1, point.value + offset_value))

        # Maintain the order of points.
        if (abs(offset_tick) > 0):
            self._proto.points.sort(key=lambda x: x.tick)

    def clone(self):
        new_proto = song_pb2.AutomationValue()
        new_proto.CopyFrom(self._proto)
        return AutomationValue(proto=new_proto)

    def _get_next_point_id(self):
        if self._next_point_id is None:
            if len(self._proto.points) == 0:
                self._next_point_id = 1
            else:
                self._next_point_id = max([point.id for point in self._proto.points]) + 1

        point_id = self._next_point_id
        if (self._next_point_id >= 2147483647):
            self._next_point_id = 1
        else:
            self._next_point_id += 1

        return point_id

    def __eq__(self, __value: AutomationValue) -> bool:
        return self._proto == __value._proto

    @staticmethod
    def _ordered_insert_point(
        points: Any,
        new_point: song_pb2.AutomationValue.ParamValue,
        overwrite=False,
    ):
        '''
        Be careful that only a copy of the new_point will be inserted, not the original object.

        So you need to update your reference to the new_point after inserting it.

        @return The copy of the original point that is actually inserted into points.
        '''
        insert_index = greater_equal(
            points,
            new_point,
            lambda x: x.tick
        )

        while (overwrite and insert_index >= 0 and insert_index < len(points) and points[insert_index].tick == new_point.tick):
            # Remove the points at the insert tick.
            del points[insert_index]
        points.insert(insert_index, new_point)
        return points[insert_index]


class AutomationData:
    '''
    All automation data of one entity (such as a track).
    *
    * Each `AutomationData` consists of several automation targets(`AutomationTarget`) and
    * the values(`AutomationValue`) store in unique targets.
    *
    * Note that there can be duplicate targets, but targets of the same type write to
    * and read from the same automation value.
    *
    * For example, there can be multiple Volume targets, each Volume target corresponds to
    * the same automation value.
    '''

    def __init__(self, proto: song_pb2.AutomationData | None = None):
        if proto is not None:
            self._proto = proto
        else:
            self._proto = song_pb2.AutomationData()

    def get_automation_targets(self):
        '''
        All automation targets specified by the user.

        Note that the return of this method is a generator,
        you would need to convert it to a list to be able
        to access it with an index.
        '''
        for target in self._proto.targets:
            yield AutomationTarget(proto=target)

    def get_automation_target_values(self):
        '''
        Values of each unique automation target.
        '''
        raise Exception("get_automation_target_values not implemented yet")

    def get_or_create_automation_value_by_id(self, tf_automation_target_id: str) -> AutomationValue:
        '''
        @param tf_automation_target_id The targetId that can be retrieved from `AutomationTarget.prototype.toTfAutomationTargetId` or `AutomationTarget.encodeAutomationTarget`.
        @returns The automation value of the given target if exists, otherwise creates a new one and returns it.
        '''
        return AutomationValue(proto=self._proto.target_values[tf_automation_target_id])

    def get_automation_value_by_id(self, tf_automation_target_id: str):
        '''
        Gets or creates the automation points and settings of an automation target.
        @param tfAutomationTargetId The targetId that can be retrieved from `AutomationTarget.prototype.toTfAutomationTargetId` or `AutomationTarget.encodeAutomationTarget`.
        '''
        if tf_automation_target_id not in self._proto.target_values:
            return None
        return AutomationValue(proto=self._proto.target_values[tf_automation_target_id])

    def get_automation_value_by_target(self, target: AutomationTarget):
        tf_automation_target_id = target.to_tf_automation_target_id()
        return self.get_automation_value_by_id(tf_automation_target_id)

    def add_automation(self, target: AutomationTarget, index=0):
        '''
        Adds an automation target, if there was no such target, creates the automation value.
        '''
        if not isinstance(index, int):
            index = 0
        self._proto.targets.insert(index, target._proto)
        target._proto = self._proto.targets[index]
        tf_automation_target_id = target.to_tf_automation_target_id()
        self.get_or_create_automation_value_by_id(tf_automation_target_id)

    def remove_automation(self, target: AutomationTarget):
        '''
        Removes all automation targets of the given type and its automation value.
        '''
        # Remove targets.
        for i in range(len(self._proto.targets)-1, -1, -1):
            existing_target = AutomationTarget(proto=self._proto.targets[i])
            if (existing_target.equals(target)):
                del self._proto.targets[i]

        # Remove values.
        tf_automation_target_id = target.to_tf_automation_target_id()
        del self._proto.target_values[tf_automation_target_id]

    def remove_automation_of_plugin(self, plugin_instance_id: str):
        '''
        Remove all automations associated with a certain plugin.
        '''
        for i in range(len(self._proto.targets)-1, -1, -1):
            automation_target = AutomationTarget(proto=self._proto.targets[i])
            if (automation_target.get_plugin_instance_id() == plugin_instance_id):
                self.remove_automation(automation_target)
        for tf_automation_target_id in self._proto.target_values:
            automation_target = AutomationTarget.decode_automation_target(tf_automation_target_id)
            if (automation_target.get_plugin_instance_id() == plugin_instance_id):
                self.remove_automation(automation_target)

    def remove_all_points_within_range(self, start_tick: int, end_tick: int):
        '''
        @param start_tick Inclusive
        @param end_tick Inclusive
        '''
        for tf_automation_target_id in self._proto.target_values:
            automation_value = AutomationValue(proto=self._proto.targetValues[tf_automation_target_id])
            automation_value.remove_points_in_range(start_tick, end_tick)

    def move_all_points_within_range(
        self,
        start_tick: int,
        end_tick: int,
        offset_tick: int,
        offset_value: float,
    ):
        '''
        @param start_tick Inclusive
        @param end_tick Inclusive
        '''
        for tf_automation_target_id in self._proto.target_values:
            automation_value = AutomationValue(proto=self._proto.targetValues[tf_automation_target_id])
            automation_value.move_points_in_range(
                start_tick,
                end_tick,
                offset_tick,
                offset_value,
                overwrite_values_in_drag_area=False,
            )

    def clone(self):
        '''
        Creates a clone of this automation data.
        '''
        new_proto = song_pb2.AutomationData()
        new_proto.CopyFrom(self._proto)
        return AutomationData(proto=new_proto)
