# ----------------------------------------- BASIC IMPORTS ----------------------------------------- 
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId
import json
from pathlib import Path
from pprint import pprint
from transcript_parser import parse_transcript
import requests
from functions import *

# ----------------------------------------- LANGCHAIN IMPORTS ----------------------------------------- 

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.text_splitter import RecursiveCharacterTextSplitter, RecursiveJsonSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain, create_history_aware_retriever, create_retrieval_chain
from langchain_community.chat_models import ChatOllama
from langchain.memory import ChatMessageHistory, ConversationBufferMemory
from langchain_community.document_loaders import PyPDFDirectoryLoader, JSONLoader, WebBaseLoader, TextLoader
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.messages import HumanMessage, AIMessage


# ----------------------------------------- SETUP -----------------------------------------

# Groq Client
llm_groq = ChatGroq(
    model_name = "mixtral-8x7b-32768",
    temperature = 0
)

# ----------------------------------------- DICT OF FUNCTIONS ----------------------------------------- 
function_list = {
    "get_schedule": {
        "description": """This function creates a schedule based on the list of courses inputted.
                            How to call: get_schedule([LIST OF COURSE CODES])
                        """,
        "function": get_schedule,
    },
    "get_professor_summary": {
        "description": """This function creates a summary of the professor based on their name. 
                            Call this function if someone asks about a person.
                            How to call: get_professor_summary("NAME OF PROFESSOR")""",
        "function": get_professor_summary,
    },
    "get_course_information": {
        "description": """This function gets the information for a given course.
                            How to call: get_course_information("COURSE CODE")""",
        "function": get_course_information,
    },
    "get_all_sections": {
        "description": """This function gets information regarding open sections for a given course
                            How to call: get_all_sections("COURSE CODE")""",
        "function": get_all_sections,
    },
    "get_general_response": {
        "description": """This function gets a response to inquiries that don't have a specific function
                            assigned to them. The QUERY parameter refers to the initial user inquiry, 
                            and should never be changed or altered in any way.
                            How to call: get_general_response("QUERY")""",
        "function": get_general_response
    }
}

# ----------------------------------------- FUNCTION CALLER CLASS ----------------------------------------- 

class FunctionCaller: 
    # Initializes attributes and function caller system prompt
    def __init__(self):
        self.client = Groq()
        self.retrieval_chain = None
        self.chat_history = []
        self.prompt = f"""
        You are a function caller that parses natural language queries,
        calling the appropriate function to help the user.
        Your only job is to call a function based on the function list provided, 
        which will generate a response to user inquiries.
        
        These are the available functions and their descriptions:
        {[f"{func}: {function_list[func]['description']}" for func in function_list.keys()]}
        
        You will respond in this format:
            {{ "function": "NAME OF FUNCTION", "args": ["LIST OF ARGUMENTS SEPERATED BY COMMAS"] }}
            
        Here are some rules for your response:
            1) Only respond with a function call
            2) Follow the format exactly as described
            3) Only call the available functions
            4) Any user query that gets passed into get_general_response should not be changed, and the original query should be passed
            5) NEVER DIRECTLY RESPOND TO USER INQUERIES, ONLY OUTPUT A FUNCTION CALL

        Example format:
            {{ "function": "get_schedule", "args": [["CMSC330", "CMSC351", "ENGL101"]] }}
            {{ "function": "get_professor_summary", "args": ["Nelson Padua-Perez"] }}
            {{ "function": "get_course_information", "args": ["CMSC330"] }}
            {{ "function": "get_all_sections", "args": ["CMSC330"] }}
            {{ "function": "get_general_response", "args": ["hello, how are you doing?"] }}
        
        Example conversions of inquiries to function calls:
            user: "Introduce yourself" -> {{ "function": "get_general_response", "args": ["Introduce yourself"] }}
            user: "What classes should I take?" -> {{ "function": "get_general_response", "args": ["What classes should I take?"] }}
            user: "Tell me about CMSC330" -> {{ "function": "get_course_information", "args": ["CMSC330"] }}
            user: "What sections are available for CMSC330 next semester?" {{ "function": "get_all_sections", "args": ["CMSC330"] }}
            user: How is Nelson Padua-Perez? -> {{ "function": "get_professor_summary", "args": ["Nelson Padua-Perez"] }}
        
        """

