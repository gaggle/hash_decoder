from logging import getLogger
from typing import TYPE_CHECKING

from hashdecoder.combinations import combinations
from hashdecoder.exc import HashDecodeError
from hashdecoder.logutil import log_same_line, log_switch

log = getLogger(__name__)

if TYPE_CHECKING:
    from hashdecoder.dictionary import Dictionary


class HashDecoder:
    def __init__(self, dictionary: 'Dictionary') -> None:
        self._dictionary = dictionary

    def decode(self, hash_: str) -> str:
        lookup = self._lookup(hash_)
        if lookup:
            return lookup

        for permutation in combinations(self._dictionary.words,
                                        self._dictionary.count()):
            log_switch(
                log,
                info=lambda: log_same_line("Processing word: %s", permutation),
                debug=lambda: log.debug("Processing permutation of length %s",
                                        len(permutation)),
            )
            if self._dictionary.peek(permutation) == hash_:
                return permutation
                # self._dictionary.add_word(permutation)
                # lookup = self._lookup(hash_)
                # if lookup:
                #     return lookup
        raise HashDecodeError(hash_)

    def _lookup(self, hash_):
        word = self._dictionary.lookup_hash(hash_)
        if word:
            log_switch(
                log,
                debug=lambda: log.debug("Found hash '%s' in %s, maps to '%s'",
                                        hash_, self._dictionary, word),
                info=lambda: log.info("Found hash '%s', maps to: %s",
                                      hash_, word)
            )
            return word
