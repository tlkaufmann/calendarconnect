from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import io
import re

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

URL = 'https://zkm.de/en/exhibitions-events/current-exhibitions'
URL2 = 'https://events.microsoft.com/?timeperiod=next30Days&isSharedInLocalViewMode=false&country=Germany&city=Karlsruhe,%20Baden-W%C3%BCrttemberg,%20Germany'

raw_html = simple_get(URL)
soup = BeautifulSoup(raw_html, 'html.parser')

example_title = 'Writing the History of the Future'
example = soup.find(text=example_title)
example_class = example.parent.parent['class']

matches = soup.find_all(attrs={'class': example_class})

print('All titles')
for match in matches:
    print(match.text)



example = example.parent

for i in range(5):
    match = re.findall('2019', example.text)
    if match:
        break
    else:
        example = example.parent


print('Div of title:')
print(example.text)





