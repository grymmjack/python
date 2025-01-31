import csv
import requests

# Base URL for Udemy Affiliate API
BASE_URL = "https://www.udemy.com/api-2.0/courses/"

# List of course IDs (you can find the course ID in the URL of the course)
course_ids = [
    "machine-learning-for-absolute-beginners",
    "learn-big-data-the-hadoop-ecosystem-masterclass",
    "machine-learning-for-beginners",
    "complete-python-masterclass"
]

# Prepare the data storage
markdown_data = []
csv_data = []

# Function to fetch course details using Udemy Affiliate API
def get_course_details(course_id):
    """Fetch course details from the Udemy Affiliate API."""
    url = f"{BASE_URL}{course_id}/"
    
    # Making a GET request to the Udemy API
    response = requests.get(url)
    
    if response.status_code == 200:
        course = response.json()
        return course
    elif response.status_code == 403:
        print(f"⚠️ Access forbidden for course {course_id} (403 error).")
        return None
    elif response.status_code == 404:
        print(f"⚠️ Course {course_id} not found (404 error).")
        return None
    else:
        print(f"⚠️ Error fetching data for course {course_id}: {response.status_code}")
        return None

# Function to scrape lessons and sections from the course data
def scrape_lessons(course):
    """Extract lessons and sections from the course and format Markdown and CSV."""
    course_title = course['title']
    course_description = course.get('headline', 'No description available')
    print(f"📖 Scraping course: {course_title}")
    
    markdown_data.append(f"# {course_title}\n")
    markdown_data.append(f"**Description**: {course_description}\n\n")

    # Check if 'sections' exist in the course response
    if 'sections' in course:
        for section in course['sections']:
            section_title = section['title']
            section_duration = section.get('duration', 'N/A')  # Default to 'N/A' if no duration

            markdown_data.append(f"## 📚 {section_title} (Duration: {section_duration})\n")
            
            for lesson in section.get('lessons', []):
                lesson_title = lesson['title']
                lesson_duration = lesson.get('duration', 'N/A')  # Default to 'N/A' if no duration

                markdown_data.append(f"- 🎓 {lesson_title} ({lesson_duration})")
                csv_data.append([course_title, section_title, section_duration, lesson_title, lesson_duration])
    else:
        print(f"⚠️ No sections available for course {course_title}")

# Loop through course IDs and fetch course data
for course_id in course_ids:
    print(f"\n🔍 Fetching data for: {course_id}")
    
    course = get_course_details(course_id)
    if course:
        scrape_lessons(course)

# Write results to Markdown and CSV
with open("course_scrape.md", "w", encoding="utf-8") as md_file:
    md_file.write("# 📚 Udemy Course Scrape Results\n\n")
    md_file.write("\n".join(markdown_data) + "\n")

with open("course_scrape.csv", "w", newline="", encoding="utf-8") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["Course", "Section", "Section Duration", "Lesson", "Lesson Duration"])
    writer.writerows(csv_data)

print(f"✅ CSV & Markdown export complete!")
