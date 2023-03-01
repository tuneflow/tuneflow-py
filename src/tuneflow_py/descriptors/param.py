from __future__ import annotations
from tuneflow_py.descriptors.text import LabelText
from tuneflow_py.descriptors.widget import WidgetDescriptor
from tuneflow_py.descriptors.common import ClipInfo
from typing import Any, Optional, List
from typing_extensions import TypedDict, Required, NotRequired, Literal
from enum import Enum


class ClipAudioDataInjectOptions(TypedDict):
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
    options: Required[ClipAudioDataInjectOptions | SelectedClipInfosInjectOptions]


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


class ParamDescriptor(TypedDict, total=False):
    '''
    Definition of the config for a single param.

    Note that the members here use camel case to be
    consistent with the typescript plugins.
    '''

    displayName: LabelText
    ''' The name to display on the UI. '''

    widget: WidgetDescriptor
    ''' Configuration of the widget to display on the UI. '''

    defaultValue: Any
    ''' The default value of the param. '''

    adjustable: Optional[bool]
    '''
    Whether this param is adjustable. If the param is not adjustable, the controllable
    part is not shown.

    Defaults to true.
    '''

    hidden: Optional[bool]
    ''' Whether this param is hidden completely. '''

    optional: Optional[bool]
    ''' Whether this param can be left None. '''

    description: Optional[LabelText]
    ''' Explaining what this parameter is for. '''

    injectFrom: InjectSource | InjectConfig
    '''
    Injects the value from the editor at the time the plugin runs.
    
    If specified, the editor will inject the value specified by the `InjectSource` or `InjectConfig`,
    '''

    adjustableWhenPluginIsApplied: Optional[bool]
    '''
    If set to true, this param can still be adjusted
    when the plugin is applied. However, changing the param
    will invalidate all the changes after this plugin.
    '''
