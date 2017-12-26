from functools import partial

from hashdecoder.lib.combinations import combinations


def test_combinations_yields_count_of_2_as_expected():
    get_words = partial(lambda: iter(['a', 'b']))
    ideal = ['a b', 'b a']
    _assert_generator_contains(
        combinations(get_words, count=2),
        ideal
    )


def test_combinations_yields_count_of_3_as_expected():
    get_words = partial(lambda: iter(['a', 'b', 'c']))
    ideal = [
        'a b', 'a c',
        'b a', 'b c',
        'c a', 'c b',
        'a b c', 'a c b',
        'b a c', 'b c a',
        'c a b', 'c b a',
    ]
    _assert_generator_contains(
        combinations(get_words, count=3),
        ideal
    )


def _assert_generator_contains(iterable, ideal):
    ideal_copy = ideal.copy()
    for entry in iterable:
        ideal_copy.remove(' '.join(entry))
    assert ideal_copy == []
