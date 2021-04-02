def same_elements(one, other):
    return len(one) == len(other) and set(one) == set(other)


def equal_dataframes(one, other, column_to_sort_by):
    assert len(one.columns) == len(other.columns)
    assert (
        (
            one
            .sort_values(by=column_to_sort_by)
            .reset_index()
            [other.columns]
        ) == other
    ).all().all()
