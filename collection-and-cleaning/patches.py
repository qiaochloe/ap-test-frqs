class Question:
    def __init__(
        self,
        question: str,
        year: int,
        question_type: str,
        question_number: int,
        exam_edition: str = " ",
    ):
        self.question = question
        self.year = year
        self.question_type = question_type
        self.question_number = question_number
        self.exam_edition = exam_edition

    def edit_row(self, df):
        df.loc[
            (df["year"] == self.year)
            & (df["question_type"] == self.question_type)
            & (df["question_number"] == self.question_number)
            & (df["exam_edition"] == self.exam_edition),
            "question",
        ] = self.question

        return df


# United States History
def apush_2016_saq(df: pd.DataFrame):
    question_text = [
        "BrieflyexplainhowONEmajorhistoricalfactorcontributedtothechangedepictedonthegraph. BrieflyexplainONEspecifichistoricaleffectthatresultedfromthechangedepictedonthegraph. BrieflyexplainANOTHERspecifichistoricaleffectthatresultedfromthechangedepictedonthegraph.",
        "Briefly explain ONE important similarity between the goals of the Spanish and the English in establishingcolonies in the Americas prior to 1700. Briefly explain ONE important difference between the goals of the Spanish and the English in establishingcolonies in the Americas prior to 1700. Briefly explain ONE way in which the difference you indicated in (b) contributed to a difference in thedevelopment of Spanish and English colonial societies.",
        "Briefly explain ONE major difference between Josephson’s and Brands’s historical interpretations of businessleaders who rose to prominence between 1865 and 1900. Briefly explain how ONE person, event, or development from the period 1865–1900 that is not explicitlymentioned in the excerpts could be used to support Josephson’s interpretation. Briefly explain how ONE person, event, or development from the period 1865–1900 that is not explicitlymentioned in the excerpts could be used to support Brands’s interpretation.",
        "Identify ONE factor that increased tensions between Great Britain and its North American colonies in theperiod 1763–1776, and briefly explain how this factor helped lead to the American Revolution. Identify a SECOND distinct factor that increased tensions between Great Britain and its North Americancolonies in the same period, and briefly explain how this factor helped lead to the American Revolution. Identify a THIRD distinct factor that increased tensions between Great Britain and its North Americancolonies in the same period, and briefly explain how this factor helped lead to the American Revolution.",
        "Explain the causes of the rise of a women’s rights movement in the period 1940–1975.",
        "Evaluate the extent to which the ratification of the Fourteenth and Fifteenth Amendments to the Constitutionmarked a turning point in the history of United States politics and society. In the development of your argument, explain what changed and what stayed the same from the periodimmediately before the amendments to the period immediately following them. (Historical thinking skill:Periodization)",
        "Evaluate the extent to which United States participation in the First World War (1917–1918) marked a turningpoint in the nation’s role in world affairs. In the development of your argument, explain what changed and what stayed the same from the periodimmediately before the war to the period immediately following it. (Historical thinking skill: Periodization)",
    ]

    Question_list = [Question(question_text[i], SAQ, 2, 2016) for i in range(7)]

    for question in Question_list:
        question.edit_row(df)
