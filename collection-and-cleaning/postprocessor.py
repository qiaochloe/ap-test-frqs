import pandas as pd

# United States History
def patch_two(question_df: pd.DataFrame) -> pd.DataFrame:
    # ap16_frq_us_history.txt is missing some identifiers
    # so patching it manually

    index = question_df[
        question_df["question_url"]
        == "https://secure-media.collegeboard.org/digitalServices/pdf/ap/ap16_frq_us_history.pdf"
    ].index[0]

    # temp = question_df.loc[index, "question"]
    for i in range(3):
        question_df.loc[index + 6 - i, "question"] = question_df.loc[
            index + 5 - i, "question"
        ]

    question_df.loc[
        index + 3, "question"
    ] = "Briefly explain ONE major difference between Josephson’s and Brands’s historical interpretations of businessleaders who rose to prominence between 1865 and 1900. Briefly explain how ONE person, event, or development from the period 1865–1900 that is not explicitlymentioned in the excerpts could be used to support Josephson’s interpretation. Briefly explain how ONE person, event, or development from the period 1865–1900 that is not explicitlymentioned in the excerpts could be used to support Brands’s interpretation."

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
