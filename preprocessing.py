import re

begin_response_phrase = ["BeginyourresponsetothisquestionatthetopofanewpageintheseparateFreeResponsebooklet",
                  "andfillintheappropriatecircleatthetopofeachpagetoindicatethequestionnumber"]

end_of_exam_phrase = ["WHEN YOUFINISH WRITING,CHECK YOUR WORKONSECTIONIIIF TIMEPERMITS",
                      "STOP END OF EXAM"]

def get_bad_phrases_regex(*phrases_list):
    """Returns regex pattern that recognizes phrase patterns regardless of whitespace characters in between
    
    Args:
        phrases (list): list of blacklisted phrases
        
    Returns:
        list: list of regex for blacklisted phrases
    """
    
    bad_phrases_regex = []
    
    for phrases in phrases_list: 
        for phrase in phrases:
            phrase = phrase.replace(" ", "")
            phrase = "".join(x + "\s*" for x in phrase)
            bad_phrases_regex.append(phrase)
        
    return bad_phrases_regex

def remove_phrases(file_content, regex):
    """Removes phrases using regex
    
    Args:
        file_content (str): text content 
        regex (list): list of regex to remove phrases by
        
    Returns:
        str: the text content with phrases removed 
    """
    
    for phrase in regex: 
        file_content = re.sub(phrase, '', file_content)
    
    return file_content

BAD_PHRASES_REGEX = get_bad_phrases_regex(begin_response_phrase, end_of_exam_phrase)

def preprocess_file_content(file_content):
    file_content = remove_phrases(file_content, BAD_PHRASES_REGEX)
    return file_content