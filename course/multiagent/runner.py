import uuid
import os
import asyncio
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.genai import types
from manager.agent import manager_root_agent

from google.adk.sessions import InMemorySessionService, DatabaseSessionService
#from google.adk.artifacts import InMemoryArtifactService , GcsArtifactService


load_dotenv()

async def main():
    print("Starting Multi-agent Runner...")
    
    APP_NAME= "pdlc"
    USER_ID = "arun_s05"
    SESSION_ID = str(uuid.uuid4())
    
    # Create a new session service to store state in internal memory
    #session_service_stateful = InMemorySessionService()
    
    # Create a new session service to store state in external DB
    session_service_stateful = DatabaseSessionService(
            db_url="sqlite:///sample.db"
            #db_url = connection_string
        )
    
    await session_service_stateful.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )
    # print("CREATED NEW SESSION:")
    # print(f"\tSession ID: {SESSION_ID}")

    runner = Runner(
        agent=manager_root_agent,
        app_name=APP_NAME,
        session_service=session_service_stateful,
        #artifact_service=artifact_service,  # Use InMemoryArtifactService for simplicity
        #artifact_service=gcs_artifact_service,  # Use GCS for artifact storage
    )

    new_message = types.Content(
        role="user", parts=[types.Part(text="What is SECTION 1001 OF THE PATRIOT ACT?")]
    )
    
    for event in runner.run(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=new_message,
    ):
        # Agent state changes are communicated via the `state_delta` field.
        # if event.actions and event.actions.state_delta:
        #     print(f"State Delta: {event.actions.state_delta}")
    
        if event.is_final_response():
            if event.content and event.content.parts:
                final_text = event.content.parts[0].text
                print(f"Final Response: {final_text}")
                
        # To avoid verbose output, only printing other intermediate events.
        elif not (event.actions and event.actions.state_delta):
            print(f"Event: {event}")

if __name__ == "__main__":
    asyncio.run(main())