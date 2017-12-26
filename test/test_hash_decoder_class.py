from hashlib import md5

from pytest import raises

from hashdecoder.exc import HashDecodeError
from hashdecoder.lib.decoder import HashDecoder
from hashdecoder.lib.dictionary import MemDictionary


def to_md5(word: str) -> str:
    return md5(word.encode('utf-8')).hexdigest()


def test_decodes_trivial_lookup():
    decoder = HashDecoder(MemDictionary(['a', 'b', 'c']))
    assert decoder.decode(to_md5('a')) == 'a'


def test_can_decode_2_permutation():
    decoder = HashDecoder(MemDictionary(['a', 'b', 'c']))
    assert decoder.decode(to_md5('a b')) == 'a b'


def test_can_decode_3_permutation():
    decoder = HashDecoder(MemDictionary(['a', 'b', 'c']))

    assert decoder.decode(to_md5('a b c')) == 'a b c'


def test_saves_permutations_to_dictionary():
    dictionary = MemDictionary(['a', 'b', 'c'])
    HashDecoder(dictionary).decode(to_md5('a b c'))
    assert 'a b c' in dictionary.yield_all()
    assert 'a b c' not in dictionary.yield_words()


def test_decode_simple_hint():
    dictionary = MemDictionary(['a', 'b', 'c'])
    with raises(HashDecodeError):
        HashDecoder(dictionary).decode(to_md5('xyz'), hint='bc')
    assert 2 == dictionary.count_permutations()


def test_decode_hint():
    dictionary = MemDictionary(['foo', 'bar', 'baz'])
    result = HashDecoder(dictionary).decode(to_md5('baz bar'), hint='aabbrz')
    assert 'baz bar' in result
    assert 2 == dictionary.count_permutations()
