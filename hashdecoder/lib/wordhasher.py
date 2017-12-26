import abc as _abc
import logging as _logging
import typing as _typing

import hashdecoder.lib.hashutil as _hashutil
import hashdecoder.lib.types as _types

if _typing.TYPE_CHECKING:
    import sqlite3

_log = _logging.getLogger(__name__)


class WordHasher(_abc.ABC):
    @_abc.abstractmethod
    def add(self, word: str):
        pass

    @_abc.abstractmethod
    def count(self) -> int:
        pass

    @_abc.abstractmethod
    def lookup_hash(self, hash_: _types.hash_type) -> _typing.Optional[str]:
        pass

    @_abc.abstractmethod
    def lookup_word(self, word: str) -> _types.hash_type:
        pass

    @_abc.abstractmethod
    def values(self) -> _typing.Iterator[str]:
        pass

    @_abc.abstractmethod
    def clear(self):
        pass


class MemWordHasher(WordHasher):
    def __init__(self, words: _types.iterator_or_sequence_type = ()) -> None:
        self._storage: dict = {}
        [self.add(w) for w in words]

    def add(self, word: str) -> None:
        word = _sanitise_word(word)
        hashed = _hashutil.md5_encode(word)
        if hashed in self._storage:
            return
        self._storage[hashed] = word

    def count(self) -> int:
        return len(self._storage.keys())

    def lookup_hash(self, hash_: _types.hash_type) -> _typing.Optional[str]:
        return self._storage.get(hash_)

    def lookup_word(self, word: str) -> _types.hash_type:
        for stored_hash, stored_word in self._storage.items():
            if word == stored_word:
                return stored_hash

    def values(self) -> _typing.Iterator[str]:
        for word in self._storage.values():
            yield word

    def clear(self):
        self._storage.clear()


class DBWordHasher(WordHasher):
    def __init__(self, db: 'sqlite3.Connection', table_name: str) -> None:
        self._db = db
        self._table_name = table_name
        self._init_table()

    def add(self, word: str) -> None:
        word = _sanitise_word(word)
        if self.lookup_word(word) is not None:
            return

        cursor = self._db.cursor()
        _log.debug("Adding to '%s': %s", self._table_name, word)
        hash_ = _hashutil.md5_encode(word)
        query = f'''
            INSERT OR IGNORE INTO {self._table_name} 
            (hash, word) VALUES (?, ?)
        '''
        cursor.execute(query, (hash_, word))
        self._db.commit()

    def count(self) -> int:
        cursor = self._db.cursor()
        query = f'SELECT COUNT(*) FROM {self._table_name}'
        cursor.execute(query)
        return cursor.fetchone()[0]

    def lookup_hash(self, hash_: _types.hash_type) -> _typing.Optional[str]:
        cursor = self._db.cursor()
        cursor.execute(
            f'SELECT word FROM {self._table_name} WHERE hash LIKE ?', [hash_])
        fetchone = cursor.fetchone()
        return fetchone[0] if fetchone else fetchone

    def lookup_word(self, word):
        cursor = self._db.cursor()
        cursor.execute(
            f'SELECT hash FROM {self._table_name} WHERE word LIKE ? ', [word])
        fetchone = cursor.fetchone()
        return fetchone[0] if fetchone else fetchone

    def values(self) -> _typing.Iterator[str]:
        query = f'SELECT word FROM {self._table_name}'
        for row in self._db.cursor().execute(query):
            yield row[0]

    def clear(self):
        self._db.executescript(
            'DROP TABLE IF EXISTS {}'.format(self._table_name))
        self._init_table()

    def _init_table(self):
        cursor = self._db.cursor()
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {self._table_name}(
            hash TEXT PRIMARY KEY, 
            word TEXT UNIQUE
        )
        ''')
        self._db.commit()


def _sanitise_word(word: str) -> str:
    return word.strip()
