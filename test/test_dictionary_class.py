from typing import Iterator, TYPE_CHECKING

from test.helpers import get_db, parametrise_dictionaries, to_md5

if TYPE_CHECKING:
    from hashdecoder.lib.dictionary import Dictionary


@parametrise_dictionaries(get_db())
def test_add_initial_word(dictionary: 'Dictionary'):
    dictionary.add_initial_word('foo')
    dictionary.add_initial_word('bar')
    assert ['bar', 'foo'] == sorted(dictionary.yield_all())


@parametrise_dictionaries(get_db())
def test_add_initial_word_is_noop_if_word_exists(dictionary: 'Dictionary'):
    dictionary.add_permutation('foo')
    dictionary.add_initial_word('foo')
    assert ['foo'] == list(dictionary.yield_all())
    assert 0 == dictionary.count_initial_words()
    assert 1 == dictionary.count_permutations()


@parametrise_dictionaries(get_db())
def test_add_initial_word_respects_hint(dictionary: 'Dictionary'):
    hint = 'abf oor'  # foobar
    dictionary.add_initial_word('bar', hint)
    dictionary.add_initial_word('baz', hint)
    assert 1 == dictionary.count_initial_words()


@parametrise_dictionaries(get_db())
def test_add_permutation(dictionary: 'Dictionary'):
    dictionary.add_permutation('foo')
    dictionary.add_permutation('bar')
    assert ['bar', 'foo'] == sorted(dictionary.yield_all())


@parametrise_dictionaries(get_db())
def test_add_permutation_is_noop_if_word_exists(dictionary: 'Dictionary'):
    dictionary.add_initial_word('foo')
    dictionary.add_permutation('foo')
    assert ['foo'] == list(dictionary.yield_all())
    assert 1 == dictionary.count_initial_words()
    assert 0 == dictionary.count_permutations()


@parametrise_dictionaries(get_db())
def test_added_words_are_sanitised(dictionary: 'Dictionary'):
    dictionary.add_initial_word('\nfoo\n')
    dictionary.add_permutation('\nbar\n')
    assert ['bar', 'foo'] == sorted(dictionary.yield_all())


@parametrise_dictionaries(get_db())
def test_clear_clears_data(dictionary: 'Dictionary'):
    dictionary.add_initial_word('foo')
    dictionary.clear()
    assert [] == list(dictionary.yield_all())


@parametrise_dictionaries(get_db())
def test_count_initial_words(dictionary: 'Dictionary'):
    dictionary.add_permutation('foo')
    dictionary.add_initial_word('bar')
    assert 1 == dictionary.count_initial_words()


@parametrise_dictionaries(get_db())
def test_count_permutations(dictionary: 'Dictionary'):
    dictionary.add_permutation('foo')
    dictionary.add_initial_word('bar')
    assert 1 == dictionary.count_permutations()


@parametrise_dictionaries(get_db())
def test_lookup_hash(dictionary: 'Dictionary'):
    dictionary.add_initial_word('foo')
    dictionary.add_permutation('bar')

    assert 'foo' == dictionary.lookup_hash(to_md5('foo'))
    assert 'bar' == dictionary.lookup_hash(to_md5('bar'))


@parametrise_dictionaries(get_db())
def test_yield_all(dictionary: 'Dictionary'):
    dictionary.add_initial_word('foo')
    dictionary.add_permutation('bar')
    assert isinstance(dictionary.yield_all(), Iterator)
    assert ['foo', 'bar'] == list(dictionary.yield_all())


@parametrise_dictionaries(get_db())
def test_yield_all_hint_narrows_trivial_lookup(dictionary: 'Dictionary'):
    dictionary.add_initial_word('a')
    dictionary.add_initial_word('b')
    dictionary.add_initial_word('c')
    assert ['a'] == list(dictionary.yield_all(hint='a'))


@parametrise_dictionaries(get_db())
def test_yield_all_hint_narrows_lookup(dictionary: 'Dictionary'):
    dictionary.add_initial_word('foo')
    dictionary.add_initial_word('bar')
    dictionary.add_initial_word('baz')
    assert ['bar', 'baz'] == list(dictionary.yield_all(
        hint=''.join(sorted('aabbrz'))
    ))


def _get_words(db):
    cursor = db.cursor()
    cursor.execute('''SELECT word FROM words''')
    return tuple(sorted(e[0] for e in cursor.fetchall()))


def _get_permutations(db):
    cursor = db.cursor()
    cursor.execute('''SELECT word FROM permutations''')
    return tuple(sorted(e[0] for e in cursor.fetchall()))
