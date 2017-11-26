from hashdecoder.word_repository import MemoryWordRepository


def test_mem_word_repository_yields_content():
    rep = MemoryWordRepository(['a'])
    assert list(rep.yield_words()) == ['a']


def test_mem_word_repository_strips_newlines():
    rep = MemoryWordRepository(['a\n'])
    assert list(rep.yield_words()) == ['a']
