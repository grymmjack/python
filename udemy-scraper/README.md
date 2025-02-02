# udemy-scraper

## Requirements

✅ Python 3.x - Download & Install: https://www.python.org/downloads/  
✅ Google Chrome - Download & Install: https://www.google.com/chrome/  
✅ ChromeDriver - Automatically installed via webdriver-manager

## Setup

1. Clone repo: `gh repo clone grymmjack/python`
2. Go to dir: `cd python/udemy-scraper`
3. Activate venv: `source bin/activate`
4. Install pypi modules: `pip install selenium webdriver-manager pandas`
5. Get path to chrome profile: `chrome://version` - copy profile path to clipboard and use for `--user-data-dir` in #7
6. Start a new terminal
7. Setup chrome for debugging: `google-chrome --remote-debugging-port=9222 --user-data-dir="/tmp/ChromeProfile"` - this will open a new chrome. Authenticate to udemy in this browser and keep it open while running the script.
8. Run the script: `python scraper.py`

