import pandas as pd
import numpy as np
from processor import create_csv

question_file = "ap-european-history/question.csv"
que = pd.read_csv(question_file)

# question_regex doesn't recognize semicolons (such as "Question 1:") for 1999 txt file
# This patches the data.

index = que[que["year"] == 1999].index[0]
questions = [
    "For the period 1861 to 1914, analyze how various Russians perceived the condition of the Russian peasantry and explain how they proposed to change that condition.",
    "Contrast how a Marxist and a Social Darwinist would account for the differences in the conditions of these two mid-nineteenth-century families.",
    "Analyze the ways in which the contrasting styles of these two paintings reflect the different economic values and social structures of France and the Netherlands in the seventeenth century.",
    "Contrast the historical context, beliefs, and behavior of quepean youth represented by these two photographs.",
    """Machiavelli suggested that a ruler should behave both "like a lion" and "like a fox." Analyze the policies of TWO of the following quepean rulers, indicating the degree to which they successfully followed Machiavellis suggestion. 
Choose two: Elizabeth I of England 
Henry IV of France 
Catherine the Great of Russia 
Frederick II of Prussia""",
    """Discuss the relationship between politics and religion by examining the wars of religion. Choose TWO specific examples from the following: 
Dutch Revolt  French Wars of Religion  English Civil War Thirty Years' War""",
    "Compare and contrast the degree of success of treaties negotiated in Vienna (1814-1815) and Versailles (1919) in achieving quepean stability.",
]

que.loc[index : index + 6, "question"] = questions

create_csv(que, question_file)
