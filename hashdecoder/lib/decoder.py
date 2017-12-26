import logging as _logging
import typing as _typing

import hashdecoder.exc as _exceptions
import hashdecoder.lib.combinations as _combinations
import hashdecoder.lib.logutil as _logutil
import hashdecoder.lib.types as _types

_log = _logging.getLogger(__name__)

if _typing.TYPE_CHECKING:
    from hashdecoder.lib.dictionary import Dictionary as _Dictionary


class HashDecoder:
    def __init__(self, dictionary: '_Dictionary') -> None:
        self._dictionary = dictionary

    def decode(self, hash_: _types.hash_type,
               hint: _typing.Optional[str] = None) -> str:
        return self._decode(hash_, _combinations.combinations, hint)

    def _decode(self, hash_: _types.hash_type,
                get_combinations: _typing.Callable,
                hint: _typing.Optional[str] = None) -> str:
        lookup = self._lookup(hash_)
        if lookup:
            return lookup

        _log.debug("Decoding %s (hint: %s)", hash_, hint)

        valid_chars = list(hint.replace(' ', '') if hint else [])
        valid_chars = sorted(valid_chars)

        total_word_count = self._dictionary.count_words()

        for index, permutation in enumerate(get_combinations(
                self._dictionary.yield_words,
                total_word_count
        )):
            _logutil.throttled_log(_log.info, 'Processing permutation %s: %s',
                                   index, permutation)
            _log.debug("Processing permutation %s: %s",
                       index, permutation)
            if valid_chars:
                permutation_letters = sorted(permutation.replace(' ', ''))
                if not permutation_letters == valid_chars:
                    continue
            self._dictionary.add_permutation(permutation)
            lookup = self._lookup(hash_)
            if lookup:
                return lookup
        raise _exceptions.HashDecodeError(hash_)

    def _lookup(self, hash_: _types.hash_type) -> _typing.Optional[str]:
        word = self._dictionary.lookup_hash(hash_)
        if word:
            _log.debug("Found hash '%s' in %s, maps to '%s'",
                       hash_, self._dictionary, word)
        return word
