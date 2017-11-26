from hashdecoder.combinations import combinations


def test_combinations_yields_2_as_expected():
    words = ['a', 'b']
    ideal = ['ab', 'ba']
    _assert_generator_contains(combinations(words, len(words)), ideal)


def test_combinations_yields_3_as_expected():
    words = ['a', 'b', 'c']
    ideal = [
        'ab', 'ac',
        'ba', 'bc',
        'ca', 'cb',
        'abc', 'acb',
        'bac', 'bca',
        'cab', 'cba',
    ]
    _assert_generator_contains(combinations(words, len(words)), ideal)


def _assert_generator_contains(iterable, ideal):
    ideal_copy = ideal.copy()
    for entry in iterable:
        ideal_copy.remove(entry)
    assert ideal_copy == []
