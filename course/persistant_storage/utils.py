import asyncio
from google.genai.types import Content
from google.genai.types import Part

async def call_agent_async(runner, user_id, session_id, query):
    """Process a user query through the agent asynchronously."""
    print(f"\nUser: {query}")

    # Create content from the user query
    # content = content_types.Content(
    #     role="user",
    #     parts=[part.from_text(query)]
    # )
    
    content = Content(
        role="user",
        parts=[Part.from_text(text=query)]
    )
    print(f"\nContent created: {content}")
    
    print('session_id', session_id)
    print('user_id', user_id)
    

    # Get the session to see state before processing
    session = await runner.session_service.get_session(
        user_id=user_id,
        session_id=session_id,
        app_name=runner.app_name
    )
    
    # if session is None:
    #     await runner.session_service.create_session(
    #         app_name=runner.app_name,
    #         user_id=user_id,
    #         session_id=session_id,
    #         state={}
    #     )
    # else:
    print(f"\nState before processing: {session}")

    # Run the agent with the user query
    response =  runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content
    )
    print(f"\nResponse from agent: {response}")
    # Process the response
    final_response_text = None

    async for event in response:
        print(f"\nEvent received: {event}")
        if event.type == "content" and event.content.role == "User":
            # Extract the text from the content parts
            final_response_text = "".join(part.text for part in event.content.parts)
            print(f"\nFinal response text: {final_response_text}")
        # if event.type == "content" and event.content.role == "agent":
        #     final_response_text = event.content.parts[0].text
            


    # Get updated session to see state after processing
    session = await runner.session_service.get_session(
        app_name=runner.app_name,
        user_id=user_id,
        session_id=session_id
    )
    print(f"\nState after processing: {session}")

    print(f"\nAgent: {final_response_text}")
    return final_response_text