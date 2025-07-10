import os
import asyncio
import uuid
from dotenv import load_dotenv


from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService

from memory_agent.agent import memory_agent
from utils import call_agent_async

# Load environment variables
load_dotenv()

async def main():
    # Create a database session service
    # This will persist sessions to a SQLite database
    
    # db_path = "sample.db"
    # if not os.path.exists(db_path):
    # # Create an empty SQLite database file
    #     with sqlite3.connect(db_path) as conn:
    #         print(f"Database '{db_path}' created successfully.")

    session_service = DatabaseSessionService(
        db_url="sqlite:///sample.db"
    )
    
    

    # Define initial state for new sessions
    initial_state = {
        "username": "User",
        "reminders": []
    }

    # Application and user identifiers
    app_name = "ReminderApp"
    user_id = "example_user"

    # Check if we have an existing session for this user
    existing_sessions = await session_service.list_sessions(
        app_name=app_name,
        user_id=user_id
    )
    
    for session in existing_sessions.sessions:
        print(session)
    
    # Iterate over sessions to retrieve session IDs
    session_ids = [session.id for session in existing_sessions.sessions]

    # Example: Use the first session ID if available
    if session_ids:
        session_id = session_ids[0]
    else:
        session_id = None  # Handle case where no sessions exist
        # Create a new session
        session_id = str(uuid.uuid4())
        session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            state=initial_state
        )
        print(f"Created new session: {session_id}")

    
    # if len(existing_sessions.sessions) > 0:
    #     # Use the existing session
    #     session_id = existing_sessions.sessions.session_id
    #     print(f"Continuing existing session: {session_id}")
    # else:
    #     # Create a new session
    #     session_id = str(uuid.uuid4())
    #     session_service.create_session(
    #         app_name=app_name,
    #         user_id=user_id,
    #         session_id=session_id,
    #         state=initial_state
    #     )
    #     print(f"Created new session: {session_id}")

    # Create a runner with our agent and session service
    runner = Runner(
        agent=memory_agent,
        session_service=session_service,
        app_name=app_name
    )

    # Interactive chat loop
    print("\nReminder Agent Chat (Type 'exit' or 'quit' to end)")
    print("--------------------------------------------------------")

    while True:
        user_input = input("\nYou: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye! Your reminders have been saved.")
            break

        # Process the user input
        await call_agent_async(runner, user_id, session_id, user_input)

if __name__ == "__main__":
    asyncio.run(main())