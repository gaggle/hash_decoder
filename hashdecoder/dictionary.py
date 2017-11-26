from abc import ABC, abstractmethod
from hashlib import md5
from logging import getLogger
from typing import (
    Iterator,
    Optional,
)

from hashdecoder.word_repository import WordRepository

log = getLogger(__name__)


class Dictionary(ABC):
    @abstractmethod
    def add_word(self, word) -> None:
        """Add word to dictionary"""
        pass

    @abstractmethod
    def count(self) -> int:
        """Return count of hash/word pairs"""
        pass

    @abstractmethod
    def lookup_hash(self, hash_: str) -> Optional[str]:
        """Return word that corresponds to hash_"""
        pass

    @abstractmethod
    def peek(self, word) -> str:
        pass

    @abstractmethod
    def words(self) -> Iterator[str]:
        """Return iterable of words"""
        pass


class DictionaryImpl(Dictionary):
    def __init__(self, word_repository: WordRepository) -> None:
        self._word_repository = word_repository
        self._hashes_to_words: dict = {}

        for word in word_repository.yield_words():
            self._add_word(word)

    def add_word(self, word) -> None:
        log.debug("Adding word: %s", word)
        return self._add_word(word)

    def count(self) -> int:
        return self._word_repository.count()

    def peek(self, word) -> str:
        return _md5_encode(word)

    def lookup_hash(self, hash_: str) -> Optional[str]:
        return self._hashes_to_words.get(hash_)

    def words(self) -> Iterator[str]:
        for word in self._hashes_to_words.values():
            yield word

    def _add_word(self, word) -> None:
        hash_ = _md5_encode(word)
        self._hashes_to_words[hash_] = word


def _md5_encode(word: str) -> str:
    return md5(word.encode('utf-8')).hexdigest()
