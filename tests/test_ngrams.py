from selector_functional import ngrams

from tests.utils import same_elements


def test_ngrams():
    phrase = 'dummy phrase is'
    assert same_elements(
        ngrams(phrase),
        {
            'dummy', 'phrase', 'is',
            'dummy phrase', 'phrase is',
            'dummy phrase is'
        }
    )


def test_ngrams_repeated_word():
    phrase = 'dummy is dummy'
    assert same_elements(
        ngrams(phrase),
        {
            'dummy', 'is',
            'dummy is', 'is dummy',
            'dummy is dummy'
        }
    )


def test_ngrams_no_words():
    phrase = ''
    assert ngrams(phrase) == []
