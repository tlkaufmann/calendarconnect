from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import io
import re
from datetime import date, timedelta
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("--url", help="", type=str)
parser.add_argument("--title", help="", type=str)
args = parser.parse_args()  


def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

def find_date(title):
    div = soup.find(text=title)
    
    div = div.parent

    for i in range(5):
        match = re.findall(re_pattern, div.text)
        if match:
            break
        else:
            div = div.parent
            
    example_date = div.find(text = re.compile(re_pattern))
    example_date = re.findall(re_pattern, example_date)
    
    if len(example_date) == 1:
        example_date = example_date[0]

    if len(example_date)==2:
        date_1 = date(*[int(x) for x in reversed(example_date[0].split('.'))])
        date_2 = date(*[int(x) for x in reversed(example_date[1].split('.'))]) 

        if(date_2-date_1 > timedelta(0)):
            example_date = ' - '.join(example_date)
            
    return example_date

# URL = 'https://zkm.de/en/exhibitions-events/current-exhibitions'
# example_title = 'Writing the History of the Future'
URL = args.url
example_title = args.title
re_pattern = '[0-9]{1,2}\\.[0-9]{1,2}\\.[20]*[1,2][0-9]'

raw_html = simple_get(URL)
soup = BeautifulSoup(raw_html, 'html.parser')

example = soup.find(text=example_title)

example_class = example.parent.parent['class']
matches = soup.find_all(attrs={'class': example_class})
titles = []
for match in matches:
    m = re.sub('\n', '', match.text)
    titles.append(m)

for title in titles:
    print("{}: \t{}".format(title, find_date(title)))

