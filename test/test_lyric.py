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


def assert_lyric_words_equal(expected: Dict, actual: LyricWord):
    if expected["word"] != actual.get_word():
        raise Exception(
            f'Lyric words are not equal. Expected word {expected["word"]} but got {actual.get_word()}'
        )
    if expected["start_tick"] != actual.get_start_tick():
        raise Exception(
            f'Lyric words are not equal. Expected start tick {expected["start_tick"]} but got {actual.get_start_tick()}'
        )
    if expected["end_tick"] != actual.get_end_tick():
        raise Exception(
            f'Lyric words are not equal. Expected end tick {expected["end_tick"]} but got {actual.get_end_tick()}'
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
        self.assertEqual(len(lyrics), 5)
        line = lyrics.create_line(660)
        self.assertEqual(len(lyrics), 6)
        self.assertEqual(line.is_empty(), True)
        assert_lyric_lines_equal({"sentence": "", "start_tick": 660, "end_tick": 1140}, line)

    def test_create_line_from_string(self):
        lyrics = create_lyrics()
        self.assertEqual(len(lyrics), 5)
        line = lyrics.create_line_from_string("Hello world! 你好世界！", 10, 50)
        self.assertEqual(len(lyrics), 6)
        assert_lyric_lines_equal({
            "sentence": "Hello world! 你好世界！",
            "start_tick": 10,
            "end_tick": 50
        }, line)
        assert_lyric_words_equal({ "word": "Hello", "start_tick": 10, "end_tick": 14 }, line[0])
        assert_lyric_words_equal({ "word": " ", "start_tick": 14, "end_tick": 18 }, line[1])
        assert_lyric_words_equal({ "word": "world", "start_tick": 18, "end_tick": 22 }, line[2])
        assert_lyric_words_equal({ "word": "!", "start_tick": 22, "end_tick": 26 }, line[3])
        assert_lyric_words_equal({ "word": " ", "start_tick": 26, "end_tick": 30 }, line[4])
        assert_lyric_words_equal({ "word": "你", "start_tick": 30, "end_tick": 34 }, line[5])
        assert_lyric_words_equal({ "word": "好", "start_tick": 34, "end_tick": 38 }, line[6])
        assert_lyric_words_equal({ "word": "世", "start_tick": 38, "end_tick": 42 }, line[7])
        assert_lyric_words_equal({ "word": "界", "start_tick": 42, "end_tick": 46 }, line[8])
        assert_lyric_words_equal({ "word": "！", "start_tick": 46, "end_tick": 50 }, line[9])

    def test_set_words(self):
        lyrics = create_lyrics()
        line = lyrics.create_line(10)
        assert_lyric_lines_equal({
            "sentence": "",
            "start_tick": 10,
            "end_tick": 10 + DEFAULT_PPQ,
        }, lyrics[1])
        # Test updating words without changing the start and end tick
        line.set_words_from_string("Set words from string without movement")
        assert_lyric_lines_equal({
            "sentence": "Set words from string without movement",
            "start_tick": 10,
            "end_tick": 10 + DEFAULT_PPQ,
        }, line)
        # Test updating words and changing the start and end tick
        line.set_words_from_string("Set words from string with movement", 10, 12)
        self.assertEqual(len(line), 11)
        assert_lyric_lines_equal({
            "sentence": "Set words from string with movement",
            "start_tick": 10,
            "end_tick": 12,
        }, line)
        # Test setting words to none
        line.set_words_from_string("")
        assert_lyric_lines_equal({
            "sentence": "",
            "start_tick": 10,
            "end_tick": 10 + DEFAULT_PPQ * 4 * 2,
        }, line)

    def test_remove_line_at_index(self):
        lyrics = create_lyrics()
        self.assertEqual(len(lyrics), 5)
        lyrics.create_line(11)
        lyrics.create_line(20)
        self.assertEqual(len(lyrics), 7)
        lyrics.remove_line_at_index(5)
        self.assertEqual(len(lyrics), 6)
        lyrics.remove_line_at_index(4)
        lyrics.remove_line_at_index(1)
        lyrics.remove_line_at_index(2)
        lyrics.remove_line_at_index(1)
        self.assertEqual(len(lyrics), 2)
        assert_lyric_lines_equal({
            "sentence": "Hello world this is a test.",
            "start_tick": 10,
            "end_tick": 50
        }, lyrics[0])

    def test_remove_line(self):
        lyrics = create_lyrics()
        self.assertEqual(len(lyrics), 5)
        line = lyrics.create_line(50)
        self.assertEqual(len(lyrics), 6)
        lyrics.remove_line(line)
        self.assertEqual(len(lyrics), 5)
        lyrics.remove_line(lyrics[4])
        lyrics.remove_line(lyrics[3])
        lyrics.remove_line(lyrics[2])
        lyrics.remove_line(lyrics[1])
        self.assertEqual(len(lyrics), 1)
        assert_lyric_lines_equal({
            "sentence": "Hello world this is a test.",
            "start_tick": 10,
            "end_tick": 50
        }, lyrics[0])

    def test_clone_line(self):
        lyrics = create_lyrics()
        self.assertEqual(len(lyrics), 5)
        line = lyrics.create_line(300)
        new_line = lyrics.clone_line(line)
        self.assertEqual(len(lyrics), 7)
        # Check the cloned line
        assert_lyric_lines_equal({
            "sentence": "",
            "start_tick": 300,
            "end_tick": 780
        }, new_line)
        # Check if cloned and sorted properly
        assert_lyric_lines_equal({
            "sentence": "",
            "start_tick": 300,
            "end_tick": 780
        }, lyrics[3])
        assert_lyric_lines_equal({
            "sentence": "",
            "start_tick": 300,
            "end_tick": 780
        }, lyrics[4])

    def test_create_word(self):
        lyrics = create_lyrics()
        line = lyrics.create_line(300)
        self.assertEqual(line.is_empty(), True)
        line.create_word("second", 15, 20)
        line.create_word(" ", 13, 15)
        line.create_word("first", 10, 12)
        assert_lyric_lines_equal({
            "sentence": "first second",
            "start_tick": 10,
            "end_tick": 20,
        }, line)
        assert_lyric_words_equal({"word": "first", "start_tick": 10, "end_tick": 12}, line[0])
        assert_lyric_words_equal({"word": " ", "start_tick": 13, "end_tick": 15}, line[1])
        assert_lyric_words_equal({"word": "second", "start_tick": 15, "end_tick": 20}, line[2])

    def test_get_word_at_index(self):
        lyrics = create_lyrics()
        line = lyrics.create_line_from_string("first second", 10, 20)
        assert_lyric_lines_equal({
            "sentence": "first second",
            "start_tick": 10,
            "end_tick": 20,
        }, line)
        assert_lyric_words_equal({"word": "first", "start_tick": 10, "end_tick": 13}, line[0])
        assert_lyric_words_equal({"word": " ", "start_tick": 13, "end_tick": 16}, line[1])
        assert_lyric_words_equal({"word": "second", "start_tick": 16, "end_tick": 20}, line[2])
        assert_lyric_words_equal({"word": "first", "start_tick": 10, "end_tick": 13}, line.get_word_at_index(0))
        assert_lyric_words_equal({"word": " ", "start_tick": 13, "end_tick": 16}, line.get_word_at_index(1))
        assert_lyric_words_equal({"word": "second", "start_tick": 16, "end_tick": 20}, line.get_word_at_index(2))

    def test_get_index_of_word_at_tick(self):
        lyrics = create_lyrics()
        line = lyrics.create_line_from_string("testing get word", 10, 15)
        assert_lyric_lines_equal({
            "sentence": "testing get word",
            "start_tick": 10,
            "end_tick": 15,
        }, line)
        self.assertEqual(line.get_index_of_word_at_tick(10), 0)
        self.assertEqual(line.get_index_of_word_at_tick(11), 1)
        self.assertEqual(line.get_index_of_word_at_tick(12), 2)
        self.assertEqual(line.get_index_of_word_at_tick(13), 3)
        self.assertEqual(line.get_index_of_word_at_tick(14), 4)

    def test_clear(self):
        lyrics = create_lyrics()
        lyrics.create_line(10)
        self.assertEqual(len(lyrics), 6)
        lyrics.clear()
        self.assertEqual(len(lyrics), 0)


class TestLyricLine(unittest.TestCase):
    def test_create_word(self):
        lyrics = create_lyrics()
        line = lyrics.create_line(10)
        self.assertEqual(len(line), 0)
        line.create_word("first", 15, 20)
        line.create_word("second", 30, 50)
        line.create_word(" ", 28, 29)
        self.assertEqual(len(line), 3)
        assert_lyric_words_equal({"word": "first", "start_tick": 15, "end_tick": 20}, line[0])
        assert_lyric_words_equal({"word": " ", "start_tick": 28, "end_tick": 29}, line[1])
        assert_lyric_words_equal({"word": "second", "start_tick": 30, "end_tick": 50}, line[2])
        assert_lyric_lines_equal({
            "sentence": "first second",
            "start_tick": 15,
            "end_tick": 50,
        }, line)

    def test_clear(self):
        lyrics = create_lyrics()
        line = lyrics.create_line(10)
        line.create_word("first", 15, 20)
        line.create_word("second", 30, 50)
        self.assertEqual(len(line), 2)
        line.clear()
        self.assertEqual(len(line), 0)
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
        line.create_word("word", 20, 30)
        # Replace the empty word
        self.assertEqual(len(line), 2)
        assert_lyric_words_equal({
            "word": "test",
            "start_tick": 15,
            "end_tick": 20,
        }, line[0])
        assert_lyric_words_equal({
            "word": "word",
            "start_tick": 20,
            "end_tick": 30,
        }, line[1])
        line.remove_word_at_index(0)
        # There will be 1 placeholder left
        self.assertEqual(len(line), 1)
        assert_lyric_words_equal({
            "word": "word",
            "start_tick": 20,
            "end_tick": 30,
        }, line[0])
        # Test changed order of lines
        assert_lyric_lines_equal({
            "sentence": "word",
            "start_tick": 20,
            "end_tick": 30,
        }, lyrics[1])

    def test_remove_word(self):
        lyrics = create_lyrics()
        line = lyrics.create_line(10)
        word = line.create_word("first", 15, 20)
        line.create_word("second", 30, 50)
        assert_lyric_words_equal({"word": "first", "start_tick": 15, "end_tick": 20}, line[0])
        line.remove_word(word)
        assert_lyric_words_equal({"word": "second", "start_tick": 30, "end_tick": 50}, line[0])
        assert_lyric_lines_equal({
            "sentence": "second",
            "start_tick": 30,
            "end_tick": 50,
        }, lyrics[1])
        self.assertEqual(len(line), 1)


class TestLyricWord(unittest.TestCase):
    def test_set_word(self):
        lyrics = create_lyrics()
        line = lyrics.create_line(10)
        word = line[0]
        word = LyricWord(line, "test", 10, 20, word)
        word.set_word("changed")
        self.assertEqual(word.get_word(), "changed")

    def test_set_start_tick(self):
        lyrics = create_lyrics()
        line = lyrics.create_line(10)
        word = line.create_word("test", 15, 20)
        line.create_word("tick", 30, 50)
        assert_lyric_lines_equal({
            "sentence": "testtick",
            "start_tick": 15,
            "end_tick": 50,
        }, lyrics[1])
        word.set_start_tick(5)
        self.assertEqual(word.get_start_tick(), 5)
        self.assertEqual(line.get_start_tick(), 5)
        # Test if lines are sorted
        assert_lyric_lines_equal({
            "sentence": "testtick",
            "start_tick": 5,
            "end_tick": 50,
        }, lyrics[0])

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
        }, lyrics[1])
    
    def test_set_tick_to_remove_word(self):
        lyrics = create_lyrics()
        line = lyrics.create_line(10)
        word = line.create_word("test", 15, 20)
        assert_lyric_lines_equal({
            "sentence": "test",
            "start_tick": 15,
            "end_tick": 20,
        }, lyrics[1])
        self.assertEqual(len(line), 1)
        word.set_start_tick(20)
        self.assertEqual(len(line), 0)
        assert_lyric_lines_equal({
            "sentence": "",
            "start_tick": 15,
            "end_tick": 15 + DEFAULT_PPQ * 4 * 2,
        }, lyrics[1])
        word = line.create_word("gaga", 15, 20)
        self.assertEqual(len(line), 1)
        assert_lyric_lines_equal({
            "sentence": "gaga",
            "start_tick": 15,
            "end_tick": 20,
        }, lyrics[1])
        word.set_end_tick(15)
        self.assertEqual(len(line), 0)
        assert_lyric_lines_equal({
            "sentence": "",
            "start_tick": 15,
            "end_tick": 15 + DEFAULT_PPQ * 4 * 2, 
        }, lyrics[1])

    def test_move_to_basic(self):
        lyrics = create_lyrics()
        line = lyrics.create_line(10)
        word = line.create_word(word="test", start_tick=5, end_tick=15)
        word.move_to(5, 15)
        self.assertEqual(word.get_start_tick(), 5)
        self.assertEqual(word.get_end_tick(), 15)
        assert_lyric_lines_equal({
            "sentence": "test",
            "start_tick": 5,
            "end_tick": 15
        }, lyrics[0])

    def test_move_to_delete_word(self):
        lyrics = create_lyrics()
        line = lyrics.create_line(10)
        word = line.create_word(word="create", start_tick=40, end_tick=3000)
        self.assertEqual(len(line), 1)
        assert_lyric_lines_equal({
            "sentence": "create",
            "start_tick": 40,
            "end_tick": 3000,
        }, lyrics[1])
        word.move_to(6, 6)
        self.assertEqual(len(line), 0)
        assert_lyric_lines_equal({
            "sentence": "",
            "start_tick": 40,
            "end_tick": 40 + DEFAULT_PPQ * 4 * 2,
        }, lyrics[1])

    def test_move_to_change_line_order(self):
        lyrics = create_lyrics()
        line = lyrics.create_line(10)
        word = line.create_word(word="create", start_tick=1600, end_tick=3000)
        assert_lyric_lines_equal({
            "sentence": "create",
            "start_tick": 1600,
            "end_tick": 3000,
        }, lyrics[5])
        word.move_to(1, 2)
        assert_lyric_lines_equal({
            "sentence": "create",
            "start_tick": 1,
            "end_tick": 2,
        }, lyrics[0])


if __name__ == '__main__':
    unittest.main()
