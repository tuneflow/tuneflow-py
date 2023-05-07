from __future__ import annotations
from tuneflow_py.descriptors.text import LabelText
from tuneflow_py.descriptors.widget import WidgetDescriptor
from tuneflow_py.descriptors.common import ClipInfo
from tuneflow_py.descriptors.clip_descriptor import AudioData
from typing import Any, List
from typing_extensions import TypedDict, Required, NotRequired, Literal
from enum import Enum


class Mp3DataConvertOptions(TypedDict):
    sampleRate: NotRequired[int]
    ''' Sample rate in Hz, default 44100. '''


class AudioDataConvertOptions(TypedDict):
    toFormat: Required[Literal['ogg', 'wav']]
    options: NotRequired[Mp3DataConvertOptions]


class AudioDataInjectOptions(TypedDict):
    convert: NotRequired[AudioDataConvertOptions]
    '''
    When enabled, only the visible portion of the clip will be converted to the given format.
   
    The converted audio data will start from the clip start and end at the clip end.
    '''


class ClipAudioDataInjectOptions(AudioDataInjectOptions):
    '''
    Inject config for when injection source is `InjectSource.ClipAudioData`.
    '''
    clips: Required[Literal['selectedAudioClips',] | List[ClipInfo]]


class SelectedClipInfosInjectOptions(TypedDict):
    '''
    Inject config for when injection source is `InjectSource.SelectedClipInfos`.
    '''

    maxNumClips: NotRequired[int]
    '''
    Maximum number of clip infos to include. Defaults to unlimited.
    '''


class InjectConfig(TypedDict):
    '''
    Used to specify a injection source when additional config is needed.
    '''

    type: Required[int]
    options: Required[ClipAudioDataInjectOptions |
                      SelectedClipInfosInjectOptions]


class InjectSource(Enum):
    SelectedTrackIds = 1
    ''' A string that represents the ids of the current selected tracks. '''

    SelectedClipInfos = 2
    ''' A `list[ClipInfo]` that represents the `ClipInfo`s of the current selected clips. '''

    TickAtPlayhead = 3
    ''' A number that represents the current tick that the playhead is at. '''

    EditingClipInfo = 4
    ''' The `ClipInfo` of the clip that is being edited in the MIDI editor. '''

    EditingNoteIds = 5
    ''' The ids of the notes that is being edited in the MIDI editor. '''

    TickAtPlayheadSnappedToBeat = 6
    ''' A number that represents the start tick of the beat where the playhead is at. '''

    ClipAudioData = 7
    ''' A list of `AudioData` for specified clips. '''

    Language = 8
    ''' The user language. '''


class ParamDescriptor(TypedDict):
    '''
    Definition of the config for a single param.

    Note that the members here use camel case to be
    consistent with the typescript plugins.
    '''

    displayName: Required[LabelText]
    ''' The name to display on the UI. '''

    widget: Required[WidgetDescriptor]
    '''
    Configuration of the widget to display on the UI.

    Use  `{ "type": WidgetType.NoWidget.value }` if you don't need a widget.
    '''

    defaultValue: NotRequired[Any]
    ''' The default value of the param. '''

    adjustable: NotRequired[bool]
    '''
    Whether this param is adjustable. If the param is not adjustable, the controllable
    part is not shown.

    Defaults to true.
    '''

    hidden: NotRequired[bool]
    ''' Whether this param is hidden completely. Defaults to false. '''

    optional: NotRequired[bool]
    ''' Whether this param can be left None. Defaults to false. '''

    description: NotRequired[LabelText]
    ''' Explaining what this parameter is for. '''

    injectFrom: NotRequired[int | InjectConfig]
    '''
    Injects the value from the editor at the time the plugin runs.
    
    If specified, the editor will inject the value specified by the `InjectSource` or `InjectConfig`,
    '''

    adjustableWhenPluginIsApplied: NotRequired[bool]
    '''
    If set to true, this param can still be adjusted
    when the plugin is applied. However, changing the param
    will invalidate all the changes after this plugin.

    Defaults to false.
    '''


class ClipAudioDataInjectDataEntry(TypedDict):
    clipInfo: Required[ClipInfo]
    audioData: Required[AudioData]


ClipAudioDataInjectData = List[ClipAudioDataInjectDataEntry]
'''
Type of the injected data when injection source is `InjectSource.ClipAudioData`.
'''
