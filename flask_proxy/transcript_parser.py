import re
import fitz  # PyMuPDF
import os
import json

# Parses the transcript PDF, outputting a json file "transcript_data" with the appropriate data
def parse_transcript(pdf_path):
    
    # Read PDF using PyMuPDF to extract text
    doc = fitz.open(pdf_path)
    transcript_text = ""
    for page in doc:
        transcript_text += page.get_text()
    # print(transcript_text) # DEBUGGING

    # Regular expression to match course information
    course_regex = re.compile(
        r"(?P<course_code>[A-Z]{4}\d{3}[A-Z]?)\s+(?P<title>.+?)\s+(?P<grade>[A-Z]{1,2}[+-]?)\s+(?P<attempted>\d+\.\d+)\s+(?P<earned>\d+\.\d+)\s+(?P<quality>\d+\.\d+)\s+(?P<geneds>(?:(FSAW|FSAR|FSMA|FSOC|FSPW|DSHS|DSHU|DSNS|DSNL|DSSP|DVCC|DVUP|SCIS)(?:, )?)*)",
        re.MULTILINE
    )
    
    # Dictionary to store course information
    elective_courses = {}
    cmsc_courses = {}

    # Extracting course information
    for match in course_regex.finditer(transcript_text):
        course_code = match.group("course_code")
        title = match.group("title")
        
        # Handle repeated courses by retaining the original title
        if "*Repeated Course*" in title:
            if course_code.startswith("CMSC"):
                title = cmsc_courses[course_code]['Title']
            else:
                title = elective_courses[course_code]['Title']
            
        
        # Create json for course information
        if course_code.startswith("CMSC"):  # Check if it's a CMSC course
            cmsc_courses[course_code] = {
                "Title": title,
                "Grade": match.group("grade"),
                "Credits Earned": float(match.group("earned")),
                "Gen Eds": match.group("geneds").split(", ") if match.group("geneds") else []
            }
        else:
            # Create json for course information
            elective_courses[course_code] = {
                "Title": title,
                "Grade": match.group("grade"),
                "Credits Earned": float(match.group("earned")),
                "Gen Eds": match.group("geneds").split(", ") if match.group("geneds") else []
            }

    # Compile the regex patterns for finding semester information
    semester_info_pattern = re.compile(r"(Spring|Summer|Fall|Winter)\s+(\d{4})\s+.*?Semester:\s*Attempted\s*(\d+\.\d+);\s*Earned\s*(\d+\.\d+);\s*QPoints\s*(\d+\.\d+);\s*GPA\s*(\d+\.\d+).*?UG Cumulative:\s*(\d+\.\d+);\s*(\d+\.\d+);\s*(\d+\.\d+);\s*(\d+\.\d+)", re.DOTALL)
    ug_cumulative_pattern = re.compile(r"UG Cumulative:\s*(\d+\.\d+);\s*(\d+\.\d+);\s*(\d+\.\d+);\s*(\d+\.\d+)")

    # Find all semester matches
    semester_info_matches = semester_info_pattern.findall(transcript_text)
    
    # Create a dict of semester information
    semester_info = {}
    for match in semester_info_matches:
        semester_name = f"{match[0]} {match[1]}"
        semester_data = {
            "Details": {
                "Total Credits Attempted": match[2],
                "Earned": match[3],
                "QPoints": match[4],
                "GPA": match[5]
            },
            "Cumulative": {
                "Attempted": match[6],
                "Earned": match[7],
                "QPoints": match[8],
                "GPA": match[9]
            }
        }
        semester_info[semester_name] = semester_data
        
    # Structure the final transcript JSON
    transcript_data = {
        "Student's Completed CMSC courses": cmsc_courses,
        "Student's Completed Elective courses": elective_courses,
        "Student's Semester Information": semester_info
    }
    
    # Save the data to a JSON file in the 'data' directory
    file_path = os.path.join("data", 'transcript_data.json')
    with open(file_path, 'w') as json_file:
        json.dump(transcript_data, json_file, indent=4)

    
if __name__ == '__main__':
    parse_transcript("./uploads/Testudo_-_Unofficial_Transcript.pdf")

