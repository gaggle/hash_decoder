from logging import getLogger as _getLogger
from time import time
from typing import Callable, Optional, TYPE_CHECKING as _TYPE_CHECKING

from hashdecoder.exc import HashDecodeError as _HashDecodeError
from hashdecoder.lib.combinations import combinations as _combinations
from hashdecoder.lib.logutil import (
    log_me, log_same_line as _log_same_line,
    log_switch as _log_switch,
)
from hashdecoder.lib.types import hash_type

_log = _getLogger(__name__)

if _TYPE_CHECKING:
    from hashdecoder.lib.dictionary import Dictionary as _Dictionary


class HashDecoder:
    def __init__(self, dictionary: '_Dictionary') -> None:
        self._dictionary = dictionary

    @log_me
    def decode(self, hash_: hash_type,
               hint: Optional[str] = None) -> str:
        return self._decode(hash_, _combinations, hint)

    def _decode(self, hash_: hash_type, get_combinations: Callable,
                hint: Optional[str] = None) -> str:
        lookup = self._lookup(hash_)
        if lookup:
            return lookup

        _log.debug("Decoding %s (hint: %s)", hash_, hint)

        valid_chars = list(hint.replace(' ', '') if hint else [])
        valid_chars = sorted(valid_chars)

        skipped_entries = 0
        total_word_count = self._dictionary.count_words()

        loop_start = -1

        def log_every_nth(i, word):
            nonlocal loop_start
            elapsed_time = time() - loop_start
            if elapsed_time > 1:
                _log_same_line("Processing permutation %s: %s",
                               i, word)
                loop_start = time()

        for index, permutation in enumerate(get_combinations(
                self._dictionary.yield_words,
                total_word_count
        )):
            _log_switch(
                _log,
                info=lambda: log_every_nth(index, permutation),
                debug=lambda: _log.debug("Processing permutation %s: %s",
                                         index, permutation),
            )
            if valid_chars:
                permutation_letters = sorted(permutation.replace(' ', ''))
                if not permutation_letters == valid_chars:
                    continue
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
