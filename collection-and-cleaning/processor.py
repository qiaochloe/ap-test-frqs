# TODO:
# add "Source:" as a header for a document; remove before getting questions
# add section for "Historical Background:"; also remove before getting questions
# add section for Form B?
# consider serving regex as tuples (for the flags)

import re
import pandas as pd
import numpy as np
from datetime import date
from preprocessor import preprocess_file_content
from os import listdir

from typing import Tuple


class Exam:

    earliest_year = 1954
    latest_year = date.today().year if date.today().month > 6 else date.today().year - 1

    @classmethod
    def get_year(cls, file_name: str, file_content: str) -> str:
        # search content of the file
        year_regex = "\d+"
        for match in re.finditer(year_regex, file_content):
            value = match.group(0)
            if len(value) == 4 and cls.earliest_year <= int(value) <= cls.latest_year:
                return value

        # search the name of the file
        for match in re.finditer("\d+", file_name):  # all numbers in a str
            value = match.group(0)
            if len(value) == 4 and EARLIEST_YEAR <= int(value) <= LATEST_YEAR:
                return value
            elif len(value) == 2:
                if int(value) <= int(str(LATEST_YEAR)[-2:]):
                    return "20" + value
                elif int(value) >= int(str(EARLIEST_YEAR)[-2:]):
                    return "19" + value

        return np.NaN

    @staticmethod
    def remove_phrases(
        file_content: str, regex_list: list, regex_flags=re.I | re.M
    ) -> str:

        """Removes phrases from file using a list of regex"""
        if type(regex_list) is not list:
            regex_list = [regex_list]
        for regex in regex_list:
            file_content = re.sub(regex, "", file_content, flags=regex_flags)
        return file_content


