# Importing the required modules
from random import random
from time import sleep
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
import sys
import _thread


def extract_data(day):
    url = f'http://nepalstock.com/todaysprice?_limit=500&startDate={day}'
    print(f'Data for day: {day}, URL: {url}')
    year = day.split('-')[0]
    data = []

    page = urlopen(url)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")

    list_header = []
    soup = BeautifulSoup(html, 'html.parser')
    header = soup.find_all("table")[0].find_all("tr")[1]

    for items in header:
        try:
            list_header.append(items.get_text())
        except:
            continue

    table_data = soup.find_all("table")[0].find_all("tr")[2:]

    for element in table_data:
        sub_data = []
        for sub_element in element:
            try:
                sub_data.append(sub_element.get_text().strip(
                    "\n                                              "))
            except:
                continue
        data.append(sub_data)

    try:
        dataFrame = pd.DataFrame(data=data, columns=list_header)
        dataFrame = dataFrame[dataFrame['S.N.'].apply(lambda x: x.isnumeric())]
        dataFrame.to_csv(f'data/{year}/{day}.csv', index=False)
    except:
        print(f'no data found on {day}')
    # sleep for few seconds before sending another request
    # to avoid blocking
    sleep(2*random())


if len(sys.argv) < 3:
    print('Invalid no of arguments.')
    print(f'Usagage: python main.py <start_date> <end_date>')
    print(f'Example Usage: python main.py 2010-01-01 2010-01-20')
    exit(-1)

dates = pd.date_range(start=sys.argv[1], end=sys.argv[2])

# filter out firday and saturday
# as there is no transaction
dates = [(date) for date in dates if (
    date.weekday() < 4 or date.weekday() > 5
)]

if len(dates) == 0:
    print(f'Date Range {sys.argv[1]} to {sys.argv[2]} is invalid!')
    exit(-1)

for date in dates:
    dt = f"{date:%Y-%m-%d}"
    _thread.start_new_thread(extract_data, (dt,))
    sleep(0.5)
