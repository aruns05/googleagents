from google.adk.runners import Runner
from google.genai import types
import os
from dotenv import load_dotenv


def get_connection_string() -> str:
    load_dotenv()
    
    DB_HOST=os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD  = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    DB_PORT = os.getenv("DB_PORT") 
    
    connection_string = f"postgresql+pg8000://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return connection_string
    

def get_session_details(user_id,app_name,session_id=None):

    print("This function is a placeholder for get session details")