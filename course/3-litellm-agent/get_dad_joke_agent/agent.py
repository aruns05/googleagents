from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.models.lite_llm import LiteLlM
import time
import os
import random

from dotenv import load_dotenv

# Load environment variables from the .env file (if present)
load_dotenv()

# Access environment variables as if they came from the actual environment
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


model = LiteLlM(
    model = "gpt-4o", 
    api_key=OPENAI_API_KEY
)
def get_dad_joke()->str:
    print("Getting a dad joke...")
    jokes =[
      "Why did the scarecrow win an award? Because he was outstanding in his field!",  
      "I told my wife she was drawing her eyebrows too high. She looked surprised.",
      "I used to play piano by ear, but now I use my hands.",
      "Why don't skeletons fight each other? They don't have the guts.",
    ]
    return random.choice(jokes)
        
root_agent = Agent(
    name="get_dad_joke_agent",
    model=model,
    description="Agent to send jokes about different people",
    instruction="""You are a helpful assistant that uses the following tools
     get_dad_joke to get jokes on dad.""",
    tools=[get_dad_joke]
)

# root_agent = Agent(
#     name="tool_agent",
#     model="gemini-2.0-flash",
#     description="Greeting agent",
#     instruction="""You are a helpful assistant that uses the following tools
#     google_search    
#     """,
#     tools=[google_search],
# )