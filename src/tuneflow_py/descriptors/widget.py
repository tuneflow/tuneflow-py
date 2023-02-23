from __future__ import annotations
from tuneflow_py.descriptors.text import LabelText
from tuneflow_py.descriptors.common import RealNumber
from enum import Enum
from typing import Optional, Any, List
from typing_extensions import Literal, TypedDict
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


class SliderWidgetConfig(TypedDict, total=False):
    minValue: RealNumber
    maxValue: RealNumber
    step: RealNumber
    unit: Optional[str]


class InputWidgetConfig(TypedDict, total=False):
    minValue: RealNumber
    maxValue: RealNumber
    step: RealNumber


class TrackSelectorWidgetConfig(TypedDict, total=False):
    alwaysShowTrackInfo: Optional[bool]
    '''  Whether to always show the track info. Default to false. '''

    allowedTrackTypes: Optional[List[TrackType]]  # type: ignore
    ''' If specified, only the allowed types of tracks can be selected. '''


class PitchWidgetConfig(TypedDict, total=False):
    minAllowedPitch: Optional[RealNumber]
    maxAllowedPitch: Optional[RealNumber]


class TrackPitchSelectorWidgetConfig(TypedDict, total=False):
    trackSelectorConfig: TrackSelectorWidgetConfig
    pitchSelectorConfig: PitchWidgetConfig


class InstrumentSelectorWidgetConfig(TypedDict, total=False):
    disabledPrograms: Optional[List[RealNumber]]
    ''' Not supported yet. '''


class SelectWidgetOption(TypedDict, total=False):
    label: LabelText
    value: Any


class SelectWidgetConfig(TypedDict, total=False):
    options: List[SelectWidgetOption]

    allowSearch: Optional[bool]
    ''' Whether to show search box. Default to false. '''

    placeholder: LabelText

    virtualListProps: Optional[Any]
    ''' https://arco.design/vue/component/select#virtual-list '''

    populateOptionsWithGeneratableStyles: Optional[bool]
    '''
    Whether to populate the options with the styles that
    TuneFlow can generate.
    '''

    populateOptionsWithGeneratableTempos: Optional[bool]
    '''
    Whether to populate the options with the tempo settings that
    TuneFlow can generate with.
    '''


class SelectListWidgetConfig(TypedDict, total=False):
    options: List[SelectWidgetOption]
    maxHeight: Optional[RealNumber]
    size: Optional[str]
    virtualListProps: Optional[Any]
    ''' https://arco.design/vue/component/list '''

    allowSearch: Optional[bool]


class SwitchWidgetConfig(TypedDict, total=False):
    type: Optional[Literal['circle', 'round', 'line']]
    '''
    'circle' | 'round' | 'line'
    
    https://arco.design/vue/component/switch
    '''


class InputNumberWidgetConfig(TypedDict, total=False):
    minValue: RealNumber
    maxValue: RealNumber
    step: RealNumber


class FileSelectorWidgetConfig(TypedDict, total=False):
    allowedExtensions: List[str]
    ''' The extensions (without ".") that are allowed to choose. '''

    selectDirectory: Optional[str]
    '''
    Whether to select a directory instead of a file.
    Default to false.
    '''

    placeholder: Optional[LabelText]
    ''' Custom placeholder text. '''

    selectLocalFile: Optional[bool]
    ''' If true, selects local system files. '''


AudioSourceType = Literal['file', 'audioTrack', 'record']


class MultiSourceAudioSelectorWidgetConfig(TypedDict, total=False):
    allowedSources: Optional[List[AudioSourceType]]
    ''' Default to allow all audio sources. '''


class MultiSourceAudioSelectorResult(TypedDict, total=False):
    sourceType: AudioSourceType

    audioInfo: Any
    '''
    Result type will be:
    * `File` if `sourceType` is 'file'
    * trackId if `sourceType` is 'audioTrack'
    * `AudioBuffer` if `sourceType` is 'record'
    '''


class DescriptionData(TypedDict, total=False):
    label: LabelText
    value: str
    span: RealNumber


class DescriptionsWidgetConfig(TypedDict, total=False):
    size: Literal['mini', 'small', 'medium', 'large']
    column: int
    data: List[DescriptionData]


class TextAreaWidgetConfig(TypedDict, total=False):
    placeholder: str
    maxLength: int
    allowClear: bool
    autoSize: bool


class WidgetDescriptor(TypedDict, total=False):
    type: int  # WidgetType
    config: Optional[SliderWidgetConfig
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
