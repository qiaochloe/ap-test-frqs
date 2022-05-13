import re

file_name = "ap21-frq-world-history.txt"
file_regex = '^([0-9]\.\s)(.*?)((?=\n[0-9]\.)|(?=\s\s\s)|(?=\nDocument [0-9]\s))$'
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

def get_questions(file_content, file_regex, question_keys):
    """Scrapes CollegeBoard site and returns links to FRQ PDFs
    
    Args: 
        file_name (str): name of file
        file_regex (str): regex to parse file
        question_keys (list): keys in [Type][Number] format for the returned dictionary
    
    Returns:
        dict: dictionary of exam questions sorted by year
    """

    questions = {}
    count = 0
    
    for match in re.finditer(file_regex, file_content, flags=re.I|re.M|re.S):
        
        question = match.group(2) # string
        
        # remove a) b) c) and convert to subquestions list
        question = re.sub("^[abc]\)\s", "", question, flags=re.I|re.M|re.S)
        question = re.findall("^.*?\n*$", question, flags=re.I|re.M|re.S) # list of subquestions
        
        # clean up newlines and empty strings
        question = [re.sub("\n", "", subquestion, flags=re.I|re.M|re.S).strip(" ") for subquestion in question if subquestion != ""]

        # add subquestions list to dictionary
        questions[question_keys[count]] = question        
        count += 1

    return questions

def main(file_name, file_regex, question_keys):
    
    questions = {}
    
    with open(f'test-data/{file_name}', encoding="utf-8") as file:
        file_content = file.read() # string
        file_content = remove_bad_phrases(file_content, get_bad_phrases_regex(initial_bad_phrases))
        
        questions = get_questions(file_content, file_regex, question_keys)
        
    return questions

print(main(file_name, file_regex, question_keys))
                    
# ^([0-9]\.\s)(.*?)((?=\n[0-9]\.)|(?=\s\s\s)|(?=\nDocument [0-9]\s))$
# re.M
# re.S
# re.I