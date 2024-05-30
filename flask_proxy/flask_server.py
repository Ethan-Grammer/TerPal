# ----------------------------------------- BASIC IMPORTS ----------------------------------------- 

import os
from dotenv import load_dotenv
from bson.objectid import ObjectId
import json
from pathlib import Path
from pprint import pprint
from transcript_parser import parse_transcript
from function_caller import *


# ----------------------------------------- FLASK IMPORTS ----------------------------------------- 

from flask import Flask, request, jsonify, flash
from flask_pymongo import PyMongo
from flask_cors import CORS
from werkzeug.utils import secure_filename


# ----------------------------------------- SETUP -----------------------------------------

# Flask configurations
app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000  # 16 Megabyte limit

# Initializes FunctionCaller
fc = FunctionCaller()


# ----------------------------------------- ROUTES ----------------------------------------- 

# +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=   
 
#                                  Route for transcript upload
    
# +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=

@app.route('/upload', methods=['POST'])
def upload_file():
    # Attempt to obtain file from request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    
    # Throws error if no file name
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Save file to upload folder
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Parse transcript, adding JSON configuration to data folder
    parse_transcript(filepath)
    
    # Call function to set up RAG chain in FunctionCaller after file is parsed
    response = fc.process_transcript()
    
    return jsonify({'confirmation': 'File successfully uploaded and properly processed!', 'response': response}), 200


# +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
    
#                                   Route for user queries
    
# +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=

@app.route('/chat', methods=['POST'])
def chat():
    # Retrieves user query
    chat = request.json
    query = chat["messages"]  
    
    # Pass user query to FunctionCaller
    response = fc.answer_query(query)
    print(response)
    
    return jsonify({'response': response})


# ----------------------------------------- TESTING ----------------------------------------- 

# Run back end on port 3001
if __name__ == '__main__':
    app.run(debug=True, port=3001)