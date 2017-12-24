from hashlib import md5
from sqlite3 import connect

from pytest import mark

from hashdecoder.lib.dictionary import DBDictionary, MemDictionary


def get_db():
    return connect(":memory:")


def parametrize_dictionaries(db):
    return mark.parametrize(
        "dictionary",
        [(DBDictionary(db)), (MemDictionary())],
        ids=lambda x: type(x).__name__
    )


def to_md5(word: str) -> str:
    return md5(word.encode('utf-8')).hexdigest()
