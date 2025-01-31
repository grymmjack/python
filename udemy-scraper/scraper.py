import csv
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==========================
# 🔧 CONFIGURABLE CONSTANTS
# ==========================

SCROLL_PAUSE_TIME = 2
SCROLL_RETRY_LIMIT = 3
WAIT_TIME = 10
EXPAND_WAIT_TIME = 2
LESSON_EXTRACTION_WAIT = 2
COURSE_NAVIGATION_WAIT = 5
SECTION_SCROLL_WAIT = 1

CHROME_PROFILE_PATH = "user-data-dir=~/.config/google-chrome/Profile 1"
CHROME_DEBUG_ADDRESS = "127.0.0.1:9222"

COURSE_SECTION_SELECTOR = '[data-purpose^="section-panel-"]'
COURSE_EXPAND_BUTTON_SELECTOR = "svg[aria-hidden='true']"
COURSE_HEADING_SELECTOR = '[data-purpose="section-heading"]'
LESSON_ITEM_SELECTOR = '[data-purpose^="curriculum-item-"]'
LESSON_TITLE_SELECTOR = '[data-purpose="item-title"], span.section--item-title--EWIuI'
LESSON_DURATION_SELECTOR = "div.curriculum-item-link--metadata--XK804 span"

GO_TO_COURSE_BUTTON_SELECTOR = "//button[@data-purpose='buy-this-course-button']"

OUTPUT_MARKDOWN_FILE = "course_scrape.md"
OUTPUT_CSV_FILE = "course_scrape.csv"

# ==========================
# 🚀 START SELENIUM DRIVER
# ==========================

options = webdriver.ChromeOptions()
options.add_argument(CHROME_PROFILE_PATH)
options.add_experimental_option("debuggerAddress", CHROME_DEBUG_ADDRESS)

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, WAIT_TIME)

markdown_data = []
csv_data = []

# ==========================
# 📜 IMPROVED SCROLL FUNCTION
# ==========================

def human_like_scroll():
    """Scroll until no new content loads, checking if new sections appear."""
    last_sections_count = len(driver.find_elements(By.CSS_SELECTOR, COURSE_SECTION_SELECTOR))
    attempts = 0

    while attempts < SCROLL_RETRY_LIMIT:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)

        new_sections_count = len(driver.find_elements(By.CSS_SELECTOR, COURSE_SECTION_SELECTOR))

        if new_sections_count == last_sections_count:
            attempts += 1
            print(f"🛑 No new sections detected. Trying again ({attempts}/{SCROLL_RETRY_LIMIT})...")
        else:
            print(f"✅ New sections detected! Resetting scroll attempts.")
            attempts = 0

        last_sections_count = new_sections_count

# ==========================
# 🎯 CLICK "GO TO COURSE"
# ==========================

def click_go_to_course():
    """Click the 'Go to Course' button if available."""
    try:
        go_to_course_btn = wait.until(EC.element_to_be_clickable((By.XPATH, GO_TO_COURSE_BUTTON_SELECTOR)))
        go_to_course_btn.click()
        print("🎯 Clicked 'Go to Course' button.")
        time.sleep(COURSE_NAVIGATION_WAIT)
    except Exception:
        print("⚠️ 'Go to Course' button not found or already on the course page.")

# ==========================
# 📂 EXPAND COURSE SECTIONS
# ==========================

def expand_sections():
    """Expand all course sections except the first one."""
    driver.execute_script("window.scrollTo(0, 0)")

    try:
        sections = driver.find_elements(By.CSS_SELECTOR, COURSE_SECTION_SELECTOR)
        print(f"🔄 Found {len(sections)} sections.")

        for i, section in enumerate(sections):
            if i == 0:
                print(f"📂 Skipping section {i+1} (already expanded).")
                continue

            try:
                expand_button = section.find_element(By.CSS_SELECTOR, COURSE_EXPAND_BUTTON_SELECTOR)
                driver.execute_script("arguments[0].scrollIntoView();", expand_button)
                time.sleep(SECTION_SCROLL_WAIT)
                expand_button.click()
                print(f"📂 Expanded section {i+1}")
                time.sleep(EXPAND_WAIT_TIME)
            except Exception:
                print(f"⚠️ Could not expand section {i+1} (might already be open).")

    except Exception as e:
        print(f"❌ Error finding sections: {e}")

