import requests
from bs4 import BeautifulSoup
import os
import json

# Load the JSON data from the file
with open("./json_data/course_codes.json", 'r') as file:
    courses = json.load(file)

# Create a list of course codes
course_codes = []

for course in courses:
    course_code = list(course.keys())[0]
    course_codes.append(course_code)

# URL for open sections of classes for each course type
url_beg = "https://app.testudo.umd.edu/soc/search?courseId="
url_end = "&sectionId=&termId=202408&_openSectionsOnly=on&creditCompare=%3E%3D&credits=0.0&courseLevelFilter=ALL&instructor=&_facetoface=on&_blended=on&_online=on&courseStartCompare=&courseStartHour=&courseStartMin=&courseStartAM=&courseEndHour=&courseEndMin=&courseEndAM=&teachingCenter=ALL&_classDay1=on&_classDay2=on&_classDay3=on&_classDay4=on&_classDay5=on"


# Creates bs4 parsed html for each testudo page
for course in course_codes:
    url = url_beg + course + url_end
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    file_path = os.path.join("testudo_course_data", course + '.html')
    with open(file_path, "w") as file:
        file.write(soup.prettify())
