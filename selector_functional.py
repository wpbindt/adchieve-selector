import re
from typing import Iterable, List, Set

import numpy
import pandas

REQUIRED_COLUMNS = {
    'searchTerm',
    'impressions',
    'adGroupName',
    'campaignName',
}

MAX_WORDS_QUERY = 10


def check_for_columns(data: pandas.DataFrame, columns: Iterable[str]) -> None:
    for column in columns:
        if column not in data.columns:
            raise ValueError(f'Missing required column: {column}')


def is_asin(query: str) -> bool:
    return query.startswith('b0') and len(query) == 10


def normalize(query: str, stopwords_regex: re.Pattern) -> str:
    lowercase_query = query.lower()
    no_stopwords = re.sub(stopwords_regex, '', lowercase_query)
    only_alphanumeric_chars = re.sub(r'[^\w ]', '', no_stopwords)
    return ' '.join(only_alphanumeric_chars.split())  # remove whitespace


def preprocess(
    df: pandas.DataFrame,
    stopwords_regex: re.Pattern
) -> pandas.DataFrame:
    check_for_columns(df, REQUIRED_COLUMNS)
    no_asins = df[~ df.searchTerm.apply(is_asin)]
    if no_asins.empty:
        return pandas.DataFrame(
            columns=list(df.columns) + ['normalizedSearchTerm']
        )

    return (
        no_asins
        .assign(
            normalizedSearchTerm=lambda df:
            df.searchTerm.apply(normalize, stopwords_regex=stopwords_regex)
        )
    )


def grams(n: int, words: List[str]) -> Set[str]:
    return {
        ' '.join(token)
        for token in zip(*(words[i:] for i in range(n)))
    }


def ngrams(phrase: str) -> Set[str]:
    words = phrase.split()
    output = []
    for n in range(1, len(words) + 1):
        output.extend(grams(n, words))

    return output


def flatten_column(
    df: pandas.DataFrame,
    list_column: str,
) -> pandas.DataFrame:
    """
    This is basically the "explode" method from pandas,
    which is not available in 0.23.4.
    """
    if df.empty:
        return df
    lens_of_lists = df[list_column].apply(len)
    origin_rows = range(len(df))
    destination_rows = numpy.repeat(origin_rows, lens_of_lists)
    expanded_df = df.iloc[destination_rows].drop(list_column, axis=1)
    expanded_df[list_column] = [
        item
        for items in df[list_column]
        for item in items
    ]
    expanded_df.reset_index(inplace=True, drop=True)
    return expanded_df


def add_ngram_column(df: pandas.DataFrame, column: str) -> pandas.DataFrame:
    return (
        df
        .assign(ngram=lambda df: df[column].apply(ngrams))
        .pipe(flatten_column, list_column='ngram')
    )


def compute_impressions(df: pandas.DataFrame) -> pandas.DataFrame:
    return (
        df
        [['ngram', 'impressions']]
        .groupby('ngram', as_index=False)
        .sum()
    )


def compute_ad_group(df: pandas.DataFrame) -> pandas.DataFrame:
    return (
        df
        .sort_values(by='impressions')
        .drop_duplicates('ngram', keep='last')
        .drop('impressions', axis=1)
    )


def prune_ngrams(ngrams: List[str]) -> Set[str]:
    output = set()
    while ngrams:
        ngram = ngrams.pop()
        output.add(ngram)
        ngrams = list(filter(lambda query: query not in ngram, ngrams))

    return output


def create_stopword_regex(stopwords: List[str]) -> re.Pattern:
    return r'\b' + r'\b|\b'.join(stopwords)


def main(
    df: pandas.DataFrame,
    threshold: int,
    stopwords=List[str]
) -> pandas.DataFrame:
    stopwords_regex = create_stopword_regex(stopwords)
    normalized_ngrams = (
        df
        .pipe(preprocess, stopwords_regex=stopwords_regex)
        .pipe(add_ngram_column, column='normalizedSearchTerm')
    )
    highest_impressions_ad_groups = compute_ad_group(normalized_ngrams)
    all_ngrams = (
        normalized_ngrams
        .pipe(compute_impressions)
        .merge(highest_impressions_ad_groups, on='ngram')
        .assign(ngramLength=lambda df: df.ngram.str.split().str.len())
        .sort_values(by='ngramLength')
        .query('impressions >= @threshold & ngramLength <= @MAX_WORDS_QUERY')
        .drop(columns=['ngramLength', 'impressions', 'normalizedSearchTerm'])
        .rename(columns={'ngram': 'selection'})
    )
    pruned_ngrams = prune_ngrams(all_ngrams.selection.tolist())

    return all_ngrams[all_ngrams.selection.isin(pruned_ngrams)]


# algo:
#  - split every query into ngrams
#  - assign to each ngram the sum of the impressions of all queries in which
#    it occurs, and the ad group where these are maximal
#  - remove the ngrams which fall under a certain threshold
#  - sort the ngrams by length (ascending)
#  - while ngrams:
#        ngram = ngrams.pop()
#        output.append(ngram)
#        ngrams = filter(lambda query: query not in ngram, ngrams)
