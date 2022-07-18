import pandas as pd


def strip_df(df: pd.DataFrame, key: str) -> pd.DataFrame:
    def strip_chars(text: str) -> str:
        try:
            text = text.strip().replace("  ", " ")
            text = re.sub("\n", "", text)
            text = re.sub("^[\dabc](\)|\.)", "", text, flags=re.I | re.M)
        finally:
            return text

    df[f"{key}"] = df[f"{key}"].apply(strip_chars)
    return df


def post_cleaning(
    cls, question_df: pd.DataFrame, source_df: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:

    question_df = cls.strip_df(question_df, "question")
    source_df = cls.strip_df(source_df, "source_content")
    return question_df, source_df


# United States History
def patch_two(question_df: pd.DataFrame) -> pd.DataFrame:
    # ap16_frq_us_history.txt is missing some identifiers
    # so patching it manually

    index = question_df[
        question_df["question_url"]
        == "https://secure-media.collegeboard.org/digitalServices/pdf/ap/ap16_frq_us_history.pdf"
    ].index[0]

    # temp = question_df.loc[index, "question"]
    for i in range(3):
        question_df.loc[index + 6 - i, "question"] = question_df.loc[
            index + 5 - i, "question"
        ]

    question_df.loc[
        index + 3, "question"
    ] = "Briefly explain ONE major difference between Josephson’s and Brands’s historical interpretations of businessleaders who rose to prominence between 1865 and 1900. Briefly explain how ONE person, event, or development from the period 1865–1900 that is not explicitlymentioned in the excerpts could be used to support Josephson’s interpretation. Briefly explain how ONE person, event, or development from the period 1865–1900 that is not explicitlymentioned in the excerpts could be used to support Brands’s interpretation."

    return question_df


def main():
    exams = [
        "ap-european-history",
        "ap-united-states-government-and-politics",
        "ap-united-states-history",
        "ap-world-history",
    ]

    for exam in exams:
        question = pd.read_csv(f"{exam}/question.csv")
        source = pd.read_csv(f"{exam}/source.csv")
