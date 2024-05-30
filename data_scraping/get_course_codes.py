import requests
from bs4 import BeautifulSoup
import os
import json

# Hardcoded course codes to avoid (masters + honors programs not applicable to most students)
# Lost my sanity doing this ;-;
hard_coded_avoid_courses = ['ABRM', 'AGNR', 'AMSC', 'ARMY', 'ARSC', 'BIOI', 
                            'BMSO', 'BSCI', 'BSST', 'BUAC', 'BUDT', 'BUFN',
                            'BULM', 'BUMK', 'BUSI', 'BUSM', 'BUSO', 'CBMG',
                            'CHPH', 'CLFS', 'CPBE', 'CPCV', 'CPDJ', 'CPET',
                            'CPGH', 'CPJT', 'CPMS', 'CPPL', 'CPSA', 'CPSF',
                            'CPSG', 'CPSN', 'CPSP', 'CPSS', 'EDCP', 'EDHD',
                            'EDHI', 'EDMS', 'EDSP', 'EDUC', 'EMBA', 'ENCO',
                            'ENPM', 'ENRE', 'ENSE', 'ENTM', 'ENTS', 'EPIB',
                            'FGSM', 'FIRE', 'GBHL', 'GEMS', 'HACS', 'HBUS',
                            'HDCC', 'HESI', 'HGLO', 'HHUM', 'HLSC', 'HNUH',
                            'HONR', 'MEES', 'MIEH', 'MITH', 'MLAW', 'MLSC',
                            'MOCB', 'MSML', 'MSQC', 'MUSC', 'NAVY', 'NIAS',
                            'PEER', 'PHPE', 'PHSC', 'RDEV', 'RELS', 'SLAA',
                            'SLLC', 'SMLP', 'SPHL', 'SURV', 'TDPS', 'TLPL',
                            'TLTC', 'UMEI', 'URSP', 'USLT', 'VMSC', 'WEID', 
                            'XPER', 'INAG'] # oopsies forgot one

# Parse testudo site
response = requests.get("https://app.testudo.umd.edu/soc/")
soup = BeautifulSoup(response.text, 'html.parser')

# Find all the div elements that have a class 'course-prefix'
course_divs = soup.find_all('div', class_='course-prefix')

course_codes = []
# Loop through each div and extract the course code and name
for div in course_divs:
    course_code = div.find('span', class_='prefix-abbrev').text.strip()  # Extracting text and removing extra spaces
    if course_code in hard_coded_avoid_courses:
        continue
    course_name = div.find('span', class_='prefix-name').text.strip()  # Extracting course name similarly
    course = { course_code: course_name}
    course_codes.append(course)


print(course_codes)

file_path = os.path.join("json_data", 'course_codes.json')
with open(file_path, 'w') as json_file:
    json.dump(course_codes, json_file, indent=4)