from __future__ import annotations
import re
from typing import Callable, List, Optional, Generator
import unicodedata

from tuneflow_py.utils import lower_equal
from tuneflow_py.models.protos import song_pb2
from tuneflow_py.models.song import Song

LyricTokenizer = Callable[[str], List[str]]
DEFAULT_PPQ = Song.get_default_resolution()


class LyricWord:
    '''
    LyricWord is the primary unit of a LyricLine
    The class is a wrapper of the LyricWord proto object
    A word is located with start_tick and end_tick
    '''
    # The default word placeholer for an empty lyric line
    PLACEHOLDER_WORD = "^%%^"

    def __init__(
        self,
        line: LyricLine,
        word: str | None = None,
        start_tick: int | None = None,
        end_tick: int | None = None,
        proto: song_pb2.LyricLine.LyricWord | None = None
    ):
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
        '''
        Set a new start tick for the word.
        This might delete the word if the new start tick is greater than or equal to the end tick.

        Args:
            start_tick (int): The new start tick of the word.
        '''
        if start_tick >= self._proto.end_tick and resolve_order:
            self._delete_from_parent()
            return
        self._proto.start_tick = start_tick
        if resolve_order:
            self.line.sort_words()

    def get_end_tick(self):
        return self._proto.end_tick

    def set_end_tick(self, end_tick: int, resolve_order=True):
        '''
        Set a new end tick for the word.
        This might delete the word if the new end tick is less than or equal to the start tick.

        Args:
            end_tick (int): The new end tick of the word.
        '''
        if end_tick <= self._proto.start_tick and resolve_order:
            self._delete_from_parent()
            return
        self._proto.end_tick = end_tick

    def move_to(self, start_tick: int, end_tick: int):
        if start_tick >= end_tick:
            self._delete_from_parent()
        self._proto.start_tick = start_tick
        self._proto.end_tick = end_tick
        self.line.sort_words()

    def _delete_from_parent(self):
        '''
        Delete the word from the parent line.
        '''
        self.line.remove_word(self)

    def __eq__(self, other: LyricWord):
        return (
            self._proto.start_tick == other._proto.start_tick
            and self._proto.end_tick == other._proto.end_tick
            and self._proto.word == other._proto.word
        )


