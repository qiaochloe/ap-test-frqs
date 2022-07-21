# TODO:
# add "Source:" as a header for a document; remove before getting questions
# add section for "Historical Background:"; also remove before getting questions
# add section for Form B?
# consider serving regex as tuples (for the flags)

# NOTE:
# AP GOV has set 1 and 2 starting 2021
# APUSH, APEH had Form B from 2002-2011
# APWORLD doesn't have any special forms

import re
import pandas as pd
import numpy as np
from datetime import date
from preprocessor import preprocess_file_content
from pdf_scraper import (
    get_frqs_url,
    get_frqs_soup,
    get_question_links,
    get_scoring_links,
)
from os import listdir
from os.path import exists

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

    @classmethod
    def get_exam_edition(cls, year: str, file_content: str) -> str:
        return ""

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
        cls, question_url: str, year: str, file_content: str
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
                    question_url,
                ]
            )

        return docs

    @classmethod
    def get_sources(cls, question_url: str, year: str, file_content: str) -> list:

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
                    question_url,
                ]
            )

        return sources

    @classmethod
    def get_source_df(
        cls, question_url: str, year: str, file_content: str
    ) -> pd.DataFrame:

        columns = [
            "source_content",
            "source_number",
            "question_type",
            "question_number",
            "year",
            "question_url",
        ]

        df = pd.DataFrame(
            [
                *cls.get_documents(question_url, year, file_content),
                *cls.get_sources(question_url, year, file_content),
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
        cls, question_url: str, year: str, file_content: str
    ) -> pd.DataFrame:

        questions = cls.get_questions(file_content)
        question_type, question_number = cls.get_question_type(year)
        questions, question_type, question_number = cls.fill_in_nan(
            questions, question_type, question_number
        )

        columns = [
            "question",
            "question_type",
            "question_number",
            "year",
            "question_url",
        ]
        df = pd.DataFrame(columns=columns)

        count = 0
        while count < len(questions):
            df.loc[count + 1] = [
                questions[count],
                question_type[count],
                question_number[count],
                year,
                question_url,
            ]
            count += 1

        return df


class EuropeanHistoryExam(WorldHistoryExam):
    name = "ap-european-history"

    @classmethod
    def get_exam_edition(cls, year: str, file_content: str) -> str:
        year = int(year)
        if 2002 <= year <= 2011:
            if "Form B" in file_content:
                return "Form B"
        return ""

    @classmethod
    def get_sources(
        cls, question_url: str, year: str, file_content: str
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
                    question_url,
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


class UnitedStatesHistoryExam(WorldHistoryExam):
    name = "ap-united-states-history"

    @classmethod
    def get_exam_edition(cls, year: str, file_content: str) -> str:
        year = int(year)
        if 2002 <= year <= 2011:
            if "Form B" in file_content:
                return "Form B"
        return ""

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


class UnitedStatesGovernmentAndPoliticsExam(WorldHistoryExam):
    name = "ap-united-states-government-and-politics"

    @classmethod
    def get_exam_edition(cls, year: str, file_content: str) -> str:
        year = int(year)
        if year >= 2021:
            if "Set 2" in file_content:
                return "Set 2"
        return "Set 1"

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


def get_pdf_name_from_link(link: str) -> str:
    link = link.split("/")[-1]
    link = link.split(".pdf")[0] + ".txt"
    return link


def main(exam: Exam) -> None:

    question_links = get_question_links(
        get_frqs_soup(get_frqs_url(exam.name)), exam.name
    )
    # files = get_files(f"{exam.name}/question-text") then [for file in files]

    source_dfs_list = []
    question_dfs_list = []

    for url in question_links:

        # exam identification information
        file_name = get_pdf_name_from_link(url)
        file_path = f"{exam.name}/question-text/{file_name}"

        if exists(file_path):
            file_content = get_file_content(file_path)
        else:
            print("Missing URL: " + url)
            print("Missing FILE: " + file_name)
            continue

        year = exam.get_year(file_name, file_content)
        exam_edition = exam.get_exam_edition(year, file_content)

        # sources
        file_content = preprocess_file_content(file_content)
        source_df = exam.get_source_df(url, year, file_content)
        source_df["exam_edition"] = exam_edition
        source_dfs_list.append(source_df)

        # questions
        file_content = exam.remove_sources(file_content)
        question_df = exam.get_question_df(url, year, file_content)
        question_df["exam_edition"] = exam_edition
        question_dfs_list.append(question_df)

    source_dfs = pd.concat(source_dfs_list, ignore_index=True, sort=False)
    question_dfs = pd.concat(question_dfs_list, ignore_index=True, sort=False)
    create_csv(source_dfs, f"{exam.name}/source.csv")
    create_csv(question_dfs, f"{exam.name}/question.csv")


# TESTS

if __name__ == "__main__":
    apwh = WorldHistoryExam()
    main(apwh)

    apush = UnitedStatesHistoryExam()
    main(apush)

    euro = EuropeanHistoryExam()
    main(euro)

    apgov = UnitedStatesGovernmentAndPoliticsExam()
    main(apgov)

# with open("test.txt", "w+") as file:
#    content = remove_sources(preprocess_file_content(get_file_content("ap-world-history/question-text/ap-world-history-frq-2017.txt")))
#    file.write(content)

# a = preprocess_file_content(get_file_content("ap-world-history/question-text/ap16_frq_world_history.txt"))
# with open("test.txt", "w+") as file:
#    file.write(a)
