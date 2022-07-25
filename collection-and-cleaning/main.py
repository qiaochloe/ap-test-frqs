from pdf_scraper import scrape_pdfs
import processor
from processor import (
    Exam,
    WorldHistoryExam,
    EuropeanHistoryExam,
    UnitedStatesHistoryExam,
    UnitedStatesGovernmentAndPoliticsExam,
)
import postprocessor

# Example
exam = UnitedStatesGovernmentAndPoliticsExam()
# scrape_pdfs(exam.name)

# >>> cd {exam}/pdf
# >>> for i in *; do qpdf --decrypt --replace-input "$i"; done

# Use ADOBE ACROBAT to get the text from the pdf

processor.main(exam)
postprocessor.main(exam.name)