# ==========================
# 📖 SCRAPE LESSONS & EXPORT DATA
# ==========================

def scrape_lessons(course_title):
    """Extract lessons and durations correctly and format Markdown properly."""
    try:
        sections = driver.find_elements(By.CSS_SELECTOR, COURSE_SECTION_SELECTOR)
        print(f"📖 Found {len(sections)} sections.")

        for section in sections:
            try:
                # Extract section title and clean it
                section_title_raw = section.find_element(By.CSS_SELECTOR, COURSE_HEADING_SELECTOR).text.strip()
                section_lines = section_title_raw.split("\n")
                section_title = section_lines[0]  # ✅ KEEP ONLY FIRST LINE
                section_duration = "N/A"

                # If there's a second line, check if it contains a time duration
                if len(section_lines) > 1 and re.search(r"\d+h \d+min|\d+min", section_lines[1]):
                    section_duration = section_lines[1]  # ✅ Extract section total duration

                print(f"📚 Section: {section_title} (Duration: {section_duration})")
                markdown_data.append(f"\n## 📚 {section_title} (Duration: {section_duration})\n")

                lessons = section.find_elements(By.CSS_SELECTOR, LESSON_ITEM_SELECTOR)
                if not lessons:
                    print("   ❌ No lessons found.")
                    continue

                for lesson in lessons:
                    try:
                        lesson_title = lesson.find_element(By.CSS_SELECTOR, LESSON_TITLE_SELECTOR).text.strip()

                        # ✅ Extract correct lesson duration
                        duration_elements = lesson.find_elements(By.CSS_SELECTOR, LESSON_DURATION_SELECTOR)
                        lesson_duration = duration_elements[-1].text.strip() if duration_elements else "N/A"

                        print(f"   🎓 {lesson_title} ({lesson_duration})")
                        markdown_data.append(f"- 🎓 {lesson_title} ({lesson_duration})")

                        csv_data.append([course_title, section_title, section_duration, lesson_title, lesson_duration])

                    except Exception as e:
                        print(f"   ⚠️ Skipping lesson due to error: {e}")

            except Exception as e:
                print(f"⚠️ Error extracting section details: {e}")

    except Exception as e:
        print(f"❌ Error finding lessons: {e}")

# ==========================
# 🔍 MAIN EXECUTION LOOP
# ==========================

course_urls = [
    "https://www.udemy.com/machine-learning-for-absolute-beginners/learn/v4/",
    "https://www.udemy.com/learn-big-data-the-hadoop-ecosystem-masterclass/learn/v4/",
    "https://www.udemy.com/machine-learning-for-beginners/learn/v4/",
    "https://www.udemy.com/complete-python-masterclass/learn/v4/",
    "https://www.udemy.com/learn-aws-the-hard-way/learn/v4/",
    "https://www.udemy.com/the-ultimate-python-programming-course/learn/v4/",
    "https://www.udemy.com/the-complete-python-postgresql-developer-course/learn/v4/",
    "https://www.udemy.com/learn-construct-2-creating-an-action-platformer-in-html5/learn/v4/",
    "https://www.udemy.com/learn-cloud-computing-with-aws/learn/v4/",
    "https://www.udemy.com/learn-kubernetes-from-a-devops-kubernetes-guru/learn/v4/"
]

for course_url in course_urls:
    print(f"\n🔍 Navigating to: {course_url}")
    driver.get(course_url)
    human_like_scroll()
    click_go_to_course()
    expand_sections()

    course_title = driver.title.split("|")[0].strip()
    scrape_lessons(course_title)

# ==========================
# 📝 WRITE TO MARKDOWN FILE
# ==========================

with open(OUTPUT_MARKDOWN_FILE, "w", encoding="utf-8") as md_file:
    md_file.write("# 📚 Udemy Course Scrape Results\n\n")
    md_file.write("\n".join(markdown_data) + "\n")

# ==========================
# 📄 WRITE TO CSV FILE
# ==========================

with open(OUTPUT_CSV_FILE, "w", newline="", encoding="utf-8") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["Course", "Section", "Section Duration", "Lesson", "Lesson Duration"])
    writer.writerows(csv_data)

print(f"✅ CSV & Markdown export complete!")

driver.quit()
