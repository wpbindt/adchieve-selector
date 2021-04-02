from selector_functional import prune_ngrams


def test_prune_ngrams():
    ngrams = [
        'bike',
        'car',
        'please',
        'gazelle bike',
        'bike please',
        'red bike',
        'red gazelle bike',
        'blue gazelle bike'
    ]

    assert prune_ngrams(ngrams) == {
        'blue gazelle bike',
        'red gazelle bike',
        'red bike',
        'bike please',
        'car'
    }


def test_prune_ngrams_empty():
    assert prune_ngrams([]) == set()
