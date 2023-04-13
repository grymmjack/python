import os
import time
import urllib3
import signal
import sys
from bs4 import BeautifulSoup


def signal_handler(sig, frame):
    print('\n\nAborting!\n')
    render_output()


signal.signal(signal.SIGINT, signal_handler)
cwd = os.path.split(__file__)[0]
COLLECTION_FILE = f"{cwd}{os.sep}data.txt"
SCRAPED_FILE = f"{cwd}{os.sep}scraped.txt"
file = open(COLLECTION_FILE, mode='r')
http = urllib3.PoolManager()


def render_output():
    print("\nItems scraped:\n")
    unique_data = set(data)
    final_data = (list(unique_data))
    final_data.sort()
    outfile = open(SCRAPED_FILE, 'w')
    for item in final_data:
        print(item)
        outfile.write(f"{item}\n")
    file.close()
    outfile.close()
    sys.exit()


def get_page_title(url, delay=3):
    print(f"Waiting {delay} seconds...", end='')
    time.sleep(delay)
    print(f"Fetching {url:64}", end='...')
    response = http.request('GET', url)
    html = response.data
    parsed_html = BeautifulSoup(html,features="html.parser")
    title = ''
    try:
        title = parsed_html.select('font[size="4"]')[0].getText()
    except (Exception):
        pass
    print(f"FOUND TITLE: {title}")
    return title


lines = file.readlines()
total_lines = len(lines)
num_pad = len(str(total_lines))
data = []
urls_found = 0

for line in lines:
    if line.startswith('http'):
        urls_found += 1
        print(f"{urls_found:{num_pad}d}: ", end='')
        data.append(get_page_title(line.strip(),delay=0))

render_output()
