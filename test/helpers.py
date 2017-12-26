from hashlib import md5
from sqlite3 import connect

from pytest import mark

from hashdecoder.lib.dictionary import get_db_dictionary, get_mem_dictionary
from hashdecoder.lib.wordhasher import DBWordHasher, MemWordHasher


def get_db():
    return connect(":memory:")


def parametrise_dictionaries(db):
    return mark.parametrize(
        "dictionary",
        [
            get_mem_dictionary(),
            get_db_dictionary(db),
        ],
        ids=lambda x: type(x).__name__
    )


def parametrise_hashers(db):
    return mark.parametrize(
        "hasher",
        [
            MemWordHasher(),
            DBWordHasher(db, 'test'),
        ],
        ids=lambda x: type(x).__name__
    )


def to_md5(word: str) -> str:
    return md5(word.encode('utf-8')).hexdigest()
