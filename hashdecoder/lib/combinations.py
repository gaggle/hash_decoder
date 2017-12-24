from itertools import permutations
from logging import getLogger
from typing import Callable, Iterable

log = getLogger(__name__)


def combinations(get_iterable: Callable[[], Iterable], count: int) -> Iterable:
    for length in range(2, count + 1):
        for e in permutations(get_iterable(), length):
            yield " ".join(e)
