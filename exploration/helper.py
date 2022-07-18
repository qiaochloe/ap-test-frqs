import pandas as pd
import re
import string
from nltk.corpus import stopwords
from collections import Counter
from typing import Tuple


def remove_punct(text):
    PUNCT_TO_REMOVE = string.punctuation
    return text.translate(str.maketrans("", "", PUNCT_TO_REMOVE))


def remove_stopwords(text):
    STOPWORDS = set(stopwords.words("english"))
    return " ".join([word for word in str(text).split() if word not in STOPWORDS])


def remove_freqwords(text):
    FREQWORDS = set(
        [
            "analyze",
            "describe",
            "explain",
            "compare",
            "contrast",
            "evaluate",
            "identify",
            "passage",
            "image",
            "continuity",
            "example",
            "factor",
            "contributed",
        ]
    )
    CAPFREQWORDS = set(["ONE", "TWO", "THREE"])
    return " ".join(
        [
            word
            for word in str(text).split()
            if word.lower() not in FREQWORDS and word not in CAPFREQWORDS
        ]
    )


def process_for_nlp(df):
    df["question_nlp"] = df["question"].apply(
        lambda text: remove_freqwords(remove_stopwords(remove_punct(text)))
    )


def get_common_words(series, n=100):
    """
    Args:
        series (df.Series): column from df such as df["question"]
        n (int): number of common words

    Returns:
        list: list of tuples in (word, count) form
    """

    cnt = Counter()
    for text in series.values:
        for word in text.split():
            cnt[word] += 1

    return cnt.most_common(n)


def get_question_period(df):
    YEAR_REGEX = r"(\d{4})(?:\-|–)?(\d{2,4})?"
    CENTURY_REGEX = r"(\s[a-z]*|\s[a-z]*\s)century"
    CENTURY_PLURAL_REGEX = r" (\w*?) and (\w*?) centuries"

    question_period = []

    for text in df["question"].values:
        year = re.findall(YEAR_REGEX, text, flags=re.M | re.S | re.I)
        century = re.findall(CENTURY_REGEX, text, flags=re.M | re.S | re.I)
        century_plural = re.findall(
            CENTURY_PLURAL_REGEX, text, flags=re.M | re.S | re.I
        )
        # convert list of tuples to flat list

        period = [
            *flatten_tuple_list(year),
            *century,
            *flatten_tuple_list(century_plural),
        ]

        # set only stores unique values
        # period = list(set(period))
        period = list(filter(None, set(period)))
        period = [item.strip() for item in period]

        question_period.append(period if period else "Missing question period.")

    df["df_period"] = question_period


def flatten_tuple_list(tup_list: list[Tuple[str]]) -> list:
    return list(sum(tup_list, ()))
