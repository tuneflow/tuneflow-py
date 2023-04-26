import unittest
from typing import Dict
from tuneflow_py.models.song import Song
from tuneflow_py.models.lyric import Lyrics, LyricLine, LyricWord


class MockLyricLine:
    def __init__(self, sentence: str, start_tick: int, end_tick: int):
        self.sentence = sentence
        self.start_tick = start_tick
        self.end_tick = end_tick

    def assert_equal(self, line: LyricLine):
        if line.get_sentence() != self.sentence:
            raise Exception(
                f'Lyric lines are not equal. Expected sentence {self.sentence} but got {line.get_sentence()}'
            )
        if line.get_start_tick() != self.start_tick:
            raise Exception(
                f'Lyric lines are not equal. Expected start tick {self.start_tick} but got {line.get_start_tick()}'
            )
        if line.get_end_tick() != self.end_tick:
            raise Exception(
                f'Lyric lines are not equal. Expected end tick {self.end_tick} but got {line.get_end_tick()}'
            )


def create_lyrics():
    song = Song()
    lyrics = Lyrics(song)
    lyrics.create_line_from_string("Hello world this is a test.", 10, 50)
    lyrics.create_line_from_string("Mixing symbols & numbers 12345, special #%$^characters, LoWeR uPPeR CaSe", 60, 100)
    lyrics.create_line_from_string("émphasis on accénts, we also allow overlapping", 50, 110)
    # This is an example of Chinese lyrics.
    lyrics.create_line_from_string("这是一个中文歌词的例子。", 500, 550)
    # This is an example of Japanese lyrics.
    lyrics.create_line_from_string("これは日本語の歌詞の例です。", 600, 650)
    return lyrics


class TestLyrics(unittest.TestCase):
    def test_create_line(self):
        lyrics = create_lyrics()
        line = lyrics.create_line(660)
        self.assertEqual(len(lyrics._proto.lines), 6)
        self.assertEqual(line.is_empty(), True)
        MockLyricLine("", 660, 1140).assert_equal(line)

    def test_create_line_from_string(self):
        lyrics = create_lyrics()
        line = lyrics.create_line_from_string("Hello world! 你好世界！", 10, 50)
        self.assertEqual(len(lyrics._proto.lines), 6)
        MockLyricLine("Hello world! 你好世界！", 10, 50).assert_equal(line)

    def test_remove_line_at_index(self):
        lyrics = create_lyrics()
        lyrics.create_line(11)
        lyrics.create_line(20)
        self.assertEqual(len(lyrics._proto.lines), 7)
        lyrics.remove_line_at_index(5)
        self.assertEqual(len(lyrics._proto.lines), 6)
        lyrics.remove_line_at_index(4)
        lyrics.remove_line_at_index(1)
        lyrics.remove_line_at_index(2)
        lyrics.remove_line_at_index(1)
        self.assertEqual(len(lyrics._proto.lines), 2)
        MockLyricLine("Hello world this is a test.", 10, 50).assert_equal(lyrics.get_line_at_index(0))

    def test_clear(self):
        lyrics = create_lyrics()
        lyrics.create_line(10)
        lyrics.clear()
        self.assertEqual(len(lyrics._proto.lines), 0)


class TestLyricLine(unittest.TestCase):
    def test_create_word(self):
        lyrics = create_lyrics()
        line = lyrics.create_line(10)
        line.create_word("first", 15, 20)
        line.create_word("second", 30, 50)
        self.assertEqual(len(line._proto.words), 2)
        self.assertEqual(line._proto.words[0].word, "first")
        self.assertEqual(line._proto.words[1].word, "second")

    def test_clear(self):
        lyrics = create_lyrics()
        line = lyrics.create_line(10)
        line.create_word("first", 15, 20)
        line.create_word("second", 30, 50)
        line.clear()
        self.assertEqual(len(line._proto.words), 1)
        self.assertEqual(line.is_empty(), True)

    def test_remove_word_at_index(self):
        lyrics = create_lyrics()
        line = lyrics.create_line(9)
        line.create_word("test", 15, 20)
        line.remove_word_at_index(0)
        # There will be 1 placeholder left
        self.assertEqual(len(line._proto.words), 1)
        MockLyricLine("", 15, 15 + 480 * 4 * 2).assert_equal(lyrics.get_line_at_index(0))


class TestLyricWord(unittest.TestCase):
    def test_set_word(self):
        lyrics = create_lyrics()
        line = lyrics.create_line(10)
        word = line._proto.words[0]
        lyric_word = LyricWord(line, "test", 10, 20, word)
        lyric_word.set_word("changed")
        self.assertEqual(lyric_word.get_word(), "changed")

    def test_set_start_tick(self):
        lyrics = create_lyrics()
        line = lyrics.create_line(10)
        word = line._proto.words[0]
        lyric_word = LyricWord(line, "test", 10, 20, word)
        lyric_word.set_start_tick(5)
        self.assertEqual(lyric_word.get_start_tick(), 5)

    def test_move_to(self):
        lyrics = create_lyrics()
        line = lyrics.create_line(10)
        word = line._proto.words[0]
        lyric_word = LyricWord(line, "test", 10, 20, word)
        lyric_word.move_to(5, 15)
        self.assertEqual(lyric_word.get_start_tick(), 5)
        self.assertEqual(lyric_word.get_end_tick(), 15)


if __name__ == '__main__':
    unittest.main()
