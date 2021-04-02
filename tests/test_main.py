from unittest.mock import patch

import pandas
from pandas.testing import assert_frame_equal

from selector_functional import main
from tests.utils import equal_dataframes


def test_main():
    input_df = pandas.DataFrame(
        data={
            'searchTerm': [
                'the new blue bike', 'new bike', 'new bike', 'red bike', 'bike'
            ],
            'adGroupName': [
                'blue bikes', 'yellow bikes', 'blue bikes',
                'red bike', 'blue bike'
            ],
            'campaignName': 5 * ['campaign name'],
            'impressions': [300, 200, 100, 10, 300]
        }
    )
    threshold = 299
    stopwords = ['the', 'and', 'all']
    actual = main(input_df, threshold, stopwords)
    expected = pandas.DataFrame(
        data={
            'selection': ['new blue bike', 'new bike'],
            'adGroupName': ['blue bikes', 'yellow bikes'],
            'searchTerm': ['the new blue bike', 'new bike'],
            'campaignName': 2 * ['campaign name']
        }
    )

    equal_dataframes(actual, expected, 'adGroupName')


@patch('selector_functional.MAX_WORDS_QUERY', 2)
def test_main_max_words():
    input_df = pandas.DataFrame(
        data={
            'searchTerm': ['1 2 3'],
            'adGroupName': ['blue bikes'],
            'impressions': [300],
            'campaignName': ['campaign name']
        }
    )
    threshold = 299
    stopwords = ['the', 'and', 'all']
    actual = main(input_df, threshold, stopwords)
    expected = pandas.DataFrame(
        data={
            'selection': ['1 2', '2 3'],
            'adGroupName': 2 * ['blue bikes'],
            'searchTerm': 2 * ['1 2 3'],
            'campaignName': 2 * ['campaign name']
        }
    )
    equal_dataframes(actual, expected, 'adGroupName')


def test_main_empty():
    input_df = pandas.DataFrame(columns=[
        'searchTerm', 'adGroupName', 'impressions', 'campaignName'
    ])
    actual = main(input_df, 300, ['stop', 'words'])
    expected = pandas.DataFrame(columns=[
        'selection', 'adGroupName', 'campaignName', 'searchTerm'
    ])
    assert_frame_equal(actual, expected, check_like=True)
