import pandas as pd
import re
import string
from nltk.corpus import stopwords
from collections import Counter


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
