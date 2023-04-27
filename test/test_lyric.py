import unittest
from typing import Dict
from tuneflow_py.models.song import Song
from tuneflow_py.models.lyric import Lyrics, LyricLine, LyricWord

DEFAULT_PPQ = Song.get_default_resolution()


def assert_lyric_lines_equal(expected: Dict, actual: LyricLine):
    if expected["sentence"] != actual.get_sentence():
        raise Exception(
            f'Lyric lines are not equal. Expected sentence {expected["sentence"]} but got {actual.get_sentence()}'
        )
    if expected["start_tick"] != actual.get_start_tick():
        raise Exception(
            f'Lyric lines are not equal. Expected start tick {expected["start_tick"]} but got {actual.get_start_tick()}'
        )
    if expected["end_tick"] != actual.get_end_tick():
        raise Exception(
            f'Lyric lines are not equal. Expected end tick {expected["end_tick"]} but got {actual.get_end_tick()}'
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
        assert_lyric_lines_equal({"sentence": "", "start_tick": 660, "end_tick": 1140}, line)

    def test_create_line_from_string(self):
        lyrics = create_lyrics()
        line = lyrics.create_line_from_string("Hello world! 你好世界！", 10, 50)
        self.assertEqual(len(lyrics._proto.lines), 6)
        assert_lyric_lines_equal({
            "sentence": "Hello world! 你好世界！",
            "start_tick": 10,
            "end_tick": 50
        }, line)

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
        assert_lyric_lines_equal({
            "sentence": "Hello world this is a test.",
            "start_tick": 10,
            "end_tick": 50
        }, lyrics.get_line_at_index(0))
        
    def test_clone_line(self):
        lyrics = create_lyrics()
        line = lyrics.create_line(300)
        lyrics.clone_line(line)
        self.assertEqual(len(lyrics._proto.lines), 7)
        assert_lyric_lines_equal({
            "sentence": "",
            "start_tick": 300,
            "end_tick": 780
        }, lyrics.get_line_at_index(3))
        assert_lyric_lines_equal({
            "sentence": "",
            "start_tick": 300,
            "end_tick": 780
        }, lyrics.get_line_at_index(4))

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

    def test_get_index_of_line_at_tick(self):
        lyrics = create_lyrics()
        lyrics.create_line(10)
        lyrics.create_line(20)
        index_generator = lyrics.get_index_of_line_at_tick(10)
        self.assertEqual(next(index_generator), 1)
        self.assertEqual(next(index_generator), 0)

    def test_remove_word_at_index(self):
        lyrics = create_lyrics()
        line = lyrics.create_line(9)
        line.create_word("test", 15, 20)
        # Replace the empty word
        self.assertEqual(len(line._proto.words), 1)
        line.remove_word_at_index(0)
        # There will be 1 placeholder left
        self.assertEqual(len(line._proto.words), 1)
        assert_lyric_lines_equal({
            "sentence": "",
            "start_tick": 15,
            "end_tick": 15 + DEFAULT_PPQ * 4 * 2
        }, lyrics.get_line_at_index(1))

    def test_remove_word(self):
        lyrics = create_lyrics()
        line = lyrics.create_line(10)
        word = line.create_word("first", 15, 20)
        line.remove_word(word)
        self.assertEqual(len(line._proto.words), 1)
        self.assertEqual(line.is_empty(), True)


class TestLyricWord(unittest.TestCase):
    def test_set_word(self):
        lyrics = create_lyrics()
        line = lyrics.create_line(10)
        word = line._proto.words[0]
        word = LyricWord(line, "test", 10, 20, word)
        word.set_word("changed")
        self.assertEqual(word.get_word(), "changed")

    def test_set_start_tick(self):
        lyrics = create_lyrics()
        line = lyrics.create_line(10)
        word = line.create_word("test", 15, 20)
        word.set_start_tick(5)
        self.assertEqual(word.get_start_tick(), 5)
        self.assertEqual(line.get_start_tick(), 5)
        
    def test_set_end_tick(self):
        lyrics = create_lyrics()
        line = lyrics.create_line(20)
        word = line.create_word("test", 15, 20)
        word.set_end_tick(30)
        self.assertEqual(word.get_end_tick(), 30)
        assert_lyric_lines_equal({
            "sentence": "test",
            "start_tick": 15,
            "end_tick": 30
        }, lyrics.get_line_at_index(1))

    def test_move_to(self):
        lyrics = create_lyrics()
        line = lyrics.create_line(10)
        word = line._proto.words[0]
        word = LyricWord(line=line, proto=word)
        word.move_to(5, 15)
        self.assertEqual(word.get_start_tick(), 5)
        self.assertEqual(word.get_end_tick(), 15)
        assert_lyric_lines_equal({
            "sentence": "",
            "start_tick": 5,
            "end_tick":15 
        }, lyrics.get_line_at_index(0))


if __name__ == '__main__':
    unittest.main()
