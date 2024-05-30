import os
import json
import requests
from groq import Groq
from langchain_core.messages import HumanMessage, AIMessage

client = Groq()
# ----------------------------------------- QUERY FUNCTIONS ----------------------------------------- 

# +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
    
#                               Returns a schedule from a list of classes
    
# +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
def get_schedule(list_of_course_codes):
    course_information = ""
    for course_code in list_of_course_codes:
        course_information += (f"All available sections for {course_code}\n\n" 
                               + get_all_sections(course_code))
    
    schedule = create_schedule(course_information)
    return schedule


# +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
    
#                            Returns professor summary + rating from their name
    
# +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
def get_professor_summary(professor_name):
    
    # Call PlanetTerp API for professor reviews
    professor_data = requests.get(
        "https://planetterp.com/api/v1/professor",
        params={
            "name": professor_name,
            "reviews": "true"
        }
    ).json()
    
    # Create string of reviews, including the course and rating for each review
    review_str = f"Reviews of {professor_name}:\n\n"
    count = 1
    # Professor data from API contains {'courses', 'average_rating', 'type', 'reviews', 'name', 'slug'}
    for review in professor_data['reviews']:
        if(count > 25):
            break
        review_str += (str(f"Review for {review['course']}:") + review['review'] + 
                        "\nRating:" + str(review['rating']) + "\n\n"
                    )
        count += 1
    
    # Create summary of professor based on reviews
    summary = create_professor_summary(review_str)
    
    return summary


# +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
    
#                                     Returns information about a course
    
# +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
def get_course_information(course_code):
    schedule_data = read_json_file("./data/schedule_data.json")
    for dept_code, courses in schedule_data.items():
        if course_code in courses:
            course = courses[course_code]
            course_info = (f"Title: {course['title']}" +
            f"\nCredits: {course['credits']}" + 
            f"\nDescription: {course['description']}" +
            f"\nPrerequisites: {course['prerequisites']}" + 
            f"\nRestrictions: {course['restrictions']}" + 
            f"\nCrosslisted As: {course['crosslisted_as']}" +
            f"\nCredit Granted For: {course['credit_granted_for']}")
            return course_info.strip()
    return "Course not found."


# +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
    
#                                  Returns all section information for a course
    
# +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
def get_all_sections(course_code):
    schedule_data = read_json_file("./data/schedule_data.json")
    all_sections = ""
    for dept_code, courses in schedule_data.items():
        if course_code in courses:
            course = courses[course_code]
            sections = course['sections']
            for section_id in sections:
                section = sections[section_id]
                section_info = (f"Section: {section_id}" +
                                f"\nInstructor: {section['instructor']}" +
                                f"\nSeat Information: {section['seats_info']}"
                                f"\nTimes & Locations: ")
                
                for entry in section['section_times_locations']:
                    section_info += (f"{entry['time_info']['days']} from {entry['time_info']['start_time']}" +
                                    f" to {entry['time_info']['end_time']} at {entry['location_info']}\n        "+
                                    f"           ")
                all_sections += section_info + "\n"
            return all_sections
        
    return "Sections were not found."

# +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
    
#                                  Answers general inquiries using retrieval chain
    
# +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
def get_general_response(message, retrieval_chain, chat_history):
    # Generates AI response through retrieval chain
    response = retrieval_chain.invoke({
        "chat_history": chat_history,
        "input": message
    })
    
    print(response)
    
    return response['answer']


# ----------------------------------------- GENERATIVE FUNCTIONS ----------------------------------------- 

# +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
    
#                               Returns a detailed summary of professor ratings
    
# +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=

def create_professor_summary(review_text):
    context_prompt = f"""
        You are a summary generator. 
        Your job is to analyze professor ratings from PlanetTerp, 
        and create a comprehensive summary of the reviews.
        Specifically mention these three points:
            What people like about the professor
            What people don't like about the professor
            The average rating of the professor
        
    """
    
    chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": context_prompt
                },
                {
                    "role": "user",
                    "content": review_text,
                }
            ],
            model="mixtral-8x7b-32768",
        )
    
    return chat_completion.choices[0].message.content


# +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
    
#                       Returns a comprehensive schedule made up of selected courses
    
# +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=

def create_schedule(course_information):
    context_prompt = f"""
        You are a schedule generator, creating a schedule given a list of courses
        and their sections. Make sure to include every single course and choose sections that don't
        have time conflicts. An ideal schedule would have these classes as close together as possible.
        
        The time and locations for sections will be formatted as below,
        where MWF would represent classes on Monday, Wednesday, and Friday:
            "Times & Locations: MWF from 1:00pm to 1:50pm at ATL 2324"
        
        If you cannot generate a section without overlapping time, 
        respond with "Cannot create schedule due to conflicts, please try again.
        
        
        Otherwise, here is an example of the format you should respond with below:
        
        <format>
        Here is a possible schedule that includes open sections of LIST_OF_CLASSES without any time conflicts:
        
        -Monday
            COURSE_ID (SECTION_ID) from START_TIME to END_TIME at LOCATION
            ...
            COURSE_ID (SECTION_ID) from START_TIME to END_TIME at LOCATION
        -Tuesday:
            COURSE_ID (SECTION_ID) from START_TIME to END_TIME at LOCATION
            ...
            COURSE_ID (SECTION_ID) from START_TIME to END_TIME at LOCATION
        -Wednesday:
            COURSE_ID (SECTION_ID) from START_TIME to END_TIME at LOCATION
            ...
            COURSE_ID (SECTION_ID) from START_TIME to END_TIME at LOCATION
        -Thursday:
            COURSE_ID (SECTION_ID) from START_TIME to END_TIME at LOCATION
            ...
            COURSE_ID (SECTION_ID) from START_TIME to END_TIME at LOCATION
        -Friday:
            COURSE_ID (SECTION_ID) from START_TIME to END_TIME at LOCATION
            ...
            COURSE_ID (SECTION_ID) from START_TIME to END_TIME at LOCATION
        
        It is important to double-check that there are no scheduling conflicts with any other courses or obligations. 
        If there are any issues with this schedule, please let me know and I can try to suggest alternative sections.
        </format>
        
        example of format:
        -Monday:
            CMSC131 (0102) from 9:00am to 9:50am at IRB 0324
            DATA100 (0111) from 10:00am to 10:45am at PHY 4206
            DATA100 (0111) from 11:00am to 11:50am at ESJ 0224
            GEOL100 (0101) from 1:00pm to 1:50pm at ATL 2324
        -Tuesday:
            No classes!
        -Wednesday:
            CMSC131 (0102) from 9:00am to 9:50am at IRB 0324
            DATA100 (0111) from 11:00am to 11:50am at ESJ 0224
            GEOL100 (0101) from 1:00pm to 1:50pm at ATL 2324
        -Thursday:
            No classes!
        -Friday:
            CMSC131 (0102) from 9:00am to 9:50am at IRB 0324
            DATA100 (0111) from 11:00am to 11:50am at ESJ 0224
            GEOL100 (0101) from 1:00pm to 1:50pm at ATL 2324
        
        Here are some rules for your response:
        1) MAKE SURE TO ONLY INCLUDE ONE SECTION FOR EACH COURSE!!
        2) ONLY INCLUDE COURSES GIVEN IN USER INPUT!!
    """
    
    chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": context_prompt
                },
                {
                    "role": "user",
                    "content": course_information,
                }
            ],
            model="mixtral-8x7b-32768",
        )
    
    return chat_completion.choices[0].message.content


# ----------------------------------------- AUXILARY FUNCTIONS ----------------------------------------- 
def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

