from __future__ import annotations
import re
from typing import Callable, List, Optional
import unicodedata

from tuneflow_py.utils import lower_equal
from tuneflow_py.models.protos import song_pb2
from tuneflow_py.models.song import Song

LyricTokenizer = Callable[[str], List[str]]
DEFAULT_PPQ = Song.get_default_resolution()


class Lyrics:
    def __init__(self, song: Song) -> None:
        self.song = song
        if song._proto.lyrics is None:
            song._proto.lyrics = song_pb2.Lyrics()
        self._proto = song._proto.lyrics

    def create_line(self, start_tick: int, resolve_order: bool = True):
        lyric_line = LyricLine(lyrics=self, start_tick=start_tick)
        if resolve_order:
            self.sort_lines()
        return lyric_line

    def create_line_from_string(self, input: str, start_tick: int, end_tick: int, tokenizer: Optional[LyricTokenizer] = None):
        line = self.create_line(start_tick=start_tick, resolve_order=False)
        if not input:
            return line
        line.create_words_from_string(input, start_tick, end_tick, tokenizer)
        return line

    def get_index_of_line_at_tick(self, tick: int):
        if len(self._proto.lines) == 0:
            return -1
        start_search_index = lower_equal(
            self._proto.lines, tick, key=lambda line: line.start_tick
        )
        for index in range(start_search_index, -1, -1):
            line = self._proto.lines[index]
            if tick >= line.start_tick and tick <= line.end_tick:
                return index
        return -1

    def get_lines(self):
        for line_proto in self._proto.lines:
            if len(line_proto.words) == 0:
                raise Exception("Lyric line has no words")
            yield LyricLine(
                lyrics=self,
                start_tick=line_proto.words[0].start_tick,
                proto=line_proto
            )
            
    def get_line_at_index(self, index: int):
        proto = self._proto.lines[index]
        if len(proto.words) == 0:
            raise Exception("Lyric line has no words")
        return LyricLine(
            lyrics=self,
            start_tick=proto.words[0].start_tick,
            proto=self._proto.lines[index]
        )
        
    def remove_line_at_index(self, index: int):
        if index < 0 or index >= len(self._proto.lines):
            return
        self._proto.lines.pop(index)

    def clone_line(self, original_line: "LyricLine"):
        line = LyricLine(lyrics=self, start_tick=original_line.get_start_tick())
        for lyric_word in original_line.get_words():
            line.create_word(
                word=lyric_word.get_word(),
                start_tick=lyric_word.get_start_tick(),
                end_tick=lyric_word.get_end_tick(),
            )
        self._proto.lines.append(line._proto)
        return line

    def sort_lines(self):
        self._proto.lines.sort(key=lambda line: line.words[0].start_tick)

    def clear(self):
        del self._proto.lines[:]


