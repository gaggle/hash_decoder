from contextlib import contextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from io import TextIOWrapper


@contextmanager
def seek_at(file: 'TextIOWrapper', seek=0):
    original_seek = file.tell()
    file.seek(seek)
    try:
        yield file
    finally:
        file.seek(original_seek)
