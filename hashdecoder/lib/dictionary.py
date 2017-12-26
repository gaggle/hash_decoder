import abc as _abc
import enum as _enum
import logging as _logging
import typing as _typing

import hashdecoder.lib.hashutil as _hashutil
import hashdecoder.lib.types as _types

if _typing.TYPE_CHECKING:
    import sqlite3

_log = _logging.getLogger(__name__)


class Dictionary(_abc.ABC):
    @_abc.abstractmethod
    def add_permutation(self, word: str) -> None:
        """Add word-permutation to dictionary"""
        pass

    @_abc.abstractmethod
    def add_word(self, word: str, hint: _typing.Optional[str] = None) -> None:
        """Add core word to dictionary"""
        pass

    @_abc.abstractmethod
    def count_permutations(self) -> int:
        """Return count of permutations"""
        pass

    @_abc.abstractmethod
    def count_words(self) -> int:
        """Return count of words"""
        pass

    @_abc.abstractmethod
    def lookup_hash(self, hash_: _types.hash_type) -> _typing.Optional[str]:
        """Return word that corresponds to hash"""
        pass

    @_abc.abstractmethod
    def lookup_word(self, word: str) -> _typing.Optional[_types.hash_type]:
        """Return hash that corresponds to word"""
        pass

    @_abc.abstractmethod
    def yield_all(self) -> _typing.Iterator[str]:
        """Iterate through all words"""
        pass

    @_abc.abstractmethod
    def yield_words(
            self,
            hint: _typing.Optional[str] = None
    ) -> _typing.Iterator[str]:
        """Iterate through words"""
        pass


class MemDictionary(Dictionary):
    def __init__(self, words: _types.iterator_or_sequence_type = ()) -> None:
        self._words: dict = {}
        self._permutations: dict = {}
        for word in words:
            self.add_word(word)

    def add_permutation(self, word: str) -> None:
        word = _sanitise_word(word)
        if self.lookup_word(word) is not None:
            return
        self._permutations[_hashutil.md5_encode(word)] = word

    def add_word(self, word: str, hint: _typing.Optional[str] = None) -> None:
        word = _sanitise_word(word)
        if hint and not _word_is_subset_of_hint(word, hint):
            return
        self._words[_hashutil.md5_encode(word)] = word

    def count_permutations(self) -> int:
        return len(self._permutations.keys())

    def count_words(self) -> int:
        return len(self._words.keys())

    def lookup_hash(self, hash_: _types.hash_type) -> _typing.Optional[str]:
        entries = {**self._permutations, **self._words}
        return entries.get(hash_)

    def lookup_word(self, word: str) -> _typing.Optional[_types.hash_type]:
        entries = {**self._permutations, **self._words}
        for h, w in entries.items():
            if w == word:
                return h
        return None

    def yield_all(self) -> _typing.Iterator[str]:
        entries = {**self._words, **self._permutations}
        for word in entries.values():
            yield word

    def yield_words(
            self,
            hint: _typing.Optional[str] = None
    ) -> _typing.Iterator[str]:

        for word in self._words.values():
            if hint and not any(c in word for c in hint):
                continue
            yield word


class DBDictionary(Dictionary):
    Table = _enum.Enum('Table', 'words permutations')

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

    def drop(self) -> None:
        for e in self.Table:
            table_name = e.name
            self._db.executescript('drop table if exists {}'.format(table_name))

    def add_permutation(self, word: str) -> None:
        word = _sanitise_word(word)
        if self.lookup_word(word) is not None:
            return
        cursor = self._db.cursor()
        _log.debug("Adding permutation: '%s'", word)
        self._add(cursor, word, self.Table.permutations)
        self._db.commit()

    def add_word(self, word: str, hint: _typing.Optional[str] = None) -> None:
        word = _sanitise_word(word)
        if hint and not _word_is_subset_of_hint(word, hint):
            return
        cursor = self._db.cursor()
        _log.debug("Adding word: %s", word)
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

    def lookup_hash(self, hash_: _types.hash_type) -> _typing.Optional[str]:
        cursor = self._db.cursor()
        cursor.execute(
            'SELECT word FROM words WHERE hash LIKE ? '
            'UNION '
            'SELECT word FROM permutations WHERE hash LIKE ?',
            (hash_, hash_))
        fetchone = cursor.fetchone()
        return fetchone[0] if fetchone else fetchone

    def lookup_word(self, word: str) -> _typing.Optional[str]:
        cursor = self._db.cursor()
        cursor.execute(
            'SELECT hash FROM words WHERE word LIKE ? '
            'UNION '
            'SELECT hash FROM permutations WHERE word LIKE ?',
            (word, word))
        fetchone = cursor.fetchone()
        return fetchone[0] if fetchone else fetchone

    def yield_all(self) -> _typing.Iterator[str]:
        for row in self._db.cursor().execute(
                'SELECT word FROM words '
                'UNION '
                'SELECT word FROM permutations ORDER BY word DESC'):
            yield row[0]

    def yield_words(
            self,
            hint: _typing.Optional[str] = None
    ) -> _typing.Iterator[str]:
        query = "SELECT word FROM words"
        if hint:
            query += " WHERE word LIKE '%{}%'".format(hint[0])
            query += "".join(
                [" OR word LIKE '%{}%'".format(s) for s in hint[1:]])
        for row in self._db.cursor().execute(query):
            yield row[0]

    def _add(self, cursor: 'sqlite3.Cursor', word: str,
             table: Table) -> None:
        hash_ = _hashutil.md5_encode(word)
        table_name = self.Table[table.name].name
        query = '''INSERT OR IGNORE INTO {} (hash, word) VALUES (?, ?)'''.format(
            table_name)
        cursor.execute(query, (hash_, word))

    def _count(self, cursor: 'sqlite3.Cursor',
               table: Table) -> None:
        table_name = self.Table[table.name].name
        query = 'SELECT COUNT(*) FROM {}'.format(table_name)
        cursor.execute(query)


def _sanitise_word(word: str) -> str:
    return word.strip()


def _word_is_subset_of_hint(entry, hint):
    valid_chars = set(hint or [])
    if ' ' in valid_chars:
        valid_chars.remove(' ')

    if all((c in valid_chars) for c in entry):
        return True
    return False
