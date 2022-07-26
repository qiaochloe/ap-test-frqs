import pandas as pd

# United States History
def patch_one(question_df: pd.DataFrame) -> pd.DataFrame:
    # question_regex doesn't recognize semicolons (such as "Question 1:")
    # This patches the data for the 1999 txt file
    # ^(([0-9]\.)|Question \d)(.*?)((?=\n[1-9]\.)|(?=\nQuestion \d)|(?=\s\s\s)|(?=\nDocument [\w*]\s)|(?=\sEND))$

    index = question_df[question_df["year"] == "1999"].index[0]
    questions = [
        "To what extent had the colonists developed a sense of their identity and unity as Americans by the eve of the Revolution? Use the documents and your knowledge of the period 1750 to 1776 to answer the question.",
        """How did TWO of the following contribute to the reemergence of a two party system in the period 1820 to 1840?
    Major political personalities
    States' rights 
    Economic issues""",
        "How were the lives of the Plains Indians in the second half of the nineteenth century affected by technological developments and government actions?",
        "In what ways did economic conditions and developments in the arts and entertainment help create the reputation of the 1920s as the Roaring Twenties?",
        "Assess the success of the United States policy of containment in Asia between 1945 and 1975.",
    ]

    question_df.loc[index : index + 4, "question"] = questions
    return question_df


# European History
def patch_one(question_df: pd.DataFrame) -> pd.DataFrame:
    # question_regex doesn't recognize semicolons (such as "Question 1:")
    # This patches the data for the 1999 txt file

    index = question_df[question_df["year"] == "1999"].index[0]
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

    question_df.loc[index : index + 6, "question"] = questions
    return question_df
