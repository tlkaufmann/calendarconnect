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

    # Load the page
    URL = args.url
    example_title = args.title

    titles, dates = scrap_events(URL, example_title)

    for title, date in zip(titles, dates):
        print("{}: \t{}".format(title, date))
