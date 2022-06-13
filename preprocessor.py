# TODO: check 2013, 2001, 

import re

begin_response_phrase = ["BeginyourresponsetothisquestionatthetopofanewpageintheseparateFreeResponsebooklet",
                         "andfillintheappropriatecircleatthetopofeachpagetoindicatethequestionnumber"]

next_page_phrase = ["GO ON TO THE NEXT PAGE"]

directions_phrase = ["Directions:"
                      "You are to answer the following question.", 
                      "You should spend 5 minutes organizing or outlining your essay",
                      "Write an essay that:",
                      "Has a relevant thesis and supports that thesis with appropriate historical evidence",
                      "Addresses all parts of the question",
                      "Makes direct, relevant comparisons",
                      "Analyzes relevant reasons for similarities and differences",
                      "Uses world historical context to show continuities and changes over time",
                      "Analyzes the process of continuity and change over time",
                      "Suggested planning and writing"
                      "Suggested reading and writing"]

# keep END OF EXAM for the regex (finding the last problem)
end_of_question_phrase = ["WHEN YOUFINISH WRITING,CHECK YOUR WORKONSECTIONIIIF TIMEPERMITS"]

historical_background_phrase = ["Historical background:"]

keywords = ["College Board",
            "Directions:"]

all_phrases = (begin_response_phrase + next_page_phrase + 
               directions_phrase + end_of_question_phrase + 
               historical_background_phrase + keywords)

# ^([0-9]\.)(.*?)((?=\n[0-9]\.)|(?=\s\s\s)|(?=\nDocument [0-9]\s)|(?=\sEND))$

case_sensitive_phrases = ["STOP",
                          "WORLD HISTORY"]

strip_spaces_regex = ["^ (?=\d)"]

headers_regex = ["SECTION [I]",
                 "Part [ABC]"]

other_regex = ["-\d+-",
               "^(Percent of)(.*?)(score.)(\s*)(.*?)(\s*?)$"]

# "^(Percent of)(.*?)(score—)(.*?)(\n)$"

def get_phrases_regex(phrases):
    """Returns regex pattern that recognizes phrase patterns regardless of whitespace characters in between
    
    Args:
        phrases (list): list of blacklisted phrases
        
    Returns:
        list: list of regex for blacklisted phrases
    """
    
    phrases_regex = []
    
    for phrase in phrases:
        phrase = phrase.replace(" ", "")
        phrase = "".join(x + "\s*" for x in phrase)
        phrase = "^.*" + phrase + ".*$"
        phrases_regex.append(phrase)
    
    return phrases_regex    
    
# remove "STOP"
def remove_phrases(file_content, *regex_lists, regex_flags=re.I|re.M):
    """Removes phrases using regex
    
    Args:
        file_content (str): text content 
        regex_lists (list): list of regex to remove phrases by
        
    Returns:
        str: the text content with phrases removed 
    """
    
    for regex_list in regex_lists:
        for regex in regex_list: 
            file_content = re.sub(regex, '', file_content, flags=regex_flags)
    
    return file_content

all_phrases_regex = get_phrases_regex(all_phrases)
case_sensitive_regex = get_phrases_regex(case_sensitive_phrases)

def preprocess_file_content(file_content):
    file_content = remove_phrases(file_content, strip_spaces_regex)
    file_content = remove_phrases(file_content, all_phrases_regex, headers_regex)
    file_content = remove_phrases(file_content, other_regex, regex_flags=re.I|re.M|re.S)
    file_content = remove_phrases(file_content, case_sensitive_regex, regex_flags=re.M)
    return file_content