# +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
    
    # Takes query and outputs response from LLM
    def answer_query(self, query):
        # Convert query to function call
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": self.prompt
                },
                {
                    "role": "user",
                    "content": query,
                }
            ],
            model="mixtral-8x7b-32768",
        )
        response = chat_completion.choices[0].message.content
        
        # Stupid LLM apparently can't follow simple formatting instructions
        response = remove_backslashes(response)
        
        # DEBUGGING
        print("") 
        print("------------- FunctionCaller Response ------------- ")
        print("")
        print("User Query:", query)
        print("")
        print("Function Caller Response:", response)
        print("")
        
        
        # Convert response to actual function call
        response_dict = json.loads(response)
        function_name = response_dict["function"]
        args = response_dict["args"]
        
        # Call the function
        if function_name in function_list:
            function_to_call = function_list[function_name]["function"]
            
            # Pass in Retrieval Chain for general query
            if function_name == 'get_general_response':
                args.append(self.retrieval_chain)
                # It's important to pass in chat_history in order to invoke retrieval chain
                args.append(self.chat_history)
            
            result = function_to_call(*args)
            self.chat_history.append(HumanMessage(content=query))
            self.chat_history.append(AIMessage(content=result))
            
            # DEBUGGING
            print("Chat History:")
            print("")
            for chat in self.chat_history:
                print(chat)
                print("")
            print("----------------------------------------------------")
            print("")
            return(result)

# +=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
    
# Creates retrieval chain based on the relevent json data, and outputs an introduction message
    def process_transcript(self):
        # Combine JSON documents and load the data
        combine_json_data()
        json_data = read_json_file("./data/combined_data.json")
        
        # Split documents into chunks
        json_splitter = RecursiveJsonSplitter(max_chunk_size=1200)
        docs = json_splitter.create_documents(texts=[json_data])
        
        # Load CS Graduation Requirements
        loader = TextLoader('./data/CMSC_grad_reqs.txt')
        grad_req_docs = loader.load()
        docs += grad_req_docs
        
        # Use embedding function on document chunks, storing vectors in a Chroma vectorstore
        embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = Chroma.from_documents(docs, embedding_function)
        
        # Create retriever chain to search for relevant documents through the Chroma vectorstore
        retriever = vectorstore.as_retriever()
        prompt = ChatPromptTemplate.from_messages([
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            ("user", "Given the above conversation, generate a search query to get information relevant to the conversation")
        ])   
        retriever_chain = create_history_aware_retriever(llm_groq, retriever, prompt)
        
        # System message to set up RAG context
        template = """
        You are a virtual advisor for a UMD student, and should refer to yourself with the name TerpPal.
        Your job is to answer user queries regarding class suggestions, graduation requirements, etc. 
        You should answer user queries to the best of your abilities based off of the context provided:
        
        <context>
        {context}
        </context>
        
        Follow these rules when responding:
        1) Make sure to use at least 3 turtle emojis
        2) Talk in a friendly tone
        3) Assume whatever information you have regarding CS degree requirements at UMD are up to date
        """
        
        # Create prompt that loads the system message, chat history, and afterwards takes user input
        prompt = ChatPromptTemplate.from_messages([
            ("system", template),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ])
        document_chain = create_stuff_documents_chain(llm_groq, prompt)
        
        for doc in document_chain:
            print(doc)
        
        # Chains retrieved document into document chain, answering inqueries based on retrieved documents
        self.retrieval_chain = create_retrieval_chain(retriever_chain, document_chain)
        
        # Invokes response for introduction
        introduction = get_general_response("Introduce yourself, list CS courses the student has completed, and suggest any recommendations for classes to take next semester", self.retrieval_chain, self.chat_history)
        
        return introduction
        
        

# ----------------------------------------- AUXILARY FUNCTIONS -----------------------------------------

# Read json file
def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Write data to json file
def write_json_file(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Combine all json files for RAG context
def combine_json_data():
    # Directory containing the JSON files
    directory_path = './data'

    # Dictionary to hold all the data
    combined_data = {}

    # Create key-value pair for transcript data
    transcript_path = os.path.join(directory_path, 'transcript_data.json')
    combined_data['Student Transcript Data'] = read_json_file(transcript_path)
    
    # ----------------------- ADD DEGREE REQS DATA ----------------------- 
    
    # Write combined data to a new JSON file
    output_path = os.path.join(directory_path, "combined_data.json")
    write_json_file(combined_data, output_path)
    print("Data combined successfully!")

# Removes backslashes from function caller's inability to follow simple instructions
def remove_backslashes(input_string):
    # Replace all backslashes with an empty string
    cleaned_string = input_string.replace("\\", "")
    return cleaned_string


# ----------------------------------------- TESTING ----------------------------------------- 
if __name__ == "__main__":
    # TESTING FUNCTIONALITY
    fc = FunctionCaller()
    # fc.process_transcript()
    # print(fc.answer_query("Tell me about GEOL100"))
    # print(fc.answer_query("What sections are available for GEOL100?"))
    print(fc.answer_query("How is Nelson Padua-Perez?"))
    # print(fc.answer_query("Should I take this class?"))
    # for chat in fc.chat_history:
    #     print(chat)
    

