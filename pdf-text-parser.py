import re
import pandas as pd
import numpy as np
from preprocessing import preprocess_file_content 

EARLIEST_YEAR = 1954
LATEST_YEAR = 2022

file_name = "ap21-frq-world-history.txt"
file_regex = "^([0-9]\.\s)(.*?)((?=\n[0-9]\.)|(?=\s\s\s)|(?=\nDocument [0-9]\s))$"
question_keys = ["SAQ1", "SAQ2", "SAQ3", "SAQ4", "DBQ1", "LEQ2", "LEQ3", "LEQ4"]

def get_file_content(file_name):
    """
    Args: 
        file_name (str): name of the text file
    
    Returns: 
        str: content of the text file
    """
    
    with open(file_name, encoding="utf-8") as file:
        file_content = file.read() # string
        
    return file_content

def get_year(file_content, file_name):
    """
    Args: 
        file_content (str): content of the text file
        file_name (str): name of the text file
    
    Returns:
        int: year of the exam; NaN if the year is not found
    """
    # search content of the file
    year_regex = "\d+"
    for match in re.finditer(year_regex, file_content):
        value = match.group(0)
        if len(value) == 4 and EARLIEST_YEAR <= int(value) <= LATEST_YEAR:
            return int(value)
    
    # search the name of the file
    for match in re.finditer("\d+", file_name): # all numbers in a str
        value = match.group(0)
        if len(value) == 4 and EARLIEST_YEAR <= int(value) <= LATEST_YEAR:
            return int(value)
        elif len(value) == 2:
            if int(value) <= int(str(LATEST_YEAR)[-2:]):
                return int("20" + value)
            elif int(value) >= int(str(EARLIEST_YEAR)[-2:]):
                return int("19" + value)
            
    return np.NaN

def get_questions(file_content, file_regex):
    """Gets a list of questions
    
    Args: 
        file_content (str): content of the text file
        file_regex (str): regex to parse file
    
    Returns:
        list: list of exam questions in chronological order (as they appear in the text)
    """

    questions = []
    count = 0
    
    for match in re.finditer(file_regex, file_content, flags=re.I|re.M|re.S):
        
        question = match.group(2) # string
        
        # remove a) b) c) and convert to subquestions list
        question = re.sub("^[abc]\)\s", "", question, flags=re.I|re.M|re.S)
        question = re.findall("^.*?\n*$", question, flags=re.I|re.M|re.S) # list of subquestions
        
        # clean up newlines and empty strings
        question = [re.sub("\n", "", subquestion, flags=re.I|re.M|re.S).strip(" ") for subquestion in question if subquestion != ""]
        
        # convert list to string
        question = ' '.join(question)

        # add subquestions to dictionary
        questions.append(question)
        count += 1

    return questions    

def get_question_type(year):
    """
    Args:
        year (int): year of the exam
    
    Returns:
        question_type (list): type of each FRQ (SAQ, DBQ, LEQ)
        question_number (list): question number of each FRQ as given in the text
    """
    
    if np.isnan(year): 
        return [np.nan for i in range(10)], [np.nan for i in range(10)]
    
    elif year >= 2017:
        questions = [["SAQ", "1"], ["SAQ", "2"],
                    ["SAQ", "3"], ["SAQ", "4"],
                    ["DBQ", "1"], ["LEQ", "2"],
                    ["LEQ", "3"], ["LEQ", "4"]]
    
    else:
        questions = [["DBQ", "1"], ["LEQ", "2"], ["LEQ", "3"]]
    
    question_type = [question[0] for question in questions]
    question_number = [question[1] for question in questions]
    
    return question_type, question_number

def get_df(year, questions, question_type, question_number):
    """
    Args:
        year (int): year of exam
        questions (list): list of FRQs in order
        question_type (list): list of the type of each FRQ 
        question_number (list): list of the question number of each FRQ 
        
    Returns:
        pd.DataFrame: df of the FRQs for a given year
    """
    
    columns = ["question", "question_type", "question_number", "year"]
    df = pd.DataFrame(columns=columns)
    
    count = 0
    while count < len(questions):
        df.loc[count + 1] = [questions[count], question_type[count], question_number[count], year]
        count += 1

    return df
    
def create_csv(df, file_name):
    """
    Args:
        df (pd.DataFrame): df of the FRQs 
        file_name: path to the csv file to be edited 
    """
    
    with open(f"{file_name}", "w+") as file:
        df.to_csv(file)
    
def main(data_file_name, file_regex, output_file_name):
    
    file_content = preprocess_file_content(get_file_content(data_file_name))
    
    year = get_year(file_content, data_file_name)    
    questions = get_questions(file_content, file_regex)
    question_type, question_number = get_question_type(year)
    
    df = get_df(year, questions, question_type, question_number)
    create_csv(df, output_file_name)
    
main("./test-data/ap19-frq-world-history.txt", file_regex, "test.csv")
                    
# ^([0-9]\.\s)(.*?)((?=\n[0-9]\.)|(?=\s\s\s)|(?=\nDocument [0-9]\s))$
# re.M
# re.S
# re.I