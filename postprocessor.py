import pandas as pd

exam = "ap-world-history"
csv_file = f"{exam}/data.csv"

df = pd.read_csv(csv_file) 

def clean_question(question):
    question = question.strip().replace("  ", " ")
    question = re.sub("^[\dabc](\)|\.)", "", question, flags=re.I|re.M)
    return question

df["question"] = df["question"].apply(clean_question)
