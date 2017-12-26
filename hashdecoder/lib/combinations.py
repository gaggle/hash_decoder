import itertools as _itertools
import logging as _logging
import typing as _typing

_log = _logging.getLogger(__name__)


def combinations(get_iterable: _typing.Callable[[], _typing.Iterable],
                 count: int) -> _typing.Iterable:
    _log.debug('Generating permutations up to length %s', count)
    for length in range(2, count + 1):
        for e in _itertools.permutations(get_iterable(), length):
            yield e
