from functools import partial

from hashdecoder.lib.combinations import combinations


def test_combinations_yields_2_as_expected():
    get_words = partial(lambda: iter(['a', 'b']))
    ideal = ['a b', 'b a']
    _assert_generator_contains(combinations(get_words, count=2), ideal)


def test_combinations_yields_3_as_expected():
    words = partial(lambda: iter(['a', 'b', 'c']))
    count = 3
    ideal = [
        # 'ab', 'ac',
        'a b', 'a c',
        # 'ba', 'bc',
        'b a', 'b c',
        # 'ca', 'cb',
        'c a', 'c b',
        # 'abc', 'acb',
        'a b c', 'a c b',
        # 'bac', 'bca',
        'b a c', 'b c a',
        # 'cab', 'cba',
        'c a b', 'c b a',
    ]
    _assert_generator_contains(combinations(words, count), ideal)


def _assert_generator_contains(iterable, ideal):
    ideal_copy = ideal.copy()
    for entry in iterable:
        ideal_copy.remove(entry)
    assert ideal_copy == []
