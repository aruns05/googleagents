from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService, Session
from google.adk.runners import Runner
from google.genai.types import Content, Part
from dotenv import load_dotenv


import asyncio


load_dotenv()

async def main():     
# Define agent with output_key
    greeting_agent = LlmAgent(
        name="greeting_agent",
        model="gemini-2.0-flash", # Use a valid model
        #instruction="Generate a short, friendly greeting.",
        instruction="Write 5 lines about Sachin Tendulkar",
        output_key="output" # Save response to state['last_greeting']
    )

    # --- Setup Runner and Session ---
    app_name, user_id, session_id = "cricket", "user1", "session1"
    session_service = InMemorySessionService()
    runner = Runner(
        agent=greeting_agent,
        app_name=app_name,
        session_service=session_service
    )
    session = await session_service.create_session(app_name=app_name,
                                        user_id=user_id,
                                        session_id=session_id)
    print(f"Initial state: {session.state}")

    # --- Run the Agent ---
    # Runner handles calling append_event, which uses the output_key
    # to automatically create the state_delta.
    user_message = Content(parts=[Part(text="")],)
    print(f"User message: {user_message}")
    for event in runner.run(user_id=user_id,
                            session_id=session_id,
                            new_message=user_message):
        if event.is_final_response():
            print(f"Agent responded.") # Response text is also in event.content

    # --- Check Updated State ---
    updated_session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
    print(f"State after agent run: {updated_session.state}")
    # Expected output might include: {'last_greeting': 'Hello there! How can I help you today?'}
    

if __name__ == "__main__":
    asyncio.run(main()) 