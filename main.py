from pdf_scraper import scrape_pdfs
from processor import main

exam = "ap-european-history"

scrape_pdfs(exam)

# Run this in the shell
# for i in *; do qpdf --decrypt --replace-input "$i"; done
# TODO: write script to verify that pdf and pdf-text have the same number of documents

# use Adobe Acrobat to get text

main(exam, "^([0-9]\.)(.*?)((?=\n[1-9]\.)|(?=\s\s\s)|(?=\nDocument [0-9]\s)|(?=\sEND))$")