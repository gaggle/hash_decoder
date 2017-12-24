from typing import Iterator, TYPE_CHECKING

from test.helpers import get_db, parametrize_dictionaries, to_md5

if TYPE_CHECKING:
    from hashdecoder.lib.dictionary import Dictionary


@parametrize_dictionaries(get_db())
def test_add_permutation(dictionary: 'Dictionary'):
    dictionary.add_permutation('foo')
    dictionary.add_permutation('bar')
    assert ['bar', 'foo'] == sorted(dictionary.yield_all())


@parametrize_dictionaries(get_db())
def test_add_permutation_is_noop_if_word_exists(dictionary: 'Dictionary'):
    dictionary.add_word('foo')
    dictionary.add_permutation('foo')
    assert list(dictionary.yield_all()) == ['foo']
    assert dictionary.count_words() == 1
    assert 0 == dictionary.count_permutations()


@parametrize_dictionaries(get_db())
def test_add_word(dictionary: 'Dictionary'):
    dictionary.add_word('foo')
    dictionary.add_word('bar')
    assert ['bar', 'foo'] == sorted(dictionary.yield_all())


@parametrize_dictionaries(get_db())
def test_added_words_are_sanitised(dictionary: 'Dictionary'):
    dictionary.add_word('\nfoo\n')
    dictionary.add_permutation('\nbar\n')
    assert ['bar', 'foo'] == sorted(dictionary.yield_all())


@parametrize_dictionaries(get_db())
def test_count_permutations(dictionary: 'Dictionary'):
    dictionary.add_permutation('foo')
    dictionary.add_word('bar')
    assert 1 == dictionary.count_permutations()


@parametrize_dictionaries(get_db())
def test_count_words(dictionary: 'Dictionary'):
    dictionary.add_permutation('foo')
    dictionary.add_word('bar')
    assert 1 == dictionary.count_words()


@parametrize_dictionaries(get_db())
def test_lookup_hash(dictionary: 'Dictionary'):
    dictionary.add_word('foo')
    dictionary.add_permutation('bar')

    assert 'foo' == dictionary.lookup_hash(to_md5('foo'))
    assert 'bar' == dictionary.lookup_hash(to_md5('bar'))


@parametrize_dictionaries(get_db())
def test_lookup_word(dictionary: 'Dictionary'):
    dictionary.add_word('foo')
    dictionary.add_permutation('bar')

    assert to_md5('foo') == dictionary.lookup_word('foo')
    assert to_md5('bar') == dictionary.lookup_word('bar')


@parametrize_dictionaries(get_db())
def test_yield_words(dictionary: 'Dictionary'):
    dictionary.add_word('foo')
    dictionary.add_permutation('bar')
    assert isinstance(dictionary.yield_words(), Iterator)
    assert ('foo',) == tuple(dictionary.yield_words())


@parametrize_dictionaries(get_db())
def test_yield_all(dictionary: 'Dictionary'):
    dictionary.add_word('foo')
    dictionary.add_permutation('bar')
    assert isinstance(dictionary.yield_all(), Iterator)
    assert ('foo', 'bar') == tuple(dictionary.yield_all())


@parametrize_dictionaries(get_db())
def test_hint_narrows_trivial_search(dictionary: 'Dictionary'):
    dictionary.add_word('a')
    dictionary.add_word('b')
    dictionary.add_word('c')
    assert ['a'] == list(dictionary.yield_words(hint='a'))


@parametrize_dictionaries(get_db())
def test_hint_narrows_found_words(dictionary: 'Dictionary'):
    dictionary.add_word('foo')
    dictionary.add_word('bar')
    dictionary.add_word('baz')
    assert ['bar', 'baz'] == list(dictionary.yield_words(hint='aabbrz'))


def _get_words(db):
    cursor = db.cursor()
    cursor.execute('''SELECT word FROM words''')
    return tuple(sorted(e[0] for e in cursor.fetchall()))


def _get_permutations(db):
    cursor = db.cursor()
    cursor.execute('''SELECT word FROM permutations''')
    return tuple(sorted(e[0] for e in cursor.fetchall()))
