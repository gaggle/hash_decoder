import typing as _typing

from test.helpers import get_db, parametrise_hashers

if _typing.TYPE_CHECKING:
    from hashdecoder.lib.wordhasher import WordHasher


@parametrise_hashers(get_db())
def test_add_is_noop_if_word_is_present(hasher: 'WordHasher'):
    hasher.add('foo')
    hasher.add('foo')
    assert 1 == hasher.count()
