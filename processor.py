import re
import pandas as pd
import numpy as np
from datetime import date
from preprocessor import preprocess_file_content 
from os import listdir

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

EARLIEST_YEAR = 1954

def get_latest_year():
    if date.today().month >  6:
        latest_year = date.today().year
    else: 
        latest_year = date.today().year - 1
    return latest_year

LATEST_YEAR = get_latest_year()
    
def get_year(file_content, file_name):

    """
    Args: 
        file_content (str): content of the text file
        file_name (str): name of the text file
    
    Returns:
        str: year of the exam; NaN if the year is not found
    """
    # search content of the file
    year_regex = "\d+"
    for match in re.finditer(year_regex, file_content):
        value = match.group(0)
        if len(value) == 4 and EARLIEST_YEAR <= int(value) <= LATEST_YEAR:
            return value
    
    # search the name of the file
    for match in re.finditer("\d+", file_name): # all numbers in a str
        value = match.group(0)
        if len(value) == 4 and EARLIEST_YEAR <= int(value) <= LATEST_YEAR:
            return value
        elif len(value) == 2:
            if int(value) <= int(str(LATEST_YEAR)[-2:]):
                return "20" + value
            elif int(value) >= int(str(EARLIEST_YEAR)[-2:]):
                return "19" + value
            
    return np.NaN

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
    
    for match in re.finditer(question_regex, file_content, flags=re.I|re.M|re.S):
        
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
        year (str): year of the exam
    
    Returns:
        question_type (list): type of each FRQ (SAQ, DBQ, LEQ)
        question_number (list): question number of each FRQ as given in the text
    """
    
    if pd.isna(year): 
        return [np.nan], [np.nan]
    
    elif int(year) > 2017:
        questions = [["SAQ", "1"], ["SAQ", "2"],
                    ["SAQ", "3"], ["SAQ", "4"],
                    ["DBQ", "1"], ["LEQ", "2"],
                    ["LEQ", "3"], ["LEQ", "4"]]
        
    elif int(year) == 2017:
        questions = [["SAQ", "1"], ["SAQ", "2"],
                    ["SAQ", "3"], ["SAQ", "4"],
                    ["DBQ", "1"], ["LEQ", "2"],
                    ["LEQ", "3"]]
    
    else:
        questions = [["DBQ", "1"], ["LEQ", "2"], ["LEQ", "3"]]
    
    question_type = [question[0] for question in questions]
    question_number = [question[1] for question in questions]
    
    return question_type, question_number

def fill_in_nan(questions, question_type, question_number):
            
    series = [pd.Series(lst, dtype=str) for lst in [questions, question_type, question_number]]
    df = pd.concat(series, axis=1) # fills in NaN
    
    questions = df.iloc[:,0].tolist()
    question_type = df.iloc[:,1].tolist()
    question_number = df.iloc[:,2].tolist()
    
    return questions, question_type, question_number
    
def get_df(file_name, question_regex):
    """
    Args:
        file_name: name of the exam
        question_regex: regex to parse exam questions
        
    Returns:
        pd.DataFrame: df of the FRQs for a given year
    """
    
    file_content = preprocess_file_content(get_file_content(file_name))
    
    year = get_year(file_content, file_name)    
    questions = get_questions(file_content, question_regex)
    question_type, question_number = get_question_type(year)
    questions, question_type, question_number = fill_in_nan(questions, question_type, question_number)
    
    columns = ["question", "question_type", "question_number", "year"]
    df = pd.DataFrame(columns=columns)
    
    #len(questions), len(question_type), len(question_number)
    
    count = 0
    while count < len(questions):
        df.loc[count + 1] = [questions[count], question_type[count], question_number[count], year]
        count += 1
    
    return df
    
def get_files(dir_name):
    files = [file for file in listdir(dir_name) if file.endswith(".txt")]
    return files

def create_csv(df, file_name):
    """
    Args:
        df (pd.DataFrame): df of the FRQs 
        file_name: path to the csv file to be edited 
    """
    
    with open(f"{file_name}", "w+") as file:
        df.to_csv(file, index=False)

def main(exam, question_regex):
    files = get_files(f"{exam}/pdf-text")
    
    file_dfs = [get_df(f"{exam}/pdf-text/{file}", question_regex) for file in files]
    output_df = pd.concat(file_dfs, ignore_index=True, sort=False)
    create_csv(output_df, f"{exam}/data.csv")
    
main("ap-world-history", "^([0-9]\.\s)(.*?)((?=\n[0-9]\.)|(?=\s\s\s)|(?=\nDocument [0-9]\s))$")
    
#main("./test-data/ap19-frq-world-history.txt", question_regex, "test.csv")