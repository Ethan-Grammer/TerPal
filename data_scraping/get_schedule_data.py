import os
import json
from bs4 import BeautifulSoup
import re

def parse_html_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
    
    courses_data = {}

    for course_div in soup.find_all('div', class_='course'):
        # Gets course ID
        course_id = course_div.find('div', class_='course-id').text.strip()

        # Skips over graduate level courses
        course_num_match = re.search(r'\d+', course_id)
        course_num = int(course_num_match.group())
        if(course_num > 499):
            continue
        
        # Gets course title and credits
        course_title = course_div.find('span', class_='course-title').text.strip()
        course_credits = course_div.find('span', class_='course-min-credits').text.strip()
        
        # Skips over research + independent study courses as they aren't relevant 
        if(course_div.find('span', class_='course-max-credits')):
            continue
        
        # Initializes prerequisite, restriction, crosslist, and course description information
        texts_container = course_div.find('div', class_='approved-course-texts-container')
        prerequisites, restrictions, crosslisted_as, credit_granted_for, course_description = "None listed", "No restrictions", "Not cross-listed", "No specific credits granted", []

        # Searches container for the above information
        if texts_container:
            text_blocks = texts_container.find_all('div', class_='approved-course-text')
            for text_div in text_blocks:
                if text_div.find('strong'):  # This div contains specific labels like Prerequisite
                    strong_tags = text_div.find_all('strong')
                    for tag in strong_tags:
                        label_text = tag.text.strip()
                        next_text = tag.find_next_sibling(string=True).strip()
                        if 'Prerequisite:' in label_text:
                            prerequisites = next_text
                        elif 'Restriction:' in label_text:
                            restrictions = next_text
                        elif 'Cross-listed with:' in label_text:
                            crosslisted_as = next_text
                        elif 'Credit only granted for:' in label_text:
                            credit_granted_for = next_text
                else:
                    # General course description
                    course_description.append(text_div.text.strip())
            course_description = ' '.join(course_description)  # Combine all description parts into one string
        else:
            course_description = "No description available"

        # Obtains section information
        sections = {}
        for section_div in course_div.find_all('div', class_='section delivery-f2f'):
            # Gets section ID
            section_id = section_div.find('span', class_='section-id').text.strip()
            
            # Gets section instructor name, filtering the TBA format if applicable
            instructor = section_div.find('span', class_='section-instructor').text.strip()
            if instructor.startswith("Instructor: "):
                instructor = instructor.replace("Instructor: ", "")

            # Gets section seat information
            seats_info_element = section_div.find('span', class_='seats-info')
            total_seats = seats_info_element.find('span', class_='total-seats-count').text.strip() if seats_info_element.find('span', class_='total-seats-count') else "0"
            open_seats = seats_info_element.find('span', class_='open-seats-count').text.strip() if seats_info_element.find('span', class_='open-seats-count') else "0"
            waitlist_count = seats_info_element.find('span', class_='waitlist-count').text.strip() if seats_info_element.find('span', class_='waitlist-count') else "0"
            seats_info = f"Total: {total_seats}, Open: {open_seats}, Waitlist: {waitlist_count}"
            
            # print(course_id, "section", section_id) # DEBUGGING
            
            # Gets all section days + times:
            section_times_locations = []
            section_time_div = section_div.find('div', class_='class-days-container')
            for time in section_time_div.find_all('div', class_='row'):
                time_info = {}
                location = {}
                # Checks to see if class is in person or online
                if time.find('span', class_='section-days'):
                    # Checks to see if class times have been determined or TBA
                    if time.find('span', class_='class-start-time'):
                        time_info = {
                            'days': time.find('span', class_='section-days').text.strip(),
                            'start_time': time.find('span', class_='class-start-time').text.strip(),
                            'end_time': time.find('span', class_='class-end-time').text.strip()
                        }
                    # Class time is TBA
                    else:
                        time_info = {'section_time': time.find('span', class_='section-days').text.strip()}
                # Class is online, and thus class time/details are on ELMS    
                elif time.find('span', class_='elms-class-message'):
                    time_info = {'section_time': time.find('span', class_='elms-class-message').text.strip()}
                    
                building_code = time.find('span', class_='building-code').text.strip() if time.find('span', class_='building-code') else ""
                class_room = time.find('span', class_='class-room').text.strip() if time.find('span', class_='class-room') else "No room number"
                location = f"{building_code} {class_room}" if building_code and class_room else "Location not listed"
                
                section_times_locations.append({
                    'time_info': time_info,
                    'location_info': location
                })
            
            sections[section_id] = {
                'instructor': instructor,
                'seats_info': seats_info,
                'section_times_locations': section_times_locations
            }

        
        course_data = {
            'title': course_title,
            'credits': course_credits,
            'description': course_description,
            'prerequisites': prerequisites,
            'restrictions': restrictions,
            'crosslisted_as': crosslisted_as,
            'credit_granted_for': credit_granted_for,
            'sections': sections
        }
        courses_data[course_id] = course_data

    return courses_data


def main():
    directory = './testudo_course_data'
    all_courses = {}

    # Loop through all HTML files in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            file_path = os.path.join(directory, filename)
            # print("JSONifying", filename) # DEBUGGING
            all_courses[filename[:4]] = parse_html_file(file_path)

    # Write the JSON output
    file_path = os.path.join("../flask_proxy/data", 'schedule_data.json')
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(all_courses, f, ensure_ascii=False, indent=4)
        
    file_path = os.path.join("./json_data", 'schedule_data.json')
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(all_courses, f, ensure_ascii=False, indent=4)
    
    # # TESTING with only CMSC course data
    # filename = "CMSC.html"
    # file_path = os.path.join(directory, filename)
    # all_courses = parse_html_file(file_path)
    # print(parse_html_file(file_path))
    # file_path = os.path.join("./json_data", 'cmsc_courses.json')
    # with open(file_path, 'w', encoding='utf-8') as f:
    #     json.dump(all_courses, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
