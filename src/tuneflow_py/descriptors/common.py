from typing import Union
from typing_extensions import Literal, TypedDict

RealNumber = Union[int, float]


class ClipInfo(TypedDict):
    track_id: str
    clip_id: str


SupportedPlatform = Literal['desktop', 'web']
