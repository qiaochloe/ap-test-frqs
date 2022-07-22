import pandas as pd
import re
from helper import create_csv

# CHECK:
# EURO
# Man for the field and woman for the hearth: Man for the sword and for the needle she:,LEQ,6,2000,https://secure-media.collegeboard.org/apc/euro_hist_00.pdf,


def remove_1999(df: pd.DataFrame) -> pd.DataFrame:
    df.astype({"year": "int32"}).dtypes  # make sure that year is int
    df = df.drop(df[df["year"] == 1999].index, inplace=True)
    return df


def strip_df(df: pd.DataFrame, key: str) -> pd.DataFrame:
    def strip_chars(text: str) -> str:
        try:
            text = text.strip()

            text = re.sub(
                "(?<=\. ).*?answer \(a\), \(b\), and \(c\)\w*?\.",
                "",
                text,
                flags=re.I | re.M | re.S,
            )

            # removes "a) lorem ipsum"
            text = re.sub("^[\dabc](\)|\.)", "", text, flags=re.I | re.M)
            # removes "lorem ipsum b) dolor sit amet"
            text = re.sub("(?<=\. )[abc]\)", "", text, flags=re.I | re.M)
            # removes " a. lorem ipsum b. dolor sit amet"
            text = re.sub(" [abc]\. ", "", text, flags=re.I | re.M)
            # removes " (a) lorem ipsum (b) dolor sit amet"
            text = re.sub(" \([abc]\) ", "", text, flags=re.I | re.M)

            text = re.sub("\s{2,5}", " ", text, flags=re.M)
            text = text.strip()

        except _:
            pass
        finally:
            return text

    df[f"{key}"] = df[f"{key}"].apply(strip_chars)
    return df


def main(exam: Exam):
    question = pd.read_csv(f"{exam}/question.csv")
    source = pd.read_csv(f"{exam}/source.csv")

    remove_1999(question)
    remove_1999(source)

    strip_df(question, "question")
    strip_df(source, "source_content")

    if exam == "ap-united-states-history":
        question = patch_two(question)

    create_csv(question, f"./{exam}/question.csv")
    create_csv(source, f"./{exam}/source.csv")


if __name__ == "__main__":
    exams = [
        "ap-european-history",
        "ap-united-states-government-and-politics",
        "ap-united-states-history",
        "ap-world-history",
    ]

    for exam in exams:
        main(exam)
