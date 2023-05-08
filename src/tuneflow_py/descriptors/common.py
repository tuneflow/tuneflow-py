from typing import Union
from typing_extensions import Literal, TypedDict, Required, NotRequired

RealNumber = Union[int, float]


class ClipInfo(TypedDict):
    track_id: Required[str]
    clip_id: Required[str]


class EntityId(TypedDict):
    type: Required[Literal['song', 'track', 'clip',
                           'note', 'lyrics-structure', 'lyrics-line']]

    trackId: NotRequired[str]
    ''' Required when type is `track` | `clip` | `note` '''

    clipId: NotRequired[str]
    ''' Required when type is `clip` | `note` '''

    noteId: NotRequired[int]
    ''' Required when type is `note` '''

    lyricsLineIndex: NotRequired[int]
    ''' Required when type is `lyrics-line` '''

    lyricsStructureIndex: NotRequired[int]
    ''' Required when type is `lyrics-structure` '''


SupportedPlatform = Literal['desktop', 'web']