class LyricLine:
    '''
    Lyrics is composed of a list of LyricLine objects
    '''

    def __init__(
        self,
        lyrics: Lyrics,
        start_tick: int | None = None,
        proto: song_pb2.LyricLine | None = None
    ):
        self.lyrics = lyrics
        if proto is not None:
            self._proto = proto
        else:
            self._proto = song_pb2.LyricLine()

        if len(self._proto.words) == 0:
            # Create a default placeholder for the empty line
            self._proto.words.add(
                word=LyricWord.PLACEHOLDER_WORD,
                start_tick=start_tick,
                end_tick=start_tick + DEFAULT_PPQ,
            )

    def __len__(self) -> int:
        if self.is_empty():
            return 0
        return len(self._proto.words)

    def __getitem__(self, index: int) -> LyricWord:
        return self.get_word_at_index(index)

    def is_empty(self) -> bool:
        # A line is empty if it only contains a placeholder word
        return len(self._proto.words) == 1 and self._proto.words[0].word == LyricWord.PLACEHOLDER_WORD

    def get_words(self) -> Generator:
        for word_proto in self._proto.words:
            yield LyricWord(line=self, proto=word_proto)

    def get_sentence(self) -> str:
        if self.is_empty():
            return ""
        return "".join(word_proto.word for word_proto in self._proto.words)

    @staticmethod
    def _get_start_tick(line_proto: song_pb2.LyricLine) -> int:
        if len(line_proto.words) == 0:
            raise ValueError("Words cannot be empty")
        return line_proto.words[0].start_tick

    @staticmethod
    def _get_end_tick(line_proto: song_pb2.LyricLine) -> int:
        if len(line_proto.words) == 0:
            raise ValueError("Words cannot be empty")
        return max(line_proto.words, key=lambda word_proto: word_proto.end_tick).end_tick

    def get_start_tick(self) -> int:
        return LyricLine._get_start_tick(self._proto)

    def get_end_tick(self) -> int:
        return LyricLine._get_end_tick(self._proto)

    def move_to(self, start_tick: int, end_tick: int) -> None:
        original_start = self.get_start_tick()
        original_end = self.get_end_tick()
        if original_start is None or original_end is None:
            return
        start_tick = max(start_tick, 0)
        end_tick = max(end_tick, start_tick)
        ratio = round((end_tick - start_tick) / (original_end - original_start))
        for word in self.get_words():
            word_start_tick = round(
                start_tick + (word.get_start_tick() - original_start) * ratio
            )
            word_end_tick = round(
                start_tick + (word.get_end_tick() - original_start) * ratio
            )
            word.move_to(word_start_tick, word_end_tick)

    def _set_words_from_tokens(
        self,
        tokens: List[str],
        start_tick: int,
        end_tick: int,
    ):
        if len(tokens) == 0:
            self.clear()
            return
        tick_per_word = (end_tick - start_tick) // len(tokens)
        del self._proto.words[:]
        for i, word in enumerate(tokens):
            start = start_tick + i * tick_per_word
            # Adjust the last word to match the end tick
            end = start_tick + (i + 1) * tick_per_word if i < len(tokens) - 1 else end_tick
            self._proto.words.add(word=word, start_tick=start, end_tick=end)
        self.sort_words()

    def set_words_from_string(
        self,
        input: str,
        start_tick: int | None = None,
        end_tick: int | None = None,
        tokenizer: Optional[LyricTokenizer] = None,
    ):
        '''
        Update lyric word objects of the line from a string of words
        The string is split into words with a tokenizer if provided
        Otherwise, the default tokenizer is used

        Args:
            input (str): The string of words
            start_tick (int | None): The start tick of the line. Use the original tick if set None
            end_tick (int | None): The end tick of the line. Use the original tick if set None
            tokenizer (Optional[LyricTokenizer]): The tokenizer to use
        '''
        start_tick = self.get_start_tick() if start_tick is None else start_tick
        end_tick = self.get_end_tick() if end_tick is None else end_tick
        tokens = (
            tokenizer(input) if tokenizer
            else LyricLine.default_lyric_tokenizer(input)
        )
        if len(tokens) == 0:
            self.clear()
        self._set_words_from_tokens(tokens, start_tick, end_tick)

    @staticmethod
    def _get_index_of_word_at_tick(line: song_pb2.LyricLine, tick: int):
        '''
        Internal generator implementation that locates word at a given tick.
        '''
        if len(line.words) == 0 or tick < LyricLine._get_start_tick(line) or tick >= LyricLine._get_end_tick(line):
            return -1
        index = lower_equal(
            line.words,
            tick,
            key=lambda item: item if isinstance(item, int) else item.start_tick
        )
        if index in range(len(line.words)):
            return index
        return -1

    def get_index_of_word_at_tick(self, tick: int):
        '''
        Return the index of the word in this proto that contains the given tick,
        or -1 if no such word exists.

        Args:
            tick (int): The tick to search for.

        Return:
            int: The index of the line that contains the tick, or -1 if not found.
        '''
        return LyricLine._get_index_of_word_at_tick(self._proto, tick)

    def create_word(self, word: str, start_tick: int, end_tick: int, resolve_order: bool = True):
        if self.is_empty():
            # Remove the placeholder
            del self._proto.words[:]
        proto = self._proto.words.add(word=word, start_tick=start_tick, end_tick=end_tick)
        if resolve_order:
            self.sort_words()
        return LyricWord(line=self, proto=proto)

    def get_word_at_index(self, index: int) -> LyricWord:
        if index < 0 or index >= len(self._proto.words):
            raise IndexError("Index out of range")
        return LyricWord(
            line=self,
            proto=self._proto.words[index]
        )

    def clear(self):
        new_word = self._create_placeholder_word()
        del self._proto.words[:]
        self._proto.words.append(new_word._proto)

    def _create_placeholder_word(self):
        return LyricWord(
            line=self,
            word=LyricWord.PLACEHOLDER_WORD,
            start_tick=self.get_start_tick(),
            end_tick=self.get_start_tick() + DEFAULT_PPQ * 4 * 2,
        )

    def remove_word(self, word: LyricWord):
        search_index = lower_equal(self._proto.words, word._proto, key=lambda word: word.start_tick)
        while search_index >= 0:
            lyric_word = self._proto.words[search_index]
            if lyric_word == word._proto:
                self.remove_word_at_index(search_index)
                break
            search_index -= 1

    def remove_word_at_index(self, index: int):
        if index < 0 or index >= len(self._proto.words):
            raise IndexError("Index out of range")
        if len(self._proto.words) == 1:
            # Words will become empty, insert a default placeholder.
            self.clear()
        else:
            del self._proto.words[index]
            self.sort_words()

    def sort_words(self):
        self._proto.words.sort(key=lambda word: word.start_tick)
        self.lyrics.sort_lines()

    @staticmethod
    def default_lyric_tokenizer(input: str) -> List[str]:
        '''
        Tokenizes the input string based on specific rules.

        Args:
            input (str): The input string to be tokenized.

        Returns:
            List[str]: A list of tokens generated based on the rules.
        '''
        tokens = []

        current_token = ''
        for char in input:
            if char == ' ':
                # Handle spaces
                if current_token:
                    tokens.append(current_token)
                    current_token = ''
                tokens.append(char)
            elif re.match(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff66-\uff9f]', char):
                # Handle Japanese, Chinese, Korean characters
                if current_token:
                    tokens.append(current_token)
                    current_token = ''
                tokens.append(char)
            elif unicodedata.category(char).startswith('P'):
                # Handle punctuation marks
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


