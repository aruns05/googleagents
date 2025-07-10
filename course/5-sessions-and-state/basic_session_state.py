import uuid
import asyncio
from dotenv import load_dotenv
from google.adk.runners import Runner
#from google.adk.sessions import InMemorySessionService
from google.genai import types
from question_answering_agent import question_answering_agent

from google.adk.sessions import DatabaseSessionService
from google.adk.sessions import InMemorySessionService

load_dotenv()

async def main():
    
    DB_HOST = "34.30.106.150" # e.g., '127.0.0.1' for proxy, or public IP
    DB_USER = "arun"
    DB_PASSWORD = "Mayurvihar@011"
    DB_NAME = "pdlc" # e.g., 'pdlc' if that's your database name
    DB_PORT = "5432" # Default PostgreSQL port

    connection_string = (
        f"host={DB_HOST} "
        f"dbname={DB_NAME} "
        f"user={DB_USER} "
        f"password={DB_PASSWORD} "
        f"port={DB_PORT}"
    )
    
       # Create a NEW session
    APP_NAME = "arunsridhar"
    USER_ID = "arun_s05"
    SESSION_ID = str(uuid.uuid4())
    

    # Create a new session service to store state
    #session_service_stateful = InMemorySessionService()

    session_service_stateful = DatabaseSessionService(
            #db_url="sqlite:///sample.db"
            db_url = connection_string
        )
        
    initial_state = {
        "user_name": "Arun Sridhar",
        "user_preferences": """
            I like to play Cricket,Tennis.
            My favorite food is Indian.
            My favorite reastaurant in USA is Chipotle. I like rice bowl there
            My favorite TV show is Mahabharat.
            Loves it when people like and subscribe to his YouTube channel.
        """,
    }

 
    
    # Check if we have an existing session for this user
    # existing_sessions = await session_service_stateful.list_sessions(
    #     app_name=APP_NAME,
    #     user_id=USER_ID
    # )
    
    # This prints existing sessions
    # for session in existing_sessions.sessions:
    #     print(session)
    
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
    session = await session_service_stateful.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )

    # Log final Session state
    print("=== Final Session State ===")
    
    #Looping through events
    for event in session.events:
        print(event.author)  #This gives the agent name
        # Events have content, which have parts, which have text.
        if event.content and event.content.parts:
            # Use a list comprehension to join all parts' text.
            full_text = "".join(part.text for part in event.content.parts)
            print(full_text)

    
    #save_to_db(app_name,session_id,user_id,f)
    
if __name__ == "__main__":
    asyncio.run(main())