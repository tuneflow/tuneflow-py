from __future__ import annotations
from tuneflow_py.descriptors.text import LabelText
from tuneflow_py.descriptors.common import RealNumber
from enum import Enum
from typing import Any, List, Dict
from typing_extensions import Literal, TypedDict, Required, NotRequired
from tuneflow_py.models.track import TrackType


class WidgetType(Enum):
    Slider = 1
    Input = 2
    # A widget that selects one track.
    TrackSelector = 3
    # A widget that selects a pitch.
    Pitch = 4
    TrackPitchSelector = 5
    InstrumentSelector = 6
    Select = 7
    Switch = 8
    InputNumber = 9
    MultiTrackSelector = 10
    # Does not render a widget.
    NoWidget = 11
    FileSelector = 12
    MultiSourceAudioSelector = 13
    AudioRecorder = 14
    SelectList = 15
    # Read-only table of descriptions.
    Descriptions = 16
    TextArea = 17


SliderMarkerConfig = Dict[RealNumber, LabelText]


class SliderWidgetConfig(TypedDict):
    minValue: Required[RealNumber]
    maxValue: Required[RealNumber]
    step: Required[RealNumber]
    unit: NotRequired[str]
    markers: NotRequired[SliderMarkerConfig]


class InputWidgetConfig(TypedDict):
    minValue: Required[RealNumber]
    maxValue: Required[RealNumber]
    step: Required[RealNumber]


class TrackSelectorWidgetConfig(TypedDict):
    alwaysShowTrackInfo: NotRequired[bool]
    '''  Whether to always show the track info. Default to false. '''

    allowedTrackTypes: NotRequired[List[TrackType]]  # type: ignore
    ''' If specified, only the allowed types of tracks can be selected. '''


class PitchWidgetConfig(TypedDict):
    minAllowedPitch: NotRequired[RealNumber]
    maxAllowedPitch: NotRequired[RealNumber]


class TrackPitchSelectorWidgetConfig(TypedDict):
    trackSelectorConfig: Required[TrackSelectorWidgetConfig]
    pitchSelectorConfig: Required[PitchWidgetConfig]


class InstrumentSelectorWidgetConfig(TypedDict):
    disabledPrograms: NotRequired[List[RealNumber]]
    ''' Not supported yet. '''


class SelectWidgetOption(TypedDict):
    label: Required[LabelText]
    value: Required[Any]


class SelectWidgetConfig(TypedDict):
    options: Required[List[SelectWidgetOption]]

    allowSearch: NotRequired[bool]
    ''' Whether to show search box. Default to false. '''

    placeholder: Required[LabelText]

    virtualListProps: NotRequired[Any]
    ''' https://arco.design/vue/component/select#virtual-list '''

    populateOptionsWithGeneratableStyles: NotRequired[bool]
    '''
    Whether to populate the options with the styles that
    TuneFlow can generate.
    '''

    populateOptionsWithGeneratableTempos: NotRequired[bool]
    '''
    Whether to populate the options with the tempo settings that
    TuneFlow can generate with.
    '''


class SelectListWidgetConfig(TypedDict):
    options: Required[List[SelectWidgetOption]]
    maxHeight: NotRequired[RealNumber]
    size: NotRequired[str]
    virtualListProps: NotRequired[Any]
    ''' https://arco.design/vue/component/list '''

    allowSearch: NotRequired[bool]


class SwitchWidgetConfig(TypedDict):
    type: NotRequired[Literal['circle', 'round', 'line']]
    '''
    'circle' | 'round' | 'line'
    
    https://arco.design/vue/component/switch
    '''


class InputNumberWidgetConfig(TypedDict):
    minValue: Required[RealNumber]
    maxValue: Required[RealNumber]
    step: Required[RealNumber]


class FileSelectorWidgetConfig(TypedDict):
    allowedExtensions: Required[List[str]]
    ''' The extensions (without ".") that are allowed to choose. '''

    selectDirectory: NotRequired[str]
    '''
    Whether to select a directory instead of a file.
    Default to false.
    '''

    placeholder: NotRequired[LabelText]
    ''' Custom placeholder text. '''

    selectLocalFile: NotRequired[bool]
    ''' If true, selects local system files. '''


AudioSourceType = Literal['file', 'audioTrack', 'record']


class MultiSourceAudioSelectorWidgetConfig(TypedDict):
    allowedSources: NotRequired[List[AudioSourceType]]
    ''' Default to allow all audio sources. '''


class MultiSourceAudioSelectorResult(TypedDict):
    sourceType: Required[AudioSourceType]

    audioInfo: Required[Any]
    '''
    Result type will be:
    * `File` if `sourceType` is 'file'
    * trackId if `sourceType` is 'audioTrack'
    * `AudioBuffer` if `sourceType` is 'record'
    '''


class DescriptionData(TypedDict):
    label: Required[LabelText]
    value: Required[str]
    span: NotRequired[RealNumber]


class DescriptionsWidgetConfig(TypedDict):
    size: Required[Literal['mini', 'small', 'medium', 'large']]
    column: Required[int]
    data: Required[List[DescriptionData]]


class TextAreaWidgetConfig(TypedDict):
    placeholder: NotRequired[LabelText]
    maxLength: NotRequired[int]
    allowClear: NotRequired[bool]
    autoSize: NotRequired[bool]


class WidgetDescriptor(TypedDict):
    type: Required[int]  # WidgetType
    config: NotRequired[SliderWidgetConfig
                        | InputWidgetConfig
                        | SelectWidgetConfig
                        | TrackSelectorWidgetConfig
                        | PitchWidgetConfig
                        | TrackPitchSelectorWidgetConfig
                        | InstrumentSelectorWidgetConfig
                        | SwitchWidgetConfig
                        | InputNumberWidgetConfig
                        | FileSelectorWidgetConfig
                        | SelectListWidgetConfig
                        | MultiSourceAudioSelectorWidgetConfig
                        | DescriptionsWidgetConfig
                        | TextAreaWidgetConfig]
