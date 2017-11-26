from abc import ABC, abstractmethod
from typing import Iterator


class WordRepository(ABC):
    @abstractmethod
    def count(self) -> int:
        pass

    @abstractmethod
    def yield_words(self) -> Iterator[str]:
        pass


class MemoryWordRepository(WordRepository):
    def __init__(self, words: list) -> None:
        self._words = words

    def count(self) -> int:
        return len(self._words)

    def yield_words(self) -> Iterator[str]:
        for word in self._words:
            yield _sanitise(word)


class FilePathWordRepository(WordRepository):
    def __init__(self, path: str) -> None:
        self._origin_path = path

    def count(self) -> int:
        count = 0
        with open(self._origin_path, 'r') as f:
            for _ in f.readlines():
                count += 1
        return count

    def yield_words(self) -> Iterator[str]:
        with open(self._origin_path, 'r') as f:
            while True:
                word = f.readline()
                if word == '':
                    break
                yield _sanitise(word)


def _sanitise(word: str) -> str:
    return word.rstrip('\n')
