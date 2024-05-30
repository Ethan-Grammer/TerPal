import os
import json
from bs4 import BeautifulSoup
import re
import json

# JSON reader
def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Dict for professor name and their classes
professor_info = {}

# Loop through schedule data to find professor names
schedule_data = read_json_file("./json_data/schedule_data.json")
# Gets department code, and courses from schedule_data
for dept_code, courses in schedule_data.items():
    # Gets course id
    for course_id in courses:
        course = courses[course_id]
        sections = course['sections']
        # Loops through all sections, finding professor and section info
        for section_id, section in sections.items():
            professor = section['instructor']
            if(professor == 'TBA'):
                continue
            # Adds to lists if professor is already in database
            if professor in professor_info:
                if course_id in professor_info[professor]['Courses']:
                    professor_info[professor]['Courses'][course_id]['Sections'].append(section_id)
                else:
                    professor_info[professor]['Courses'][course_id] = {'Sections': [section_id]}
            
            # Creates new entry in database for professor
            else:
                professor_info[professor] = {'Courses': {course_id : {'Sections' : [section_id]}}}

file_path = os.path.join("./json_data", 'professor_data.json')
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(professor_info, f, ensure_ascii=False, indent=4)

file_path = os.path.join("../flask_proxy/data", 'professor_data.json')
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(professor_info, f, ensure_ascii=False, indent=4)
    
# # DEBUGGING
# professor_data = read_json_file("./json_data/professor_info.json")
# for professor in professor_data:
#     print(professor)


            
        