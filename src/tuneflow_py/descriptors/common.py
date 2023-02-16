from typing import Literal, TypedDict, Optional, Union

RealNumber = Union[int, float]


class ClipInfo(TypedDict):
    track_id: str
    clip_id: str


SupportedPlatform = Literal['desktop', 'web']


class PluginInfo(TypedDict, total=False):
    supported_platforms: Optional[SupportedPlatform]
    ''' If not provided, supports all platforms. '''

    min_required_desktop_version: Optional[str]
    ''' If specified, the desktop requires a minimum version to run this plugin. '''

    is_in_development: Optional[bool]
    ''' If true, this plugin is in development stage and can only be accessed by its developer. '''
