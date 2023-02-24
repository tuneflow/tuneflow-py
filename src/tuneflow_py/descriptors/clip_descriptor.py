from typing_extensions import Required, NotRequired, TypedDict


class AudioData(TypedDict):
    '''
    A temporary holder of audio data that will be converted to local files and cleared once received.
    '''

    format: Required[str]
    data: Required[bytes]


class AudioClipData(TypedDict):
    ''' Audio-related clip data. '''

    audio_file_path: NotRequired[str]
    '''
    The absolute file path of the audio.
    
    Can be omitted if `audioData` is set.
    '''

    audio_data: NotRequired[AudioData]
    '''
    A temporary holder of the audio file data. When set, the daw will save a copy to local file system and replace
    `audioFilePath` with the saved file path, and this field will be cleared afterwards.
    
    Can be omitted if `audioFilePath` is set.

    IMPORTANT: Only supported on desktop, requires desktop app version >= 1.8.9.
    '''

    start_tick: Required[int]
    '''
    The start tick of the audio.
    
    This is an absolute position that locates the start of the audio within the song.
    
    When the clip adjusts left or right boundaries, the start position of the audio
    will not change.
    
    When the clip moves, the audio will move along with the clip.
    '''

    duration: Required[float]
    '''
    The duration of the audio content. You can get this value in the plugin
    by using `readApis.readAudioBuffer` to read the audio file content as `AudioBuffer`, and then
    get the duration from `audioBuffer.duration`.
    
    Duration needs to be updated whenever audio file (path or content) changes.
    '''
