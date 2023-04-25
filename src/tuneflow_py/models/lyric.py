import re
from typing import Callable, List, Optional
import unicodedata

from tuneflow_py.utils import lower_equal
from tuneflow_py.models.protos import song_pb2

from .song import Song

LyricTokenizer = Callable[[str], List[str]]
DEFAULT_PPQ = Song.get_default_resolution()


class Lyrics:
    def __init__(self, song: Song) -> None:
        self.song = song
        self._proto = song._proto.lyrics
        if self._proto is None:
            self._proto = song_pb2.Lyrics()
        self.lines = [
            LyricLine(lyrics=self, start_tick=line_proto.start_tick, proto=line_proto)
            for line_proto in self._proto.lines
        ]

    def _clear_proto(self) -> None:
        while len(self._proto.lines) > 0:
            self._proto.lines.pop()
    
    def clear(self) -> None:
        self._clear_proto()
        self.lines = []

    def _update_proto(self) -> None:
        self._clear_proto()
        self._proto.lines.extend([line._proto for line in self.lines])

    def get_lines(self):
        return self.lines

    def get_index_of_line_at_tick(self, tick: int):
        if not self.lines:
            return -1
        start_search_index = lower_equal(
            self.lines, tick, key=lambda line: line.get_start_tick()
        )
        for index in range(start_search_index, -1, -1):
            line = self.lines[index]
            if tick >= line.get_start_tick() and tick <= line.get_end_tick():
                return index
        return -1

    def create_line(self, start_tick: int, resolve_order: bool = True):
        lyric_line = LyricLine(lyrics=self, start_tick=start_tick)
        self.lines.append(lyric_line)
        self._proto.lines.append(lyric_line._proto)
        if resolve_order:
            self.sort_lines()
        return lyric_line

    def create_line_from_string(self, input: str, start_tick: int, end_tick: int, tokenizer: Optional[LyricTokenizer] = None):
        line = self.create_line(start_tick=start_tick, resolve_order=False)
        if not input:
            return line
        LyricLine.create_words_from_string(line, input, start_tick, end_tick, tokenizer)
        self._update_proto()
        return line

    def remove_line_at_index(self, index: int):
        if index < 0 or index >= len(self.lines):
            return
        self.lines.pop(index)
        self._proto.lines.pop(index)

    def clone_line(self, original_line: "LyricLine"):
        line = LyricLine(lyrics=self, start_tick=original_line.get_start_tick())
        for lyric_word in original_line.get_words():
            line.create_word(
                word=lyric_word.get_word(),
                start_tick=lyric_word.get_start_tick(),
                end_tick=lyric_word.get_end_tick(),
            )
        self.lines.append(line)
        self._proto.lines.append(line._proto)
        return line

    def sort_lines(self):
        self.lines.sort(key=lambda line: line.get_start_tick())
        self._update_proto()


class LyricLine:
    def __init__(self, lyrics: Lyrics, proto: song_pb2.LyricLine | None = None) -> None:
        self.lyrics = lyrics
        if proto is not None:
            self._proto = proto
        else:
            self._proto = song_pb2.LyricLine()

        # Initialize the words list with the corresponding LyricWord instances.
        self.words = [
            LyricWord(line=self, proto=word_proto)
            for word_proto in self._proto.words
        ]

    def _clear_proto(self):
        while len(self._proto.words) > 0:
            self._proto.words.pop()

    def _update_proto(self) -> None:
        self._clear_proto()
        self._proto.words.extend([word._proto for word in self.words])

    def get_sentence(self) -> str:
        if self.is_empty():
            return ""
        return "".join(word.get_word() for word in self.words)

    def is_empty(self) -> bool:
        return len(self.words) == 1 and self.words[0].get_word() == LyricWord.PLACEHOLDER_WORD

    def get_start_tick(self) -> int:
        if not self.words:
            raise ValueError("Words cannot be empty")
        return self.words[0].get_start_tick()

    def get_end_tick(self) -> int:
        if not self.words:
            raise ValueError("Words cannot be empty")
        return LyricLine.get_line_end_tick_impl(
            self.words, lambda item: item.get_end_tick()
        )

    @staticmethod
    def get_line_end_tick_impl(words, word_to_end_tick_fn) -> int:
        return word_to_end_tick_fn(max(words, key=word_to_end_tick_fn))

    def get_words(self) -> List["LyricWord"]:
        return self.words

    def move_to(self, start_tick: int, end_tick: int) -> None:
        original_start = self.get_start_tick()
        original_end = self.get_end_tick()
        if original_start is None or original_end is None:
            return
        start_tick = max(start_tick, 0)
        end_tick = max(end_tick, start_tick)
        ratio = (end_tick - start_tick) / (original_end - original_start)
        for word in self.words:
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
        tick_per_word = (end_tick - start_tick) / len(words)
        new_words = []
        for i, word in enumerate(words):
            start = int(start_tick + i * tick_per_word)
            end = int(start_tick + (i + 1) * tick_per_word)
            new_word = LyricWord(line=self, word=word, start_tick=start, end_tick=end)
            new_words.append(new_word)

        self.words = new_words
        self.sort_words()

    def create_word(self, word: str, start_tick: int, end_tick: int, resolve_order: bool = True):
        new_word = LyricWord(line=self, word=word, start_tick=start_tick, end_tick=end_tick)
        if self.is_empty():
            self.words = [new_word]
            self._proto.words.extend([new_word._proto])
        else:
            self.words.append(new_word)
            self._proto.words.append(new_word._proto)
        if resolve_order:
            self.sort_words()
        return new_word

    def clear(self):
        self._clear_proto()
        new_word = self.create_placeholder_word()
        self.words = [new_word]
        self._proto.words.extend([new_word._proto])

    def create_placeholder_word(self):
        return LyricWord(
            line=self,
            word=LyricWord.PLACEHOLDER_WORD,
            start_tick=self.get_start_tick(),
            end_tick=self.get_start_tick() + DEFAULT_PPQ * 4 * 2,
        )

    def delete_word(self, word: "LyricWord"):
        search_index = lower_equal(self.words, word, key=lambda w: w.get_start_tick())
        while search_index >= 0 and self.words[search_index]:
            lyric_word = self.words[search_index]
            if lyric_word == word:
                if len(self.words) == 1:
                    # Words will become empty, insert a default placeholder.
                    self.clear()
                else:
                    self.words.pop(search_index)
                    self._proto.words.pop(search_index)
                return lyric_word
            search_index -= 1
        return None

    def remove_word_at_index(self, index: int):
        if index < 0 or index >= len(self.words):
            return
        self.words.pop(index)
        self._proto.words.pop(index)

    def sort_words(self):
        start_tick = self.get_start_tick()
        self.words.sort(key=lambda word: word.get_start_tick())
        if self.get_start_tick() != start_tick:
            self.lyrics.sort_lines()
        self._update_proto()

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

    def delete_from_parent(self):
        self.line.delete_word(self)

    def get_word(self):
        return self._proto.word

    def set_word(self, word: "LyricWord"):
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

    def __eq__(self, other: "LyricWord"):
        if isinstance(other, LyricWord):
            return (
                self._proto.start_tick == other.start_tick
                and self._proto.end_tick == other.end_tick
                and self._proto.word == other.word
            )
        return False
