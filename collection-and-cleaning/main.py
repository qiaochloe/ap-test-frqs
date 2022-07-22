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

# scrape_pdfs(exam)

# Run this in the shell to unlock the PDFs
# cd {exam}/pdf
# for i in *; do qpdf --decrypt --replace-input "$i"; done

# use Adobe Acrobat to get text

# Example
# exam = WorldHistoryExam()
# scrape_pdfs(exam.name)

# processor.main(exam)
# postprocessor.main(exam.name)
