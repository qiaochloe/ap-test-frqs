import re
import pandas as pd

file_name = "ap21-frq-world-history.txt"

with open(f'pdfs-text/{file_name}', encoding="utf-8") as file:
    file_contents = file.read() # string
    file_lines = file.readlines() # list 

# ^([0-9]\.\s)(.*?)((?=\n[0-9]\.)|(?=\s\s\s)|(?=\nDocument [0-9]\s))$
# re.M
# re.S
# re.I

# r"Long Essay" re.I
# r"Document-Based" re.I

x = re.split(r"^([0-9]\.)", file_contents, flags=re.M)
print(type(x))


