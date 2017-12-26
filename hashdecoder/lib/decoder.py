import logging as _logging
import typing as _typing

import hashdecoder.exc as _exceptions
import hashdecoder.lib.combinations as _combinations
import hashdecoder.lib.types as _types

_log = _logging.getLogger(__name__)

if _typing.TYPE_CHECKING:
    from hashdecoder.lib.dictionary import Dictionary as _Dictionary


class HashDecoder:
    def __init__(self, dictionary: '_Dictionary') -> None:
        self._dictionary = dictionary

    def decode(self, hash_: _types.hash_type,
               hint: _types.hint_type = None) -> str:
        return self._decode(hash_, _combinations.combinations, hint)

    def _decode(self, hash_: _types.hash_type,
                get_combinations: _typing.Callable,
                hint: _types.hint_type = None) -> str:
        lookup = self._lookup(hash_)
        if lookup:
            return lookup

        valid_chars = _sanitise_hint(hint)

        total_word_count = self._dictionary.count_initial_words()

        _log.info("Decoding %s (hint: %s)", hash_, hint)
        for index, permutation in enumerate(get_combinations(
                self._dictionary.yield_all,
                total_word_count
        )):
            _log.debug("Processing permutation %s: %s",
                       index, permutation)
            if valid_chars:
                permutation_letters = ''.join(permutation)
                if not len(permutation_letters) == len(valid_chars):
                    continue
                if not sorted(permutation_letters) == valid_chars:
                    continue
            self._dictionary.add_permutation(' '.join(permutation))
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


def _sanitise_hint(hint: _types.hint_type) -> _typing.List[str]:
    valid_chars = list(hint.replace(' ', '') if hint else [])
    return sorted(valid_chars)
