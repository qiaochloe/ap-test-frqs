# TODO:
# get link to scoring guidelines PDF
# add "Source:" as a header for a document; remove before getting questions
# add section for "Historical Background:"; also remove before getting questions
# consider serving regex as tuples (for the flags)

# TODO:
# Check why source_content (match group 3) sometimes returns a number

import re
import pandas as pd
import numpy as np
from datetime import date
from preprocessor import preprocess_file_content
from os import listdir


class Exam:
    earliest_year = 1954
    latest_year = date.today().year if date.today().month > 6 else date.today().year - 1

    @classmethod
    def get_year(cls, file_name, file_content):
        """
        Args:
            file_name (str): name of the text file
            file_content (str): content of the text file

        Returns:
            str: year of the exam; NaN if the year is not found
        """
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
    def remove_phrases(file_content, regex_list, regex_flags=re.I | re.M):
        """Removes phrases using regex

        Args:
            file_content (str): text content
            regex_list (list): list of regex to remove phrases by
            regex_flags

        Returns:
            str: the text content with phrases removed
        """

        if type(regex_list) is not list:
            regex_list = [regex_list]
        for regex in regex_list:
            file_content = re.sub(regex, "", file_content, flags=regex_flags)
        return file_content


class WorldHistoryExam(Exam):
    name = "ap-world-history"
    doc_regex = r"^(Document\s*)(\d*)(.*?)(?=(Document|END))"
    source_regex = r"^(Use the (.*?) to answer all parts of the question that follows\.\s*)(.*?)((?<!\d)(?=([1-9])\.))"
    question_regex = (
        r"^([0-9]\.)(.*?)((?=\n[1-9]\.)|(?=\s\s\s)|(?=\nDocument [0-9]\s)|(?=\sEND))$"
    )

    @classmethod
    def get_documents(cls, file_name, year, file_content):
        """
        Args:
            file_name (str): name of the text file
            year (str): year of the exam
            file_content (str): content of the file

        Returns:
            list: list of all documents (in string form)
        """

        docs = []

        for match in re.finditer(cls.doc_regex, file_content, flags=re.M | re.S):
            doc_number = match.group(2)
            doc_content = match.group(3)
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
    def get_sources(cls, file_name, year, file_content):
        """
        Args:
            file_name (str): name of the text file
            year (str): year of the exam
            file_content (str): content of the file

        Returns:
            list: list of all sources (in string form)
        """

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
    def get_source_df(cls, file_name, year, file_content):
        """
        Args:
            file_name (str): name of the text file
            year (str): year of the exam
            file_content (str): content of the file

        Returns:
            pd.Dataframe: df of the documents and the sources
        """

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
    def remove_sources(cls, file_content):
        """
        Args:
            file_content (str): content of the file

        Returns:
            str: file content without the documents or sources
        """

        file_content = cls.remove_phrases(
            file_content, [cls.doc_regex], regex_flags=re.M | re.S
        )
        file_content = cls.remove_phrases(
            file_content, [cls.source_regex], regex_flags=re.M | re.S
        )

        return file_content

    @staticmethod
    def get_question_type(year):
        """
        Args:
            year (str): year of the exam

        Returns:
            question_type (list): type of each FRQ (SAQ, DBQ, LEQ)
            question_number (list): question number of each FRQ as given in the text
        """

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
    def get_questions(cls, file_content):
        """Gets a list of questions

        Args:
            file_content (str): content of the text file

        Returns:
            list: list of exam questions in chronological order (as they appear in the text)
        """

        questions = []
        count = 0

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
                if subquestion != ""
            ]

            # convert list to string
            question = " ".join(question)

            # add subquestions to dictionary
            questions.append(question)
            count += 1

        return questions

    @staticmethod
    def fill_in_nan(questions, question_type, question_number):
        """
        Args:
            questions (list): question from the file
            question_type (list): type of question
            question_number (list): number of question

        Returns:
            list, list, list
            Makes each list the same length by filling in NaN
        """

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
    def get_question_df(cls, file_name, year, file_content):
        """
        Args:
            file_name (str): name of the file
            year (str): year of the exam
            file_content (str): content of the text file

        Returns:
            pd.DataFrame: df of the FRQs for a given year
        """

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
    def strip_df(df, key):
        def strip_chars(text):
            try:
                text = text.strip().replace("  ", " ")
                text = re.sub("\n", "", text)
                text = re.sub("^[\dabc](\)|\.)", "", text, flags=re.I | re.M)
            finally:
                return text

        df[f"{key}"] = df[f"{key}"].apply(strip_chars)
        return df

    @classmethod
    def postprocessor(cls, question_df, source_df):
        question_df = cls.strip_df(question_df, "question")
        source_df = cls.strip_df(source_df, "source_content")
        return question_df, source_df


class EuropeanHistoryExam(WorldHistoryExam):
    name = "ap-european-history"

    @classmethod
    def get_sources(cls, file_name, year, file_content):
        """
        Args:
            file_name (str): name of the text file
            year (str): year of the exam
            file_content (str): content of the file

        Returns:
            list: list of all sources (in string form)
        """

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
    def get_question_type(year):

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
    def patch_one(question_df):
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
    def postprocessor(cls, question_df, source_df):
        question_df = cls.strip_df(question_df, "question")
        source_df = cls.strip_df(source_df, "source_content")

        question_df = cls.patch_one(question_df)
        return question_df, source_df


def get_files(dir_name):
    """Gets the names of all the files in a directory

    Args:
        dir_name (str): name of the directory

    Returns:
        files (list): list of all files in the directory
    """

    files = [file for file in listdir(dir_name) if file.endswith(".txt")]
    return files


def get_file_content(file_name):
    """
    Args:
        file_name (str): name of the text file

    Returns:
        str: content of the text file
    """

    with open(file_name, encoding="utf-8") as file:
        file_content = file.read()  # string
    return file_content


def create_csv(df, file_name):
    """
    Args:
        df (pd.DataFrame): df
        file_name: path to the csv file to be edited
    """

    with open(f"{file_name}", "w+") as file:
        df.to_csv(file, index=False)


def main(exam):
    files = get_files(f"{exam.name}/pdf-text")

    source_dfs_list = []
    question_dfs_list = []

    for file in files:
        file_content = get_file_content(f"{exam.name}/pdf-text/{file}")
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

# euro = EuropeanHistoryExam()
# main(euro)

apwh = WorldHistoryExam()
main(apwh)

# with open("test.txt", "w+") as file:
#    content = remove_sources(preprocess_file_content(get_file_content("ap-world-history/pdf-text/ap-world-history-frq-2017.txt")))
#    file.write(content)

# a = preprocess_file_content(get_file_content("ap-world-history/pdf-text/ap16_frq_world_history.txt"))
# with open("test.txt", "w+") as file:
#    file.write(a)