class LyricLine:
    def __init__(self, lyrics: Lyrics, start_tick: int, proto: song_pb2.LyricLine | None = None) -> None:
        self.lyrics = lyrics
        if proto is not None:
            self._proto = proto
        else:
            self._proto = self.lyrics._proto.lines.add()

        if len(self._proto.words) == 0:
            placeholder_word = LyricWord(
                line=self,
                word=LyricWord.PLACEHOLDER_WORD,
                start_tick=start_tick,
                end_tick=start_tick + DEFAULT_PPQ,
            )
            self._proto.words.append(placeholder_word._proto)
        

    def is_empty(self) -> bool:
        return len(self._proto.words) == 1 and self._proto.words[0].word == LyricWord.PLACEHOLDER_WORD

    def get_words(self) -> List["LyricWord"]:
        for word_proto in self._proto.words:
            yield LyricWord(
                line=self,
                word=word_proto.word,
                start_tick=word_proto.start_tick,
                end_tick=word_proto.end_tick,
                proto=word_proto
            )

    def get_sentence(self) -> str:
        if self.is_empty():
            return ""
        return "".join(word_proto.word for word_proto in self._proto.words)

    def get_start_tick(self) -> int:
        if len(self._proto.words) == 0:
            raise ValueError("Words cannot be empty")
        return self._proto.words[0].start_tick

    def get_end_tick(self) -> int:
        if len(self._proto.words) == 0:
            raise ValueError("Words cannot be empty")
        return max(self._proto.words, key=lambda item: item.end_tick).end_tick

    def move_to(self, start_tick: int, end_tick: int) -> None:
        original_start = self.get_start_tick()
        original_end = self.get_end_tick()
        if original_start is None or original_end is None:
            return
        start_tick = max(start_tick, 0)
        end_tick = max(end_tick, start_tick)
        ratio = (end_tick - start_tick) / (original_end - original_start)
        for word in self.get_words():
            word_start_tick = int(
                start_tick + (word.get_start_tick() - original_start) * ratio
            )
            word_end_tick = int(
                start_tick + (word.get_end_tick() - original_start) * ratio
            )
            word.move_to(word_start_tick, word_end_tick)

    def create_words_from_string(
        self,
        input: str,
        start_tick: int,
        end_tick: int,
        tokenizer: Optional[LyricTokenizer] = None,
    ) -> None:
        words = (
            tokenizer(input) if tokenizer
            else LyricLine.default_lyric_tokenizer(input)
        )
        if len(words) == 0:
            return
        tick_per_word = (end_tick - start_tick) / len(words)
        del self._proto.words[:]
        for i, word in enumerate(words):
            start = int(start_tick + i * tick_per_word)
            end = int(start_tick + (i + 1) * tick_per_word)
            self._proto.words.add(word=word, start_tick=start, end_tick=end)
        self.sort_words()

    def create_word(self, word: str, start_tick: int, end_tick: int, resolve_order: bool = True):
        if self.is_empty():
            del self._proto.words[:]
        self._proto.words.add(word=word, start_tick=start_tick, end_tick=end_tick)
        if resolve_order:
            self.sort_words()

    def clear(self):
        new_word = self.create_placeholder_word()
        del self._proto.words[:]
        self._proto.words.append(new_word._proto)

    def create_placeholder_word(self):
        return LyricWord(
            line=self,
            word=LyricWord.PLACEHOLDER_WORD,
            start_tick=self.get_start_tick(),
            end_tick=self.get_start_tick() + DEFAULT_PPQ * 4 * 2,
        )

    def remove_word(self, word: "LyricWord"):
        search_index = lower_equal(self._proto.words, word, key=lambda w: w.start_tick)
        while search_index >= 0 and self._proto.words[search_index]:
            lyric_word = self._proto.words[search_index]
            if lyric_word == word:
                if len(self._proto.words) == 1:
                    # Words will become empty, insert a default placeholder.
                    self.clear()
                else:
                    self._proto.words.pop(search_index)
            search_index -= 1

    def remove_word_at_index(self, index: int):
        if index < 0 or index >= len(self._proto.words):
            raise IndexError("Index out of range")
        if len(self._proto.words) == 1:
            # Words will become empty, insert a default placeholder.
            self.clear()
        else:
            self._proto.words.pop(index)

    def sort_words(self):
        start_tick = self.get_start_tick()
        self._proto.words.sort(key=lambda word: word.start_tick)
        if self.get_start_tick() != start_tick:
            self.lyrics.sort_lines()

    @staticmethod
    def default_lyric_tokenizer(input: str) -> List[str]:
        tokens = []

        current_token = ''
        for char in input:
            if char == ' ':
                if current_token:
                    tokens.append(current_token)
                    current_token = ''
                tokens.append(char)
            elif re.match(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff66-\uff9f]', char):
                if current_token:
                    tokens.append(current_token)
                    current_token = ''
                tokens.append(char)
            elif unicodedata.category(char).startswith('P'):
                if current_token:
                    if re.match(r"^[']+$", char) and re.match(r'^[A-Za-z0-9]+$', current_token):
                        current_token += char
                    else:
                        tokens.append(current_token)
                        tokens.append(char)
                        current_token = ''
                else:
                    tokens.append(char)
            else:
                current_token += char

        if current_token:
            tokens.append(current_token)

        return tokens


class LyricWord:
    PLACEHOLDER_WORD = "^%%^"

    def __init__(self, line: LyricLine, word: str, start_tick: int, end_tick: int, proto: song_pb2.LyricLine.LyricWord | None = None):
        self.line = line
        if proto is not None:
            self._proto = proto
        else:
            self._proto = song_pb2.LyricLine.LyricWord()
            self._proto.word = word
            self._proto.start_tick = start_tick
            self._proto.end_tick = end_tick

    def get_line(self):
        return self.line

    def get_word(self):
        return self._proto.word

    def set_word(self, word: str):
        if not word:
            raise ValueError("Word cannot be empty")
        self._proto.word = word

    def get_start_tick(self):
        return self._proto.start_tick

    def set_start_tick(self, start_tick: int, resolve_order=True):
        if (self._proto.start_tick >= self._proto.end_tick and resolve_order):
            self.delete_from_parent()
            return
        self._proto.start_tick = start_tick
        if resolve_order:
            self.line.sort_words()

    def get_end_tick(self):
        return self._proto.end_tick

    def move_to(self, start_tick: int, end_tick: int):
        self._proto.start_tick = start_tick
        self._proto.end_tick = end_tick
    
    def delete_from_parent(self):
        self.line.remove_word(self)

    def __eq__(self, other: song_pb2.LyricLine.LyricWord | "LyricWord"):
        if isinstance(other, song_pb2.LyricLine.LyricWord):
            return (
                self._proto.start_tick == other.start_tick
                and self._proto.end_tick == other.end_tick
                and self._proto.word == other.word
            )
        elif isinstance(other, LyricWord):
            return (
                self._proto.start_tick == other._proto.start_tick
                and self._proto.end_tick == other._proto.end_tick
                and self._proto.word == other._proto.word
            )
        return False
