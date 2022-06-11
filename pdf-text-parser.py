import re
import pandas as pd
import numpy as np

EARLIEST_YEAR = 1954
LATEST_YEAR = 2022

file_name = "ap21-frq-world-history.txt"
file_regex = "^([0-9]\.\s)(.*?)((?=\n[0-9]\.)|(?=\s\s\s)|(?=\nDocument [0-9]\s))$"
question_keys = ["SAQ1", "SAQ2", "SAQ3", "SAQ4", "DBQ1", "LEQ2", "LEQ3", "LEQ4"]

initial_bad_phrases = ["BeginyourresponsetothisquestionatthetopofanewpageintheseparateFreeResponsebooklet",
               "andfillintheappropriatecircleatthetopofeachpagetoindicatethequestionnumber.",
               "WHEN YOUFINISH WRITING,CHECK YOUR WORKONSECTIONIIIF TIMEPERMITS.",
               "STOP END OF EXAM"]

def get_bad_phrases_regex(bad_phrases):
    """Returns regex pattern that recognizes phrase patterns regardless of whitespace characters in between
    
    Args:
        bad_phrases (list): list of blacklisted phrases
        
    Returns:
        list: list of regex for blacklisted phrases
    """
    
    bad_phrases_regex = []
    
    for phrase in bad_phrases:
        phrase = phrase.replace(" ", "")
        phrase = "".join(x + "\s*" for x in phrase)
        bad_phrases_regex.append(phrase)
        
    return bad_phrases_regex

def remove_bad_phrases(file_content, bad_phrases_regex):
    """Removes phrases using regex
    
    Args:
        file_content (str): text content 
        bad_phrases (list): list of phrases to remove
        
    Returns:
        str: the text content with bad phrases removed 
    """
    
    for phrase in bad_phrases_regex: 
        file_content = re.sub(phrase, '', file_content)
    
    return file_content

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
    
def get_year(file_name, file_content):
    # search content of the file
    year_regex = "\d+"
    for match in re.finditer(year_regex, file_content):
        if len(value) == 4 and EARLIEST_YEAR <= int(value) <= LATEST_YEAR:
            return match
    
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

def get_question_type(year):
    if year >= 2017:
        question_type = [["SAQ", "1"], ["SAQ", "2"],
                         ["SAQ", "3"], ["SAQ", "4"],
                         ["DBQ", "1"], ["LEQ", "2"],
                         ["LEQ", "3"], ["LEQ", "4"]]
    else:
        question_type = [["DBQ", "1"], ["LEQ", "2"], ["LEQ", "3"]]
    
    return question_type

# MAIN defines the path at test-data/{file_name}
def main(file_name, file_regex):
    
    with open(f'test-data/{file_name}', encoding="utf-8") as file:
        file_content = file.read() # string
        file_content = remove_bad_phrases(file_content, get_bad_phrases_regex(initial_bad_phrases))
        questions = get_questions(file_content, file_regex)
        
    return questions

print(main(file_name, file_regex))
                    
# ^([0-9]\.\s)(.*?)((?=\n[0-9]\.)|(?=\s\s\s)|(?=\nDocument [0-9]\s))$
# re.M
# re.S
# re.I