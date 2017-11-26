from itertools import permutations
from typing import Iterable


def combinations(iterable: Iterable, count: int) -> Iterable:
    for length in range(2, count + 1):
        for e in permutations(iterable, length):
            yield "".join(e)
