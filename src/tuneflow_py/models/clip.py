from tuneflow_py.models.protos import song_pb2
from tuneflow_py.models.note import Note

ClipType = song_pb2.ClipType

class Clip:
    def __init__(self, proto: song_pb2.Clip | None = None) -> None:
        self._proto = proto if proto is not None else song_pb2.Clip()
    
    def get_note_count(self):
        return len(self._proto.notes)

    def get_raw_notes(self):
        for note_proto in self._proto.notes:
            yield Note(proto=note_proto)
    
    def get_type(self) -> int:
        return self._proto.type
    
    def delete_note_at(self, index: int):
        self._proto.notes.pop(index)