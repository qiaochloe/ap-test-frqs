# TODO: get link to scoring guidelines PDF

import requests
from bs4 import BeautifulSoup as bs

def get_question_links(exam):
    """Scrapes CollegeBoard site and returns links to FRQ PDFs
    
    :param exam: name of exam
    :type exam: str
    :rtype: list
    :return: links to question PDFs
    """
    # Set up soup
    frqs_url = f"https://apcentral.collegeboard.org/courses/{exam}/exam/past-exam-questions"
    frqs_html = requests.get(frqs_url).text
    frqs_soup = bs(frqs_html, "lxml")

    # Get links to question PDFs
    question_links = []
    
    for table in frqs_soup.findAll('table'):
        a = table.find('a', href=True)
        link = a['href']
        
        if "https" in link: 
            question_links.append(link)
        else: 
            question_links.append("https://apcentral.collegeboard.org" + link)
            
    return question_links

def download_pdfs(links):
    """Downloads PDFs in the pdf folder
    
    :param links: links to PDFs 
    :type links: list
    :rtype: None
    """

    for link in links:
        
        # Get pdf info
        name = link.split('/')[-1]
        path = f"pdfs/{name}"
        content = requests.get(link).content
        
        # Create pdf with said info
        with open(path, "wb") as pdf:
            pdf.write(content)
            
download_pdfs(get_question_links("ap-world-history"))