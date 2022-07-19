# TODO:
# Check that number of scoring guidelines and number of pdfs are the same
# Scrape Set 2 (for AP GOV)

import requests
from bs4 import BeautifulSoup as bs
import os


def get_frqs_url(exam: str) -> str:
    """Returns the past exam questions page from CollegeBoard site for a given AP exam"""

    match exam:
        case "ap-united-states-government-and-politics":
            frqs_url = "https://apcentral.collegeboard.org/courses/ap-united-states-government-and-politics/exam/ap-us-government-and-politics-past-exam-questions"
        case _:
            frqs_url = f"https://apcentral.collegeboard.org/courses/{exam}/exam/past-exam-questions"

    return frqs_url


def get_frqs_soup(frqs_url: str):  # unsure what return type soup is

    frqs_html = requests.get(frqs_url).text
    frqs_soup = bs(frqs_html, "lxml")

    return frqs_soup


def get_question_links(frqs_soup, exam: str = None) -> list:
    """Scrapes CollegeBoard site and returns links to FRQ questions"""

    # Get links to question PDFs
    question_links = []

    for table in frqs_soup.findAll("table"):
        a = table.find("a", href=True)  # first link
        link = a["href"]  # href attribute in <a>

        if "https" in link:
            question_links.append(link)
        else:
            question_links.append("https://apcentral.collegeboard.org" + link)

    if exam is not None:
        if exam == "ap-united-states-history":
            frq_soup = get_frqs_soup(
                "https://apcentral.collegeboard.org/courses/ap-united-states-history/exam/the-exam-prior-to-2014-15?course=ap-art-history"
            )
            more_links = get_question_links(frq_soup)
            question_links.extend(more_links)

    return question_links


def get_scoring_links(frqs_soup) -> list:
    """Scrapes CollegeBoard site and returns links to FRQ scoring guidelines"""

    scoring_links = []

    for table in frqs_soup.findAll("table"):
        for a in table.findAll("a", href=True):
            if a.get_text() == "Scoring Guidelines":
                link = a["href"]
                if "https" in link:
                    scoring_links.append(link)
                else:
                    scoring_links.append("https://apcentral.collegeboard.org" + link)

    return scoring_links


def download_pdfs(exam: str, folder: str, links: list) -> None:
    """Downloads PDFs under {exam}/pdf/{pdf_name}"""

    for link in links:

        # Get pdf info
        name = link.split("/")[-1]
        content = requests.get(link).content

        path = f"{exam}/{folder}/{name}"
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Create pdf with said info
        with open(path, "wb") as pdf:
            pdf.write(content)


def scrape_pdfs(exam: str, frqs_url: str) -> None:
    soup = get_frqs_soup(frqs_url)

    # question_links = get_question_links(soup)
    scoring_links = get_scoring_links(soup)

    # download_pdfs(exam, "question", question_links)
    download_pdfs(exam, "scoring-guideline", scoring_links)


def main():
    exam = "ap-european-history"
    get_question_links(get_frqs_soup(get_frqs_url(exam)))


if __name__ == "__main__":
    main()
