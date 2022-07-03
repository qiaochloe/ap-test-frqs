import requests
from bs4 import BeautifulSoup as bs
import os


def get_question_links(exam):
    """Scrapes CollegeBoard site and returns links to FRQ PDFs

    Args:
        exam (str): name of exam

    Returns:
        list: list of links to question PDFs
    """
    # Set up soup
    frqs_url = (
        f"https://apcentral.collegeboard.org/courses/{exam}/exam/past-exam-questions"
    )
    frqs_html = requests.get(frqs_url).text
    frqs_soup = bs(frqs_html, "lxml")

    # Get links to question PDFs
    question_links = []

    for table in frqs_soup.findAll("table"):
        a = table.find("a", href=True)
        link = a["href"]

        if "https" in link:
            question_links.append(link)
        else:
            question_links.append("https://apcentral.collegeboard.org" + link)

    return question_links


def download_pdfs(exam, links):
    """Downloads PDFs under {exam}/pdf/{pdf_name}

    Args:
        links (list): links to PDFs

    Returns:
        none
    """

    for link in links:

        # Get pdf info
        name = link.split("/")[-1]
        content = requests.get(link).content

        path = f"{exam}/pdf/{name}"
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Create pdf with said info
        with open(path, "wb") as pdf:
            pdf.write(content)


def scrape_pdfs(exam):
    question_links = get_question_links(exam)
    download_pdfs(exam, question_links)
