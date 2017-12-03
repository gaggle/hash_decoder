import typing
from abc import ABC, abstractmethod
from enum import Enum
from logging import getLogger

from hashdecoder.lib.hashutil import md5_encode
from hashdecoder.lib.types import hash_type, iterator_or_sequence_type

if typing.TYPE_CHECKING:
    import sqlite3
log = getLogger(__name__)


class Dictionary(ABC):
    @abstractmethod
    @abstractmethod
    def add_permutation(self, word: str) -> None:
        """Add word-permutation to dictionary"""
        pass

    def add_word(self, word: str) -> None:
        """Add core word to dictionary"""
        pass

    @abstractmethod
    def count_permutations(self) -> int:
        """Return count of permutations"""
        pass

    @abstractmethod
    def count_words(self) -> int:
        """Return count of words"""
        pass

    @abstractmethod
    def lookup_hash(self, hash_: hash_type) -> typing.Optional[str]:
        """Return word that corresponds to hash"""
        pass

    @abstractmethod
    def lookup_word(self, word: str) -> typing.Optional[hash_type]:
        """Return hash that corresponds to word"""
        pass

    @abstractmethod
    def yield_all(self) -> typing.Iterator[str]:
        """Iterate through all words"""
        pass

    @abstractmethod
    def yield_words(self) -> typing.Iterator[str]:
        """Iterate through words"""
        pass


class MemDictionary(Dictionary):
    def __init__(self, words: iterator_or_sequence_type = ()) -> None:
        self._words: dict = {}
        self._permutations: dict = {}
        for word in words:
            self.add_word(word)

    def add_permutation(self, word: str) -> None:
        word = _sanitise_word(word)
        if self.lookup_word(word) is not None:
            return
        self._permutations[md5_encode(word)] = word

    def add_word(self, word: str) -> None:
        word = _sanitise_word(word)
        self._words[md5_encode(word)] = word

    def count_permutations(self) -> int:
        return len(self._permutations.keys())

    def count_words(self) -> int:
        return len(self._words.keys())

    def lookup_hash(self, hash_: hash_type) -> typing.Optional[str]:
        entries = {**self._permutations, **self._words}
        return entries.get(hash_)

    def lookup_word(self, word: str) -> typing.Optional[hash_type]:
        entries = {**self._permutations, **self._words}
        for h, w in entries.items():
            if w == word:
                return h
        return None

    def yield_all(self) -> typing.Iterator[str]:
        entries = {**self._words, **self._permutations}
        for word in entries.values():
            yield word

    def yield_words(self) -> typing.Iterator[str]:
        for word in self._words.values():
            yield word


class DBDictionary(Dictionary):
    Table = Enum('Table', 'words permutations')

    def __init__(self, db: 'sqlite3.Connection') -> None:
        self._db = db
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS words(
            hash TEXT PRIMARY KEY, word TEXT UNIQUE)
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS permutations(
            hash TEXT PRIMARY KEY, word TEXT UNIQUE)
        ''')
        db.commit()

    def drop(self):
        for table in ['words', 'permutations']:
            self._db.executescript('drop table if exists {}'.format(table))

    def add_permutation(self, word: str) -> None:
        word = _sanitise_word(word)
        if self.lookup_word(word) is not None:
            return
        cursor = self._db.cursor()
        log.debug("Adding permutation: '%s'", word)
        self._add(cursor, word, self.Table.permutations)
        self._db.commit()

    def add_word(self, word: str) -> None:
        word = _sanitise_word(word)
        cursor = self._db.cursor()
        log.debug("Adding word: %s", word)
        self._add(cursor, word, self.Table.words)
        self._db.commit()

    def count_permutations(self) -> int:
        cursor = self._db.cursor()
        self._count(cursor, self.Table.permutations)
        return cursor.fetchone()[0]

    def count_words(self) -> int:
        cursor = self._db.cursor()
        self._count(cursor, self.Table.words)
        return cursor.fetchone()[0]

    def lookup_hash(self, hash_: str) -> typing.Optional[str]:
        cursor = self._db.cursor()
        cursor.execute(
            'SELECT word FROM words WHERE hash LIKE ? '
            'UNION '
            'SELECT word FROM permutations WHERE hash LIKE ?',
            (hash_, hash_))
        fetchone = cursor.fetchone()
        return fetchone[0] if fetchone else fetchone

    def lookup_word(self, word: str) -> typing.Optional[str]:
        cursor = self._db.cursor()
        cursor.execute(
            'SELECT hash FROM words WHERE word LIKE ? '
            'UNION '
            'SELECT hash FROM permutations WHERE word LIKE ?',
            (word, word))
        fetchone = cursor.fetchone()
        return fetchone[0] if fetchone else fetchone

    def yield_all(self) -> typing.Iterator[str]:
        for row in self._db.cursor().execute(
                'SELECT word FROM words '
                'UNION '
                'SELECT word FROM permutations ORDER BY word DESC'):
            yield row[0]

    def yield_words(self) -> typing.Iterator[str]:
        for row in self._db.cursor().execute('SELECT word FROM words'):
            yield row[0]

    def _add(self, cursor: 'sqlite3.Cursor', word: str,
             table: Table) -> None:
        hash_ = md5_encode(word)
        table_name = self.Table[table.name].name
        query = '''INSERT OR IGNORE INTO {} (hash, word) VALUES (?, ?)'''.format(
            table_name)
        cursor.execute(query, (hash_, word))

    def _count(self, cursor: 'sqlite3.Cursor',
               table: Table) -> None:
        table_name = self.Table[table.name].name
        query = 'SELECT COUNT(*) FROM {}'.format(table_name)
        cursor.execute(query)


def _flatten(iterator: typing.Iterator) -> list:
    return [item for sublist in iterator for item in sublist]


def _sanitise_word(word: str) -> str:
    return word.strip()