class WorldHistoryExam(Exam):

    name = "ap-world-history"
    doc_regex = r"^(Document\s*)(\w*)(.*?)(?=(Document|END|Question \d))"
    # doc_regex = r"^(Document\s*)(\w*)(.*?)(?=(Document|END|\D[1-3]\.\s))"
    source_regex = r"^(Use the (.*?) to answer all parts of the question that follows\.\s*)(.*?)((?<!\d)(?=([1-9])\.))"
    question_regex = (
        r"^([0-9]\.)(.*?)((?=\n[1-9]\.)|(?=\s\s\s)|(?=\nDocument [\w*]\s)|(?=\sEND))$"
    )

    @classmethod
    def get_documents(
        cls, file_name: str, year: str, file_content: str
    ) -> list[list[str]]:

        docs = []

        for match in re.finditer(cls.doc_regex, file_content, flags=re.M | re.S):
            doc_number = match.group(2)
            doc_content = (
                match.group(3)
                if any(char.isalpha() for char in match.group(3))
                else "Missing Document."
            )
            question_type = "DBQ"
            question_number = "1"
            docs.append(
                [
                    doc_content,
                    doc_number,
                    question_type,
                    question_number,
                    year,
                    file_name,
                ]
            )

        return docs

    @classmethod
    def get_sources(cls, file_name: str, year: str, file_content: str) -> list:

        sources = []

        for match in re.finditer(cls.source_regex, file_content, flags=re.M | re.S):
            source_content = match.group(3)
            source_number = "0"
            # source_type =  match.group(2)
            question_type = "SAQ"
            question_number = match.group(5)
            sources.append(
                [
                    source_content,
                    source_number,
                    question_type,
                    question_number,
                    year,
                    file_name,
                ]
            )

        return sources

    @classmethod
    def get_source_df(
        cls, file_name: str, year: str, file_content: str
    ) -> pd.DataFrame:

        columns = [
            "source_content",
            "source_number",
            "question_type",
            "question_number",
            "year",
            "file_name",
        ]

        df = pd.DataFrame(
            [
                *cls.get_documents(file_name, year, file_content),
                *cls.get_sources(file_name, year, file_content),
            ],
            columns=columns,
        )
        return df

    @classmethod
    def remove_sources(cls, file_content: str) -> str:

        file_content = cls.remove_phrases(
            file_content, [cls.doc_regex], regex_flags=re.M | re.S
        )
        file_content = cls.remove_phrases(
            file_content, [cls.source_regex], regex_flags=re.M | re.S
        )

        return file_content

    @staticmethod
    def get_question_type(year: str) -> tuple[list, list]:

        if pd.isna(year):
            return [np.nan], [np.nan]

        if int(year) > 2017:
            saq_range = range(1, 5)  # 1, 2, 3, 4
            dbq_range = range(1, 2)  # 1
            leq_range = range(2, 5)  # 2, 3, 4
        elif int(year) == 2017:
            saq_range = range(1, 5)
            dbq_range = range(1, 2)
            leq_range = range(2, 4)  # 2, 3
        else:
            saq_range = range(0)
            dbq_range = range(1, 2)
            leq_range = range(2, 4)

        questions = (
            [["SAQ", str(i)] for i in saq_range]
            + [["DBQ", str(i)] for i in dbq_range]
            + [["LEQ", str(i)] for i in leq_range]
        )
        question_type = [question[0] for question in questions]
        question_number = [question[1] for question in questions]
        return question_type, question_number

    @classmethod
    def get_questions(cls, file_content: str) -> list:
        """Returns a list of exam questions in chronological order (as they appear in the text)"""

        questions = []

        for match in re.finditer(
            cls.question_regex, file_content, flags=re.I | re.M | re.S
        ):
            question = match.group(2)  # string

            # Filter out matches that can't be questions (hacky)
            if len(question) < 20:
                continue

            # remove a) b) c) and convert to subquestions list
            question = re.sub("^[abc]\)\s", "", question, flags=re.I | re.M | re.S)
            question = re.findall(
                "^.*?\n*$", question, flags=re.I | re.M | re.S
            )  # list of subquestions

            # clean up newlines and empty strings
            question = [
                re.sub("\n", "", subquestion, flags=re.I | re.M | re.S).strip(" ")
                for subquestion in question
                if subquestion != "" and subquestion != " "
            ]

            # convert list to string
            question = " ".join(question)

            # add subquestions to dictionary
            questions.append(question)

        return questions

    @staticmethod
    def fill_in_nan(
        questions: list, question_type: list, question_number: list
    ) -> tuple[list, list, list]:

        series = [
            pd.Series(lst, dtype=str)
            for lst in [questions, question_type, question_number]
        ]
        df = pd.concat(series, axis=1)  # fills in NaN

        questions = df.iloc[:, 0].tolist()
        question_type = df.iloc[:, 1].tolist()
        question_number = df.iloc[:, 2].tolist()

        return questions, question_type, question_number

    @classmethod
    def get_question_df(
        cls, file_name: str, year: str, file_content: str
    ) -> pd.DataFrame:

        questions = cls.get_questions(file_content)
        question_type, question_number = cls.get_question_type(year)
        questions, question_type, question_number = cls.fill_in_nan(
            questions, question_type, question_number
        )

        columns = ["question", "question_type", "question_number", "year", "file_name"]
        df = pd.DataFrame(columns=columns)

        count = 0
        while count < len(questions):
            df.loc[count + 1] = [
                questions[count],
                question_type[count],
                question_number[count],
                year,
                file_name,
            ]
            count += 1

        return df

    @staticmethod
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

    @classmethod
    def postprocessor(
        cls, question_df: pd.DataFrame, source_df: pd.DataFrame
    ) -> tuple[pd.DataFrame, pd.DataFrame]:

        question_df = cls.strip_df(question_df, "question")
        source_df = cls.strip_df(source_df, "source_content")
        return question_df, source_df


