import uuid
import os
import asyncio
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.genai import types
from question_answering_agent import question_answering_agent

from google.adk.sessions import DatabaseSessionService
from google.adk.sessions import InMemorySessionService

from utils import get_session_details, get_connection_string

load_dotenv()

async def main():
        
    # DB_HOST=os.getenv("DB_HOST")
    # DB_USER = os.getenv("DB_USER")
    # DB_PASSWORD  = os.getenv("DB_PASSWORD")
    # DB_NAME = os.getenv("DB_NAME")
    # DB_PORT = os.getenv("DB_PORT") 

    # Create a NEW session
    APP_NAME = "arunsridhar"
    USER_ID = "arun_s05"
    SESSION_ID = str(uuid.uuid4())
    
    # --- Create the Connection String ---
    connection_string = get_connection_string() 
    #connection_string=f"postgresql+pg8000://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Create a new session service to store state in internal memory
    #session_service_stateful = InMemorySessionService()
    
    # Create a new session service to store state in external DB
    session_service_stateful = DatabaseSessionService(
            #db_url="sqlite:///sample.db"
            db_url = connection_string
        )
        
    initial_state = {
        "user_name": "Arun Sridhar",
        "user_preferences": """
            I like to play Cricket,Tennis.
            My favorite food is Indian.
            My favorite reastaurant in USA is Chipotle. I like rice bowl there with protein and guacamole.
            My favorite TV show is Mahabharat.
            Loves it when people like and subscribe to his YouTube channel.
        """,
    }

    # Check if we have an existing session for this user
    existing_sessions = await session_service_stateful.list_sessions(
        app_name=APP_NAME,
        user_id=USER_ID
    )
    
    #This prints existing sessions
    print("EXISTING SESSIONS:")
    for session in existing_sessions.sessions:
        print(session)
    
    stateful_session =  await session_service_stateful.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state=initial_state,
    )
    print("CREATED NEW SESSION:")
    print(f"\tSession ID: {SESSION_ID}")

    runner = Runner(
        agent=question_answering_agent,
        app_name=APP_NAME,
        session_service=session_service_stateful,
    )

    new_message = types.Content(
        role="user", parts=[types.Part(text="What is Arun's favorite restaraunt in USA?")]
    )

    for event in runner.run(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=new_message,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                print(f"Final Response: {event.content.parts[0].text}")
        else:
            print(f"Event: {event}")

    print("==== Session Event Exploration ====")
    # session = await session_service_stateful.get_session(
    #     app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    # )

    # Log final Session state
    print("=== Final Session State ===")
    
    #Looping through events
    for event in stateful_session.events:
        print(event.author)  #This gives the agent name
        # Events have content, which have parts, which have text.
        if event.content and event.content.parts:
            # Use a list comprehension to join all parts' text.
            full_text = "".join(part.text for part in event.content.parts)
            print(full_text)
    
if __name__ == "__main__":
    asyncio.run(main())
    
    
# select * from app_states
# select * from events
# select state from sessions

# select * from user_states