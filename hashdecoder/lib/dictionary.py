import abc as _abc
import itertools as _itertools
import logging as _logging
import typing as _typing

import hashdecoder.lib.types as _types
import hashdecoder.lib.wordhasher as _wordhasher

if _typing.TYPE_CHECKING:
    import sqlite3

_log = _logging.getLogger(__name__)


def get_mem_dictionary(words=None):
    class MemDictionary(Dictionary):
        pass

    return MemDictionary(_wordhasher.MemWordHasher(words or ()),
                         _wordhasher.MemWordHasher())


def get_db_dictionary(db: 'sqlite3.Connection'):
    class DBDictionary(Dictionary):
        pass

    return DBDictionary(_wordhasher.DBWordHasher(db, 'words'),
                        _wordhasher.DBWordHasher(db, 'permutations'))


class Dictionary(_abc.ABC):
    def __init__(self,
                 initial_words: '_wordhasher.WordHasher',
                 permutations: '_wordhasher.WordHasher') -> None:
        self._initial_words = initial_words
        self._permutations = permutations

    def add_initial_word(self, word: str,
                         hint: _types.hint_type = None) -> None:
        if not self._can_add_word(word, hint):
            return
        return self._initial_words.add(word)

    def add_permutation(self, word: str,
                        hint: _types.hint_type = None) -> None:
        if not self._can_add_word(word, hint):
            return
        return self._permutations.add(word)

    def clear(self):
        self._permutations.clear()
        self._initial_words.clear()

    def count_initial_words(self) -> int:
        return self._initial_words.count()

    def count_permutations(self) -> int:
        return self._permutations.count()

    def lookup_hash(self, hash_: _types.hash_type) -> _typing.Optional[str]:
        """Return word that corresponds to hash"""
        return (self._initial_words.lookup_hash(hash_) or
                self._permutations.lookup_hash(hash_))

    def yield_all(self,
                  hint: _types.hint_type = None) -> _typing.Iterator[str]:
        """Iterate over all words"""
        for word in _itertools.chain(self._initial_words.values(),
                                     self._permutations.values()):
            if not _word_is_subset_of_hint(word, hint):
                continue
            yield word

    def _can_add_word(self, word: str,
                      hint: _types.hint_type = None) -> bool:
        if not _word_is_subset_of_hint(word, hint):
            return False

        if (self._initial_words.lookup_word(word) or
                self._permutations.lookup_word(word)):
            return False
        return True


def _word_is_subset_of_hint(entry, hint):
    if not hint:
        return True
    valid_chars = set(hint or [])
    if ' ' in valid_chars:
        valid_chars.remove(' ')

    if all((c in valid_chars) for c in entry):
        return True
    return False