class EuropeanHistoryExam(WorldHistoryExam):
    name = "ap-european-history"

    @classmethod
    def get_sources(
        cls, file_name: str, year: str, file_content: str
    ) -> list[list[str]]:
        sources = []

        for match in re.finditer(cls.source_regex, file_content, flags=re.M | re.S):
            source_content = match.group(3)
            source_number = "0"
            # source_type =  match.group(2)
            question_type = "SAQ" if int(year) >= 2017 else "LEQ"
            question_number = match.group(5)
            sources.append(
                [
                    source_content,
                    source_number,
                    question_type,
                    question_number,
                    year,
                    file_name,
                ]
            )

        return sources

    @staticmethod
    def get_question_type(year: str) -> tuple[list[str], list[int]]:

        if pd.isna(year):
            return [np.nan], [np.nan]

        if int(year) > 2017:
            saq_range = range(1, 5)
            dbq_range = range(1, 2)
            leq_range = range(2, 5)
        elif int(year) == 2017:
            saq_range = range(1, 5)
            dbq_range = range(1, 2)
            leq_range = range(2, 4)
        else:
            saq_range = range(0)
            dbq_range = range(1, 2)
            leq_range = range(2, 8)

        questions = (
            [["SAQ", str(i)] for i in saq_range]
            + [["DBQ", str(i)] for i in dbq_range]
            + [["LEQ", str(i)] for i in leq_range]
        )
        question_type = [question[0] for question in questions]
        question_number = [question[1] for question in questions]
        return question_type, question_number

    @staticmethod
    def patch_one(question_df: pd.DataFrame) -> pd.DataFrame:
        # question_regex doesn't recognize semicolons (such as "Question 1:")
        # This patches the data for the 1999 txt file

        index = question_df[question_df["year"] == "1999"].index[0]
        questions = [
            "For the period 1861 to 1914, analyze how various Russians perceived the condition of the Russian peasantry and explain how they proposed to change that condition.",
            "Contrast how a Marxist and a Social Darwinist would account for the differences in the conditions of these two mid-nineteenth-century families.",
            "Analyze the ways in which the contrasting styles of these two paintings reflect the different economic values and social structures of France and the Netherlands in the seventeenth century.",
            "Contrast the historical context, beliefs, and behavior of quepean youth represented by these two photographs.",
            """Machiavelli suggested that a ruler should behave both "like a lion" and "like a fox." Analyze the policies of TWO of the following quepean rulers, indicating the degree to which they successfully followed Machiavellis suggestion.
        Choose two: Elizabeth I of England
        Henry IV of France
        Catherine the Great of Russia
        Frederick II of Prussia""",
            """Discuss the relationship between politics and religion by examining the wars of religion. Choose TWO specific examples from the following:
        Dutch Revolt  French Wars of Religion  English Civil War Thirty Years' War""",
            "Compare and contrast the degree of success of treaties negotiated in Vienna (1814-1815) and Versailles (1919) in achieving quepean stability.",
        ]

        question_df.loc[index : index + 6, "question"] = questions
        return question_df

    @classmethod
    def postprocessor(cls, question_df: pd.DataFrame, source_df: pd.DataFrame):

        question_df = cls.strip_df(question_df, "question")
        source_df = cls.strip_df(source_df, "source_content")

        question_df = cls.patch_one(question_df)
        return question_df, source_df