class Lyrics:
    def __init__(self, song: Song) -> None:
        self.song = song
        if song._proto.lyrics is None:
            song._proto.lyrics = song_pb2.Lyrics()
        self._proto = song._proto.lyrics

    def __getitem__(self, index: int) -> LyricLine:
        '''
        Access the lyric line at the given index.
        Usage: lyrics[index]
        '''
        return self.get_line_at_index(index)

    def __len__(self) -> int:
        '''
        Get the number of lyric lines.
        Usage: len(lyrics)
        '''
        return len(self._proto.lines)

    def create_line(self, start_tick: int, resolve_order: bool = True):
        '''
        Creates a new empty LyricLine object at the given start_tick.

        Args:
            start_tick (int): The starting tick for the new lyric line.
            resolve_order (bool, optional): Whether to sort the lyric lines by start_tick. Defaults to True.

        Returns:
            LyricLine: The newly created LyricLine object.
        '''
        line_proto = self._proto.lines.add()
        line = LyricLine(lyrics=self, start_tick=start_tick, proto=line_proto)
        if resolve_order:
            self.sort_lines()
        return line

    def create_line_from_string(self, input: str, start_tick: int, end_tick: int, tokenizer: Optional[LyricTokenizer] = None):
        '''
        Create a Line object from a string of words.

        Args:
            input (str): The input string of words.
            start_tick (int): The starting tick of the line.
            end_tick (int): The ending tick of the line.
            tokenizer (Optional[LyricTokenizer], optional): The tokenizer to use for splitting the input string into words.
                If None, the default tokenizer will be used. Defaults to None.

        Returns:
            Line: The created Line object.

        Raises:
            ValueError: If the input string is empty.
        '''
        line_proto = self._proto.lines.add()
        line = LyricLine(lyrics=self, start_tick=start_tick, proto=line_proto)
        if not input:
            return line
        line.set_words_from_string(input, start_tick, end_tick, tokenizer)
        return line

    @staticmethod
    def _get_index_of_line_at_tick(proto: song_pb2.Lyrics, tick: int):
        '''
        Internal generator implementation that locates lyrlic line at a given tick.
        '''
        if len(proto.lines) == 0:
            return -1
        start_search_index = lower_equal(
            proto.lines,
            tick,
            key=lambda item: item if isinstance(item, int) else LyricLine._get_start_tick(item)
        )
        for index in range(start_search_index, -1, -1):
            line = proto.lines[index]
            if tick >= LyricLine._get_start_tick(line) and tick <= LyricLine._get_end_tick(line):
                yield index
        return -1

    def get_index_of_line_at_tick(self, tick: int):
        '''
        Yield the index of the line in this proto that contains the given tick,
        or -1 if no such line exists.

        Args:
            tick (int): The tick to search for.

        Yields:
            int: The index of the line that contains the tick, or -1 if not found.
        '''
        for index in Lyrics._get_index_of_line_at_tick(self._proto, tick):
            yield index

    def get_line_at_index(self, index: int):
        if index < 0 or index >= len(self._proto.lines):
            raise IndexError("Index out of range")
        return LyricLine(lyrics=self, proto=self._proto.lines[index])

    def get_lines(self):
        for line_proto in self._proto.lines:
            if len(line_proto.words) == 0:
                raise Exception("Lyric line has no words")
            yield LyricLine(
                lyrics=self,
                proto=line_proto
            )

    def remove_line(self, line: LyricLine):
        search_index = lower_equal(
            self._proto.lines,
            line._proto,
            key=lambda line: LyricLine._get_start_tick(line)
        )
        while search_index >= 0:
            line_proto = self._proto.lines[search_index]
            if line_proto == line._proto:
                self.remove_line_at_index(search_index)
            search_index -= 1

    def remove_line_at_index(self, index: int):
        if index < 0 or index >= len(self._proto.lines):
            return
        del self._proto.lines[index]

    def clone_line(self, original_line: LyricLine):
        new_proto = self._proto.lines.add()
        new_proto.CopyFrom(original_line._proto)
        self.sort_lines()
        return LyricLine(lyrics=self, proto=new_proto)

    def sort_lines(self):
        self._proto.lines.sort(key=lambda line: LyricLine._get_start_tick(line))

    def clear(self):
        del self._proto.lines[:]
