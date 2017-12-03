from hashlib import md5
from sqlite3 import connect
from typing import Iterator, TYPE_CHECKING

from pytest import mark

from hashdecoder.dictionary import DBDictionary, MemDictionary

if TYPE_CHECKING:
    from hashdecoder.dictionary import Dictionary


def get_db():
    return connect(":memory:")


parametrize_dictionaries = lambda db: mark.parametrize("dictionary", [
    (DBDictionary(db)), (MemDictionary())
], ids=lambda x: type(x).__name__)


@parametrize_dictionaries(get_db())
def test_add_permutation(dictionary: 'Dictionary'):
    dictionary.add_permutation('foo')
    dictionary.add_permutation('bar')
    assert sorted(dictionary.yield_all()) == ['bar', 'foo']


@parametrize_dictionaries(get_db())
def test_add_permutation_is_noop_if_word_exists(dictionary: 'Dictionary'):
    dictionary.add_word('foo')
    dictionary.add_permutation('foo')
    assert list(dictionary.yield_all()) == ['foo']
    assert dictionary.count_words() == 1
    assert dictionary.count_permutations() == 0


@parametrize_dictionaries(get_db())
def test_add_word(dictionary: 'Dictionary'):
    dictionary.add_word('foo')
    dictionary.add_word('bar')
    assert sorted(dictionary.yield_all()) == ['bar', 'foo']


@parametrize_dictionaries(get_db())
def test_added_words_are_sanitised(dictionary: 'Dictionary'):
    dictionary.add_word('\nfoo\n')
    dictionary.add_permutation('\nbar\n')
    assert sorted(dictionary.yield_all()) == ['bar', 'foo']


@parametrize_dictionaries(get_db())
def test_count_permutations(dictionary: 'Dictionary'):
    dictionary.add_permutation('foo')
    dictionary.add_word('bar')
    assert dictionary.count_permutations() == 1


@parametrize_dictionaries(get_db())
def test_count_words(dictionary: 'Dictionary'):
    dictionary.add_permutation('foo')
    dictionary.add_word('bar')
    assert dictionary.count_words() == 1


@parametrize_dictionaries(get_db())
def test_lookup_hash(dictionary: 'Dictionary'):
    dictionary.add_word('foo')
    dictionary.add_permutation('bar')

    assert dictionary.lookup_hash(to_md5('foo')) == 'foo'
    assert dictionary.lookup_hash(to_md5('bar')) == 'bar'


@parametrize_dictionaries(get_db())
def test_lookup_word(dictionary: 'Dictionary'):
    dictionary.add_word('foo')
    dictionary.add_permutation('bar')

    assert dictionary.lookup_word('foo') == to_md5('foo')
    assert dictionary.lookup_word('bar') == to_md5('bar')


@parametrize_dictionaries(get_db())
def test_yield_words(dictionary: 'Dictionary'):
    dictionary.add_word('foo')
    dictionary.add_permutation('bar')
    assert isinstance(dictionary.yield_words(), Iterator)
    assert tuple(dictionary.yield_words()) == ('foo',)


@parametrize_dictionaries(get_db())
def test_yield_all(dictionary: 'Dictionary'):
    dictionary.add_word('foo')
    dictionary.add_permutation('bar')
    assert isinstance(dictionary.yield_all(), Iterator)
    assert tuple(dictionary.yield_all()) == ('foo', 'bar')


def _get_words(db):
    cursor = db.cursor()
    cursor.execute('''SELECT word FROM words''')
    return tuple(sorted(e[0] for e in cursor.fetchall()))


def _get_permutations(db):
    cursor = db.cursor()
    cursor.execute('''SELECT word FROM permutations''')
    return tuple(sorted(e[0] for e in cursor.fetchall()))


def to_md5(word: str) -> str:
    return md5(word.encode('utf-8')).hexdigest()
