# TerPal: Virtual Advisor for UMD Computer Science Students

TerPal is a virtual advisor designed to assist University of Maryland (UMD) students studying computer science. It provides guidance on class selection, graduation requirements, and other academic matters.

## Features

- **Class Recommendations**: Offers personalized class recommendations based on academic progress and interests.
- **Graduation Tracking**: Helps track progress towards graduation requirements and suggests suitable courses.
- **Schedule Planning**: Assists in planning course schedules for upcoming semesters.
- **Resource Recommendations**: Provides links to relevant resources, such as tutoring services, career development resources, and student organizations.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Ethan-Grammer/TerPal.git
   cd TerPal
   ```

2. **Install Dependencies**:
   ```bash
   npm install
   ```

3.**Start the Flask Proxy Server**:
   Do the following in another terminal
   ```bash
   cd flask_proxy
   python3 flask_server.py
   ```

4. **Start the React App**:
   ```bash
   cd react_client
   npm start
   ```

5. **Access TerPal**
   Upload your transcript to the chatbox and have TerPal answer your questions! (Please don't look at my transcript it's very bad)
   
## Usage

1. **Ask TerPal**: Type your questions or requests into the chatbox and press Enter to get responses from TerPal.
2. **Get Recommendations**: Ask for class recommendations, graduation requirements, or schedule planning assistance.
3. **Save Conversations**: TerPal can save chat histories for future reference.

## File Structure

```
TerPal/
│
├── react_client/
│   ├── public/                  # Public assets and index.html
│   └── src/                     # Source files
│       ├── components/          # React components
│       │   ├── Chatbox.js       # Chatbox component
│       │   └── Chatbox.css      # Chatbox style
│       ├── pages/               # Main pages of the app
│       ├── App.css              # Styles for the app
│       ├── App.js               # Main component
│       └── index.js             # Entry point for the app
│
├── flask_proxy/
│   ├── data/                    # Directory for json and text data used by RAG
│   ├── uploads/                 # Directory for user uploads
│   ├── flask_server.py          # Backend proxy server
│   ├── parse_transcript.py      # Parses transcript PDF and sets up RAG context
│   ├── function_caller.py       # Function Caller class
│   └── functions.py             # List of functions used by Function Caller
│
├── data_scraping/
│   ├── json_data/               # Directory for scraped and formatted json data
│   ├── testudo_course_data/     # Directory for HTML pages based on course code
│   ├── get_course_codes.py      # Scrapes course codes from Testudo
│   ├── get_testudo_courses.py   # Stores HTML pages for each course code
│   ├── get_schedule_data.py     # Scrapes schedule data from course HTMLs
│   └── get_professor_data.py    # Returns json of unique professors and their classes/sections
│
├── .gitignore               # Git ignore file
├── package.json             # Package configuration
└── README.md                # Project README
```

## Contributing

If you'd like to contribute to TerPal, fork the repository and create a pull request with your changes. You can also open issues for bug reports or feature requests.

## Credits

TerPal utilizes React for the frontend interface, flask for the backend proxy server, and the Groq, Langchain, and PlanetTerp APIs for setting up a RAG context, gathering professor data, and much more.

## License

This project is licensed under the MIT License.
