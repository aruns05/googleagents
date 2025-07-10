from google.adk.sessions import InMemorySessionService, DatabaseSessionService, Session
import asyncio
from google.adk.runners import Runner


async def main():
    
    # Create a simple session to examine its properties
    temp_service = InMemorySessionService()
    example_session = await temp_service.create_session(
        app_name="cricket",
        user_id="10",
        state={"name": "Sachin"} # State can be initialized
    )

    print(f"--- Examining Session Properties ---")
    print(f"ID (`id`):                {example_session.id}")
    print(f"Application Name (`app_name`): {example_session.app_name}")
    print(f"User ID (`user_id`):         {example_session.user_id}")
    print(f"State (`state`):           {example_session.state}") # Note: Only shows initial state here
    print(f"Events (`events`):         {example_session.events}") # Initially empty
    print(f"Last Update (`last_update_time`): {example_session.last_update_time:.2f}")
    print(f"---------------------------------")

    # Clean up (optional for this example)
    temp_service = await temp_service.delete_session(app_name=example_session.app_name,
                                user_id=example_session.user_id, session_id=example_session.id)
    print("The final status of temp_service - ", temp_service)
        
    
    
if __name__ == "__main__":
    asyncio.run(main()) 
 