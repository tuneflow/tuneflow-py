from __future__ import annotations
from tuneflow_py.descriptors.common import EntityId
from typing import List, Union
from typing_extensions import Literal, TypedDict, NotRequired

TuneflowPluginTriggerType = Literal['song', 'context-track-content', 'context-track-control', 'selected-clips']
'''
The types of plugin triggers.

    * `song` The plugin will be available on the entire song.
        When running, it will not receive additional trigger data..
    * `context-track-content` The plugin will be available on the **content** part(the "track" portion) of the track.
        When running, it will receive trigger data about the triggering track under cursor.
    * `context-track-control` The plugin will be available on the **control** part(the "knobs" portion) of the track.
        When running, it will receive trigger data about the triggering track under cursor.
    * `selected-clips` The plugin will be available on the clip. When running, it will receive trigger data about the currently selected clips.
'''

AllowedTrackType = Literal['midi', 'audio', 'aux']

AllowedClipType = Literal['midi', 'audio']


class AllowedTrackInstrument(TypedDict):
    program: NotRequired[int]
    isDrum: NotRequired[bool]


class ContextTrackContentTriggerConfig(TypedDict):
    allowedTrackTypes: NotRequired[List[AllowedTrackType]]

    allowedTrackInstruments: NotRequired[List[AllowedTrackInstrument]]
    '''
    When specified, the corresponding track's instrument must match one of the given instruments.

    NOTE: Use with caution since it blocks the plugin from running, and a lot of times you can simply
    update the tracks's instrument to what you want.
    '''

    skipAllowedInstrumentCheckOnDesktop: NotRequired[bool]
    '''
    If true, allowed instruments flags will be ignored on desktop.
    '''


class ContextTrackControlTriggerConfig(TypedDict):
    allowedTrackTypes: NotRequired[List[AllowedTrackType]]

    allowedTrackInstruments: NotRequired[List[AllowedTrackInstrument]]
    '''
    When specified, the corresponding track's instrument must match one of the given instruments.

    NOTE: Use with caution since it blocks the plugin from running, and a lot of times you can simply
    update the tracks's instrument to what you want.
    '''

    skipAllowedInstrumentCheckOnDesktop: NotRequired[bool]
    '''
    If true, allowed instruments flags will be ignored on desktop.
    '''


class SelectedClipTriggerConfig(TypedDict):
    allowedClipTypes: NotRequired[List[AllowedClipType]]

    maxNumClips: NotRequired[int]

    allowedTrackInstruments: NotRequired[List[AllowedTrackInstrument]]
    '''
    When specified, the corresponding track's instrument must match one of the given instruments.

    NOTE: Use with caution since it blocks the plugin from running, and a lot of times you can simply
    update the tracks's instrument to what you want.
    '''

    skipAllowedInstrumentCheckOnDesktop: NotRequired[bool]
    '''
    If true, allowed instruments flags will be ignored on desktop.
    '''


class TuneflowPluginTriggerConfig(TypedDict):
    type: TuneflowPluginTriggerType
    config: NotRequired[Union[ContextTrackContentTriggerConfig,
                              ContextTrackControlTriggerConfig, SelectedClipTriggerConfig]]


TuneflowPluginTrigger = Union[TuneflowPluginTriggerType, TuneflowPluginTriggerConfig]
'''
The type of the `triggers` field in the plugin's `bundle.json`.
'''


class TuneflowPluginTriggerData(TypedDict):
    '''
    The type of data that is injected to the params of the plugins that have `triggers` specified.
    '''
    type: TuneflowPluginTriggerType
    entities: NotRequired[List[EntityId]]


class TuneflowPluginOptions(TypedDict):
    allowReset: NotRequired[bool]
    '''
    Whether to allow users to reset all parameters of this plugin.

    Defaults to true.
    '''

    allowManualApplyAdjust: NotRequired[bool]
    '''
    Whether the user can manually apply this plugin and go back to adjust it.
    Enable this when you want the user to frequently toggle this plugin on and off
    to see the difference.
    For example: A plugin that divides a track into two, you want the user to
    easily switch between the plugin is on or off to see what's going on.
   
    Defaults to false.
    '''


TuneflowPluginCategory = Literal['generate', 'transcribe', 'analyze', 'synthesize', 'import', 'export', 'misc']
