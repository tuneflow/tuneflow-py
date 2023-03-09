from typing import Union
from typing_extensions import Literal, TypedDict, Required, NotRequired

RealNumber = Union[int, float]


class ClipInfo(TypedDict):
    track_id: str
    clip_id: str


class EntityId(TypedDict):
    type: Required[Literal['song', 'track', 'clip', 'note']]
    trackId: NotRequired[str]
    clipId: NotRequired[str]
    noteId: NotRequired[int]


SupportedPlatform = Literal['desktop', 'web']
