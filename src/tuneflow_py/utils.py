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
