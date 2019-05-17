from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import io
import re
from datetime import date, timedelta
from dateutil.parser import parse
import numpy as np

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

def regex_date(string):
    
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    months_short = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
    months_de = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
    months_de_short = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
    
    months_patterns = ['[0-9]{1,2}[\.]?[\s]?' + '(' + '|'.join(months) + ')' + '.' + '(20[12][0-9])?', 
                       '[0-9]{1,2}[\.]?[\s]?' + '(' + '|'.join(months_de) + ')' + '.' + '(20[12][0-9])?',
                       '[0-9]{1,2}[\.]?[\s]?' + '(' + '|'.join(months_short) + ')' + '.' + '(20[12][0-9])?',
                       '(' + '|'.join(months) + ')' + '[\s]?[0-9]{1,2}(th|st|nd|rd)?[\s]?(20[12][0-9])?',
                       '(' + '|'.join(months_short) + ')' + '[\s]?[0-9]{1,2}(th|st|nd|rd)?[\s]?(20[12][0-9])?'
                      ]

    for pattern in months_patterns:
        if re.search(pattern, string):
            return re.search(pattern, string).group()
        
    re_patterns = ['[0-9]{1,2}\\.[0-9]{1,2}\\.20[1,2][0-9]',
                      '[0-9]{1,2}\\.[0-9]{1,2}\\.[1,2][0-9]',
                  '[0-9]{1,2}\\.[0-9]{1,2}.?']

    for pattern in re_patterns:
        if re.search(pattern, string):
            return re.search(pattern, string).group()
    return None

def find_date(soup, title):
    div = soup.find(text=title)

    if div:
    
        div = div.parent

        for i in range(10):
            match = regex_date(div.text)
            if match:
                break
            else:
                div = div.parent
                
        example_date = regex_date(div.text)
        if not example_date:
            example_date = None
            
        elif len(example_date) == 1:
            example_date = example_date[0]

        elif len(example_date)==2:
            date_1 = date(*[int(x) for x in reversed(example_date[0].split('.'))])
            date_2 = date(*[int(x) for x in reversed(example_date[1].split('.'))]) 

            if(date_2-date_1 > timedelta(0)):
                example_date = ' - '.join(example_date)
                
        return example_date
    else: return None

def find_link(soup, title):
    div = soup.find(text=title)

    if div:
        div = div.parent

        re_link = 'href=\".*\"'

        for i in range(5):
            match = re.search(re_link, str(div))
            # print(match)
            if match:
                break
            else:
                div = div.parent
                
        if match:
            link = match.group().split('"')[1]
        else:
            link = ''
                
        return link
    else: return None

def scrap_events(URL, example_title):
    
    raw_html = simple_get(URL)
    soup = BeautifulSoup(raw_html, 'html.parser')

    # Find the div-class of the example title
    for string in [example_title, example_title.upper(), example_title.lower(), 
                example_title.title(), example_title.capitalize()]:
        
        try:
            example = soup.find(text=string)
        except:
            example = None
        if example:
            break
        
    print(example)
            
    if example:
        ex = example
        for i in range(5):
            try:
                example_class = ex['class']
                break
            except:
                ex = ex.parent
        title_pos = np.where(example_title == np.array(ex.text.split('\n')))[0][0]

        # Find the titles
        matches = soup.find_all(attrs={'class': example_class})
        titles = []
        for match in matches:
            if match:
                m = match.text.split('\n')[title_pos]
                titles.append(m)
            else:
                titles.append('')
    else:
        example_class = None
        titles = []

    dates = []
    links = []
    new_titles = []

    print('len(titles)', len(titles))
    for title in titles:
        date = find_date(soup, title)
        link = find_link(soup, title)

        if not link:
            link = URL
        elif link == '':
            link = URL
        elif not 'http' in link:
            link = URL

        if date and link: 
            dates.append(date)
            links.append(link)
            new_titles.append(title)
    print('len(new_titles)', len(new_titles))
    

    return new_titles, dates, links


def uniform_date(date):
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    months_short = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
    months_de = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
    months_de_short = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
    
    for en, de in zip(months, months_de):
        date = re.sub(de, en, date)
    
    try:
        date = parse(date)
        date = date.strftime('%d.%m.%Y')
    except:
        date = ''

    return date