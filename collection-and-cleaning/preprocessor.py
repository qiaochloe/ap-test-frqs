# Fix historical background phrase

import re

begin_response_phrase = [
    "BeginyourresponsetothisquestionatthetopofanewpageintheseparateFreeResponsebooklet",
    "andfillintheappropriatecircleatthetopofeachpagetoindicatethequestionnumber",
]
next_page_phrase = ["GO ON TO THE NEXT PAGE"]
directions_phrase = [
    "Directions:",
    "You are to answer the following question.",
    "You should spend 5 minutes organizing or outlining your essay",
    "Write an essay that:",
    "Has a relevant thesis and supports that thesis with appropriate historical evidence",
    "Addresses all parts of the question",
    "Makes direct, relevant comparisons",
    "Analyzes relevant reasons for similarities and differences",
    "Uses world historical context to show continuities and changes over time",
    "Analyzes the process of continuity and change over time",
    "planning and writing",
    "reading and writing",
    "writing time",
    "planning your answer",
    "THIS SPACE MAY BE USED FOR PLANNING YOUR ANSWER",
]
# keep END OF EXAM for the regex (finding the last problem)
end_of_question_phrase = [
    "WHEN YOUFINISH WRITING,CHECK YOUR WORKONSECTIONIIIF TIMEPERMITS"
]
# historical_background_phrase = ["Historical background:"]
keywords = [
    "College Board",
    "Directions:",
    "College Entrance Examination Board",
    "All rights reserved",
]

all_phrases = (
    begin_response_phrase
    + next_page_phrase
    + directions_phrase
    + end_of_question_phrase
    # + historical_background_phrase
    + keywords
)

case_sensitive_phrases = [
    "STOP",
]
more_case_sensitive_phrases = [
    "WORLD HISTORY",
    "UNITED STATES HISTORY",
    "EUROPEAN HISTORY",
]
strip_spaces_regex = ["^ (?=\d)"]
headers_regex = ["SECTION [I]", "Part [ABC]"]
other_regex = ["-[1-20]-"]  # Remove "^(Percent of)(.*?)(score.)(\s*)(.*?)(\s*?)$"


def get_phrases_regex(phrases: list) -> list:
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


all_phrases_regex = get_phrases_regex(all_phrases)
case_sensitive_regex = get_phrases_regex(case_sensitive_phrases)


def remove_phrases(file_content: str, regex_list: list, regex_flags=re.I | re.M) -> str:

    """Removes phrases from file using a list of regex"""

    if type(regex_list) is not list:
        regex_list = [regex_list]
    for regex in regex_list:
        file_content = re.sub(regex, "", file_content, flags=regex_flags)
    return file_content


def preprocess_file_content(file_content: str) -> str:

    file_content = remove_phrases(file_content, strip_spaces_regex)
    file_content = remove_phrases(file_content, all_phrases_regex)
    file_content = remove_phrases(file_content, headers_regex)
    file_content = remove_phrases(
        file_content, other_regex, regex_flags=re.I | re.M | re.S
    )
    file_content = remove_phrases(file_content, case_sensitive_regex, regex_flags=re.M)
    file_content = remove_phrases(
        file_content, more_case_sensitive_phrases, regex_flags=re.M
    )
    return file_content
