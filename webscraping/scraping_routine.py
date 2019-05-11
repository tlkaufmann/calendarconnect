from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import io
import re
from datetime import date, timedelta
import argparse
from dateutil.parser import parse
import numpy as np

from scraping_tools import *

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="", type=str)
    parser.add_argument("--title", help="", type=str)
    parser.add_argument("--date", help="", type=str)
    args = parser.parse_args()  

    # Load the page
    URL = args.url
    example_title = args.title

    titles, dates, links = scrap_events(URL, example_title)

    for title, date, link in zip(titles, dates, links):
        print("{}: \t{} \t{}".format(title, date, link))
