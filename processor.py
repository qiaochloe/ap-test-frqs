# TODO: 
# Clean the sources.csv
# Separate APWH-specific parts from the functions (make them reuseable)

import re
import pandas as pd
import numpy as np
from datetime import date
from preprocessor import preprocess_file_content
from helper import get_file_content, remove_phrases
from os import listdir


def get_latest_year():
    if date.today().month > 6:
        latest_year = date.today().year
    else:
        latest_year = date.today().year - 1
    return latest_year


EARLIEST_YEAR = 1954
LATEST_YEAR = get_latest_year()


def get_year(file_content):
    """
    Args:
        file_content (str): content of the text file

    Returns:
        str: year of the exam; NaN if the year is not found
    """
    # search content of the file
    year_regex = "\d+"
    for match in re.finditer(year_regex, file_content):
        value = match.group(0)
        if len(value) == 4 and EARLIEST_YEAR <= int(value) <= LATEST_YEAR:
            return value

    return np.NaN


# ----------------- #
# GET SOURCES.CSV #
# ----------------- #


def get_documents(file_content, doc_regex):

    year = get_year(file_content)
    docs = []

    for match in re.finditer(doc_regex, file_content, flags=re.M | re.S):
        doc_number = match.group(2)
        doc_content = match.group(3)
        question_type = "DBQ"
        question_number = "1"
        docs.append([doc_content, doc_number, question_type, question_number, year])

    return docs


def get_sources(file_content, sources_regex):
    year = get_year(file_content)
    sources = []

    for match in re.finditer(sources_regex, file_content, flags=re.M | re.S):
        source_content = match.group(3)
        source_number = "0"
        # source_type =  match.group(2)
        question_type = "SAQ"
        question_number = match.group(5)
        sources.append(
            [source_content, source_number, question_type, question_number, year]
        )

    return sources


doc_regex = r"^(Document\s*)(\d)(.*?)(?=(Document|END))"
sources_regex = r"^(Use the (.*?) to answer all parts of the question that follows\.\s*)(.*?)((?<!\d)(?=([1-9])\.))"


def get_sources_df(file_content):
    columns = [
        "source_content",
        "source_number",
        "question_type",
        "question_number",
        "year",
    ]

    df = pd.DataFrame(
        [*get_documents(file_content, doc_regex), *get_sources(file_content, sources_regex)], columns=columns
    )
    return df


def remove_sources(file_content):
    file_content = remove_phrases(file_content, [doc_regex], regex_flags=re.M|re.S)
    file_content = remove_phrases(file_content, [sources_regex], regex_flags=re.M|re.S)
    
    return file_content


# ------------ #
# GET DATA.CSV #
# ------------ #


def get_questions(file_content, question_regex):
    """Gets a list of questions

    Args:
        file_content (str): content of the text file
        question_regex (str): regex to parse file

    Returns:
        list: list of exam questions in chronological order (as they appear in the text)
    """

    questions = []
    count = 0

    for match in re.finditer(question_regex, file_content, flags=re.I | re.M | re.S):
        question = match.group(2)  # string

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

    elif int(year) > 2017:
        questions = [
            ["SAQ", "1"],
            ["SAQ", "2"],
            ["SAQ", "3"],
            ["SAQ", "4"],
            ["DBQ", "1"],
            ["LEQ", "2"],
            ["LEQ", "3"],
            ["LEQ", "4"],
        ]

    elif int(year) == 2017:
        questions = [
            ["SAQ", "1"],
            ["SAQ", "2"],
            ["SAQ", "3"],
            ["SAQ", "4"],
            ["DBQ", "1"],
            ["LEQ", "2"],
            ["LEQ", "3"],
        ]

    else:
        questions = [["DBQ", "1"], ["LEQ", "2"], ["LEQ", "3"]]

    question_type = [question[0] for question in questions]
    question_number = [question[1] for question in questions]

    return question_type, question_number


def fill_in_nan(questions, question_type, question_number):

    series = [
        pd.Series(lst, dtype=str) for lst in [questions, question_type, question_number]
    ]
    df = pd.concat(series, axis=1)  # fills in NaN

    questions = df.iloc[:, 0].tolist()
    question_type = df.iloc[:, 1].tolist()
    question_number = df.iloc[:, 2].tolist()

    return questions, question_type, question_number


def get_questions_df(file_content, question_regex):
    """
    Args:
        file_content: content of the file
        question_regex: regex to parse exam questions

    Returns:
        pd.DataFrame: df of the FRQs for a given year
    """

    year = get_year(file_content)
    questions = get_questions(file_content, question_regex)
    question_type, question_number = get_question_type(year)
    questions, question_type, question_number = fill_in_nan(
        questions, question_type, question_number
    )

    columns = ["question", "question_type", "question_number", "year"]
    df = pd.DataFrame(columns=columns)

    count = 0
    while count < len(questions):
        df.loc[count + 1] = [
            questions[count],
            question_type[count],
            question_number[count],
            year,
        ]
        count += 1

    return df


def get_files(dir_name):
    files = [file for file in listdir(dir_name) if file.endswith(".txt")]
    return files


def create_csv(df, file_name):
    """
    Args:
        df (pd.DataFrame): df
        file_name: path to the csv file to be edited
    """

    with open(f"{file_name}", "w+") as file:
        df.to_csv(file, index=False)


def main(exam, question_regex):
    files = get_files(f"{exam}/pdf-text")
    
    sources_dfs_list = []
    questions_dfs_list = []
    
    for file in files:
        file_content = preprocess_file_content(get_file_content(f"{exam}/pdf-text/{file}"))
        sources_dfs_list.append(get_sources_df(file_content))                                       
        
        file_content = remove_sources(file_content)
        questions_dfs_list.append(get_questions_df(file_content, question_regex))
        
    sources_dfs = pd.concat(sources_dfs_list, ignore_index=True, sort=False)
    create_csv(sources_dfs, f"{exam}/sources.csv")

    questions_dfs = pd.concat(questions_dfs_list, ignore_index=True, sort=False)
    create_csv(questions_dfs, f"{exam}/questions.csv")

#with open("test.txt", "w+") as file:
#    content = remove_sources(preprocess_file_content(get_file_content("ap-world-history/pdf-text/ap-world-history-frq-2017.txt")))
#    file.write(content)
    
main(
    "ap-world-history",
    "^([0-9]\.)(.*?)((?=\n[1-9]\.)|(?=\s\s\s)|(?=\nDocument [0-9]\s)|(?=\sEND))$",
)


#"^(((Use)(.*?)(answer)(.*?)(question that follows\.)))(.*?)([0-9]\.)"
# a = preprocess_file_content(get_file_content("ap-world-history/pdf-text/ap16_frq_world_history.txt"))

# with open("test.txt", "w+") as file:
#    file.write(a)