class UnitedStatesHistoryExam(WorldHistoryExam):
    name = "ap-united-states-history"

    @staticmethod
    def get_question_type(year: str) -> tuple[list[str], list[int]]:

        if pd.isna(year):
            return [np.nan], [np.nan]

        if int(year) >= 2019:
            saq_range = range(1, 5)  # 1, 2, 3, 4
            dbq_range = range(1, 2)  # 1
            leq_range = range(2, 5)  # 2, 3, 4
        elif int(year) >= 2015:
            saq_range = range(1, 5)
            dbq_range = range(1, 2)
            leq_range = range(2, 4)  # 2, 3
        else:
            saq_range = range(0)
            dbq_range = range(1, 2)
            leq_range = range(2, 6)

        questions = (
            [["SAQ", str(i)] for i in saq_range]
            + [["DBQ", str(i)] for i in dbq_range]
            + [["LEQ", str(i)] for i in leq_range]
        )
        question_type = [question[0] for question in questions]
        question_number = [question[1] for question in questions]
        return question_type, question_number

    @staticmethod
    def patch_one(question_df: pd.DataFrame) -> pd.DataFrame:
        # question_regex doesn't recognize semicolons (such as "Question 1:")
        # This patches the data for the 1999 txt file
        # ^(([0-9]\.)|Question \d)(.*?)((?=\n[1-9]\.)|(?=\nQuestion \d)|(?=\s\s\s)|(?=\nDocument [\w*]\s)|(?=\sEND))$

        index = question_df[question_df["year"] == "1999"].index[0]
        questions = [
            "To what extent had the colonists developed a sense of their identity and unity as Americans by the eve of the Revolution? Use the documents and your knowledge of the period 1750 to 1776 to answer the question.",
            """How did TWO of the following contribute to the reemergence of a two party system in the period 1820 to 1840?
Major political personalities
States' rights 
Economic issues""",
            "How were the lives of the Plains Indians in the second half of the nineteenth century affected by technological developments and government actions?",
            "In what ways did economic conditions and developments in the arts and entertainment help create the reputation of the 1920s as the Roaring Twenties?",
            "Assess the success of the United States policy of containment in Asia between 1945 and 1975.",
        ]

        question_df.loc[index : index + 4, "question"] = questions
        return question_df

    def patch_two(question_df: pd.DataFrame) -> pd.DataFrame:
        # ap16_frq_us_history.txt is missing some identifiers
        # so patching it manually

        index = question_df[
            question_df["file_name"] == "ap16_frq_us_history.txt"
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

    @classmethod
    def postprocessor(
        cls, question_df: pd.DataFrame, source_df: pd.DataFrame
    ) -> tuple[pd.DataFrame, pd.DataFrame]:

        question_df = cls.strip_df(question_df, "question")
        source_df = cls.strip_df(source_df, "source_content")

        question_df = cls.patch_one(question_df)
        question_df = cls.patch_two(question_df)
        return question_df, source_df


class UnitedStatesGovernmentAndPoliticsExam(WorldHistoryExam):
    name = "ap-united-states-government-and-politics"

    @staticmethod
    def get_question_type(year: str) -> tuple[list[str, list[int]]]:

        if pd.isna(year):
            return [np.nan], [np.nan]

        if int(year) >= 2019:
            saq_range = range(1, 4)  # 1, 2, 3
            leq_range = range(4, 5)  # 4
        else:
            saq_range = range(1, 5)
            leq_range = range(0)

        questions = [["SAQ", str(i)] for i in saq_range] + [
            ["LEQ", str(i)] for i in leq_range
        ]

        # type of each FRQ (SAQ, DBQ, LEQ)
        question_type = [question[0] for question in questions]
        # question number of each FRQ as given in the text
        question_number = [question[1] for question in questions]

        return question_type, question_number

    @staticmethod
    def strip_df(df: pd.DataFrame, key: str) -> pd.DataFrame:
        def strip_chars(text: str) -> str:
            try:
                text = text.strip().replace("  ", " ")
                text = re.sub("\n", "", text)
                text = re.sub("^[\dabc](\)|\.)", "", text, flags=re.I | re.M)
                text = re.sub("\([abc]\) ", "", text)
            finally:
                return text

        df[f"{key}"] = df[f"{key}"].apply(strip_chars)
        return df

    @classmethod
    def postprocessor(
        cls, question_df: pd.DataFrame, source_df: pd.DataFrame
    ) -> tuple[pd.DataFrame, pd.DataFrame]:

        question_df = cls.strip_df(question_df, "question")
        source_df = cls.strip_df(source_df, "source_content")

        return question_df, source_df


def get_files(dir_name: str) -> list:
    """Returns a list of the names of all the files in a directory"""

    files = [file for file in listdir(dir_name) if file.endswith(".txt")]
    return files


def get_file_content(file_name: str) -> str:
    """
    Args:
        file_name (str): name of the text file

    Returns:
        str: content of the text file
    """

    with open(file_name, encoding="utf-8") as file:
        file_content = file.read()  # string
    return file_content


def create_csv(df: pd.DataFrame, file_name: str) -> None:

    with open(f"{file_name}", "w+") as file:
        df.to_csv(file, index=False)


def main(exam: Exam) -> None:
    files = get_files(f"{exam.name}/question-text")

    source_dfs_list = []
    question_dfs_list = []

    for file in files:
        file_content = get_file_content(f"{exam.name}/question-text/{file}")
        year = exam.get_year(file, file_content)

        file_content = preprocess_file_content(file_content)
        source_dfs_list.append(exam.get_source_df(file, year, file_content))

        file_content = exam.remove_sources(file_content)
        question_dfs_list.append(exam.get_question_df(file, year, file_content))

    source_dfs = pd.concat(source_dfs_list, ignore_index=True, sort=False)
    question_dfs = pd.concat(question_dfs_list, ignore_index=True, sort=False)

    question_dfs, source_dfs = exam.postprocessor(question_dfs, source_dfs)

    create_csv(source_dfs, f"{exam.name}/source.csv")
    create_csv(question_dfs, f"{exam.name}/question.csv")


# TESTS

if __name__ == "__main__":
    # apwh = WorldHistoryExam()
    # main(apwh)

    # apush = UnitedStatesHistoryExam()
    # main(apush)

    # euro = EuropeanHistoryExam()
    # main(euro)

    apgov = UnitedStatesGovernmentAndPoliticsExam()
    main(apgov)

# with open("test.txt", "w+") as file:
#    content = remove_sources(preprocess_file_content(get_file_content("ap-world-history/question-text/ap-world-history-frq-2017.txt")))
#    file.write(content)

# a = preprocess_file_content(get_file_content("ap-world-history/question-text/ap16_frq_world_history.txt"))
# with open("test.txt", "w+") as file:
#    file.write(a)
