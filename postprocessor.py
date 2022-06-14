import pandas as pd

csv_file = "ap-world-history/data.csv"

df = pd.read_csv(csv_file) 

def clean_question(question):
    question = question.strip().replace("  ", " ")
    return question

df["question"] = df["question"].apply(clean_question)