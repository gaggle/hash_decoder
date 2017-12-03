from logging import getLogger as _getLogger
from typing import Optional, TYPE_CHECKING as _TYPE_CHECKING

from hashdecoder.custom_types import hash_type
from hashdecoder.exc import HashDecodeError as _HashDecodeError
from hashdecoder.lib.combinations import combinations as _combinations
from hashdecoder.lib.logutil import (
    log_same_line as _log_same_line,
    log_switch as _log_switch,
)

_log = _getLogger(__name__)

if _TYPE_CHECKING:
    from hashdecoder.dictionary import Dictionary as _Dictionary


class HashDecoder:
    def __init__(self, dictionary: '_Dictionary') -> None:
        self._dictionary = dictionary

    def decode(self, hash_: hash_type) -> str:
        lookup = self._lookup(hash_)
        if lookup:
            return lookup

        for permutation in _combinations(self._dictionary.yield_words,
                                         self._dictionary.count_words()):
            _log_switch(
                _log,
                info=lambda: _log_same_line("Processing word: %s", permutation),
                debug=lambda: _log.debug("Processing permutation: %s",
                                         permutation),
            )
            self._dictionary.add_permutation(permutation)
            lookup = self._lookup(hash_)
            if lookup:
                return lookup
        raise _HashDecodeError(hash_)

    def _lookup(self, hash_: str) -> Optional[str]:
        word = self._dictionary.lookup_hash(hash_)
        if word:
            _log_switch(
                _log,
                debug=lambda: _log.debug("Found hash '%s' in %s, maps to '%s'",
                                         hash_, self._dictionary, word),
                info=lambda: _log.info("Found hash '%s', maps to: %s",
                                       hash_, word)
            )
        return word
