from pdf_scraper import scrape_pdfs
from processor import main

# NOTE: AP US History has two links
# https://apcentral.collegeboard.org/courses/ap-united-states-history/exam/the-exam-prior-to-2014-15?course=ap-art-history

exam = "ap-united-states-history"
# scrape_pdfs(exam)

# Run this in the shell
# for i in *; do qpdf --decrypt --replace-input "$i"; done
# TODO: write script to verify that pdf and pdf-text have the same number of documents

# use Adobe Acrobat to get text
