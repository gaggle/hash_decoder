from hashlib import md5

from hashdecoder.decoder import HashDecoder
from hashdecoder.dictionary import DictionaryImpl
from hashdecoder.word_repository import MemoryWordRepository


def to_md5(word: str) -> str:
    return md5(word.encode('utf-8')).hexdigest()


def test_decodes_trivial_lookup():
    decoder = HashDecoder(
        DictionaryImpl(
            MemoryWordRepository(['a', 'b', 'c'])
        )
    )

    assert decoder.decode(to_md5('a')) == 'a'


def test_can_decode_2_permutation():
    decoder = HashDecoder(
        DictionaryImpl(
            MemoryWordRepository(['a', 'b', 'c'])
        )
    )

    assert decoder.decode(to_md5('ab')) == 'ab'


def test_can_decode_3_permutation():
    decoder = HashDecoder(
        DictionaryImpl(
            MemoryWordRepository(['a', 'b', 'c'])
        )
    )

    assert decoder.decode(to_md5('abc')) == 'abc'
