import re

file_name = "ap21-frq-world-history.txt"
file_regex = '^([0-9]\.\s)(.*?)((?=\n[0-9]\.)|(?=\s\s\s)|(?=\nDocument [0-9]\s))$'
# blacklist
bad_phrases = ["BeginyourresponsetothisquestionatthetopofanewpageintheseparateFreeResponsebooklet",
               "andfillintheappropriatecircleatthetopofeachpagetoindicatethequestionnumber.",
               "WHEN YOUFINISH WRITING,CHECK YOUR WORKONSECTIONIIIF TIMEPERMITS.",
               "STOP END OF EXAM"]

bad_phrases_regex = []

for phrase in bad_phrases:
    phrase = phrase.replace(" ", "")
    phrase = "".join(x + "\s*" for x in phrase)
    bad_phrases_regex.append(phrase)

# separate frq questions into a list
questions = {}
question_keys = ["SAQ1", "SAQ2", "SAQ3", "SAQ4", "DBQ1", "LEQ2", "LEQ3", "LEQ4"]
count = 0

with open(f'test-data/{file_name}', encoding="utf-8") as file:
    file_content = file.read() # string
    
    for phrase in bad_phrases_regex:
        file_content = re.sub(phrase, '', file_content)
    
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
                    
# ^([0-9]\.\s)(.*?)((?=\n[0-9]\.)|(?=\s\s\s)|(?=\nDocument [0-9]\s))$
# re.M
# re.S
# re.I

