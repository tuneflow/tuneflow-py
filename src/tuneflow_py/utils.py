from __future__ import annotations
from math import exp, log10, log, pow
from typing import Callable


def db_to_volume_value(db: float):
    '''
    Maps a dB value to a volume value (0 - 1).
    '''
    return exp((db - 6) * (1 / 20)) if db > -100 else 0


def gain_to_db(gain: float):
    '''
    @param gain A value between 0 - 2, corresponding to -inf to +6dB, gain == 1 equals dB == 0.0
    '''
    if (gain <= 0):
        return -100

    return 20 * log10(gain)


def volume_value_to_db(volume: float):
    '''
    @param volume A value between 0 - 1, corresponding to -inf to +6 dB.
    '''
    return 20 * log(volume) + 6 if volume > 0 else -100.0


def volume_value_to_gain(volume: float):
    '''
    @param volume A value between 0 - 1, corresponding to -inf to +6 dB.
    '''
    return pow(10, (20 * log(volume) + 6) * (1 / 20)) if volume > 0 else 0


def gain_to_volume_value(gain: float):
    '''
    @param gain A value between 0 - 2, corresponding to -inf to +6dB, gain == 1 equals dB == 0.0
    '''
    return exp((20 * log10(gain) - 6) * (1 / 20)) if gain > 0 else 0


def greater_equal(sorted_list: list, val, key: Callable | None = None, low: int | None = None, high: int | None = None):
    '''
    Returns the index of the first item in the array >= val. This is a successor query which also returns the item if present.
    '''
    low = low if low is not None else 0
    high = high if high is not None else len(sorted_list) - 1
    i = high + 1
    while low <= high:
        m = (low + high) >> 1
        x = sorted_list[m]
        p = (key(x) - key(val)) if key is not None else (x - val)
        if p >= 0:
            i = m
            high = m - 1
        else:
            low = m + 1
    return i


def greater_than(sorted_list: list, val, key: Callable | None = None, low: int | None = None, high: int | None = None):
    '''
    Returns the index of the first item in the array > val. This is the same as a successor query.
    '''
    low = low if low is not None else 0
    high = high if high is not None else len(sorted_list) - 1
    i = high + 1
    while low <= high:
        m = (low + high) >> 1
        x = sorted_list[m]
        p = (key(x) - key(val)) if key is not None else (x - val)
        if p > 0:
            i = m
            high = m - 1
        else:
            low = m + 1
    return i


def lower_than(sorted_list: list, val, key: Callable | None = None, low: int | None = None, high: int | None = None):
    '''
    Returns the index of the last item in the array < val. This is the same as a predecessor query.
    '''
    low = low if low is not None else 0
    high = high if high is not None else len(sorted_list) - 1
    i = low - 1
    while low <= high:
        m = (low + high) >> 1
        x = sorted_list[m]
        p = (key(x) - key(val)) if key is not None else (x - val)
        if p < 0:
            i = m
            low = m + 1
        else:
            high = m - 1
    return i


def lower_equal(sorted_list: list, val, key: Callable | None = None, low: int | None = None, high: int | None = None):
    '''
    Returns the index of the last item in the array <= val. This is a predecessor query which also returns the item if present.
    '''
    low = low if low is not None else 0
    high = high if high is not None else len(sorted_list) - 1
    i = low - 1
    while low <= high:
        m = (low + high) >> 1
        x = sorted_list[m]
        p = (key(x) - key(val)) if key is not None else (x - val)
        if (p <= 0):
            i = m
            low = m + 1
        else:
            high = m - 1
    return i


def eq(sorted_list: list, val, key: Callable | None = None, low: int | None = None, high: int | None = None):
    '''
    Returns an index of some item in the array == y or -1 if the item is not present.
    '''
    low = low if low is not None else 0
    high = high if high is not None else len(sorted_list) - 1
    while low <= high:
        m = (low + high) >> 1
        x = sorted_list[m]
        p = (key(x) - key(val)) if key is not None else (x - val)
        if p == 0:
            return m
        if p <= 0:
            low = m + 1
        else:
            high = m - 1
    return -1


def get_audio_plugin_tuneflow_id(
    manufacturer_name: str,
    plugin_format_name: str,
    plugin_name: str,
    plugin_version: str,
):
    '''
    Gets an id that Tuneflow can uniquely identify a plugin.
    '''
    return f'{manufacturer_name} // {plugin_format_name} // {plugin_name} // {plugin_version}'


def get_audio_plugin_versionless_tuneflow_id(
    manufacturer_name: str,
    plugin_format_name: str,
    plugin_name: str,
):
    '''
    Gets an id that Tuneflow can uniquely identify a plugin regardless of version.
    '''
    return f'{manufacturer_name} // {plugin_format_name} // {plugin_name}'


def decode_audio_plugin_tuneflow_id(tf_id: str):
    parts = tf_id.split(' // ')
    if len(parts) < 4:
        raise Exception('Invalid audio plugin tuneflow id.')

    return {
        "name": parts[2],
        "manufacturer_name": parts[0],
        "plugin_format_name": parts[1],
        "plugin_version": parts[3],
    }


def to_versionless_tf_id(tf_id: str):
    '''
    Converts a full tf_id to a versionless tf_id.
    @param tf_id A full tf_id
    @returns A versionless tf_id
    '''
    parts = decode_audio_plugin_tuneflow_id(tf_id)
    return get_audio_plugin_versionless_tuneflow_id(
        parts["manufacturer_name"],
        parts["plugin_format_name"],
        parts["name"],
    )


def are_tuneflow_ids_equal(tf_id1: str, tf_id2: str):
    return tf_id1 == tf_id2


def are_tuneflow_ids_equal_ignore_version(tf_id1: str, tf_id2: str):
    parsed_id1 = decode_audio_plugin_tuneflow_id(tf_id1)
    parsed_id2 = decode_audio_plugin_tuneflow_id(tf_id2)
    if len(parsed_id1) != len(parsed_id2):
        return False

    for key in parsed_id1:
        if (key == 'plugin_version'):
            continue
        if key not in parsed_id2:
            return False
        if parsed_id1[key] != parsed_id2[key]:
            return False
    return True
