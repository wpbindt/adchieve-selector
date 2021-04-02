from selector_functional import flatten_column

import pandas
from pandas.testing import assert_frame_equal


def test_flatten_column():
    df = pandas.DataFrame(
        data={
            'nested_column': [[1, 2, 3], [4], []],
            'id': ['a', 'b', 'c']
        }
    )
    expected = pandas.DataFrame(
        data={
            'nested_column': [1, 2, 3, 4],
            'id': ['a', 'a', 'a', 'b']
        }
    )
    actual = flatten_column(df, 'nested_column')
    assert_frame_equal(actual, expected, check_like=True)


def test_flatten_columns_empty():
    df = pandas.DataFrame(columns=['nested_column', 'id'])
    assert_frame_equal(flatten_column(df, 'nested_column'), df)
