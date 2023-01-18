from typing import TypedDict, Optional


class SongAccess(TypedDict, total=False):
    create_track: Optional[bool]
    ''' Whether the plugin has permission to create a new track. '''

    remove_track: Optional[bool]
    ''' Whether the plugin has permission to remove a track. '''
