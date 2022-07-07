# TODO: Check that number of scoring guidelines and number of pdfs are the same

import requests
from bs4 import BeautifulSoup as bs
import os


def get_frqs_url(exam):
    match exam:
        case "ap-united-states-government-and-politics":
            frqs_url = "https://apcentral.collegeboard.org/courses/ap-united-states-government-and-politics/exam/ap-us-government-and-politics-past-exam-questions"
        case _:
            frqs_url = f"https://apcentral.collegeboard.org/courses/{exam}/exam/past-exam-questions"

    return frqs_url


def get_frqs_soup(frqs_url):

    frqs_html = requests.get(frqs_url).text
    frqs_soup = bs(frqs_html, "lxml")

    return frqs_soup


def get_question_links(frqs_soup):
    """Scrapes CollegeBoard site and returns links to FRQ PDFs

    Args:
        exam (str): name of exam

    Returns:
        list: list of links to question PDFs
    """

    # Get links to question PDFs
    question_links = []

    for table in frqs_soup.findAll("table"):
        a = table.find("a", href=True)  # first link
        link = a["href"]  # href attribute in <a>

        if "https" in link:
            question_links.append(link)
        else:
            question_links.append("https://apcentral.collegeboard.org" + link)

    return question_links


def get_scoring_links(frqs_soup):
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


def download_pdfs(exam, folder, links):
    """Downloads PDFs under {exam}/pdf/{pdf_name}

    Args:
        exam (str): name of the exam
        folder (str): name of the subfolder inside the exam folder
        links (list): links to PDFs

    Returns:
        none
    """

    for link in links:

        # Get pdf info
        name = link.split("/")[-1]
        content = requests.get(link).content

        path = f"{exam}/{folder}/{name}"
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Create pdf with said info
        with open(path, "wb") as pdf:
            pdf.write(content)


def scrape_pdfs(exam, frqs_url):
    soup = get_frqs_soup(frqs_url)

    # question_links = get_question_links(soup)
    scoring_links = get_scoring_links(soup)

    # download_pdfs(exam, "question", question_links)
    download_pdfs(exam, "scoring-guideline", scoring_links)


def main(exam):
    frqs_url = get_frqs_url(exam)
    scrape_pdfs(exam, frqs_url)

    if exam == "ap-united-states-history":
        scrape_pdfs(
            exam,
            "https://apcentral.collegeboard.org/courses/ap-united-states-history/exam/the-exam-prior-to-2014-15?course=ap-art-history",
        )


main("ap-world-history")
