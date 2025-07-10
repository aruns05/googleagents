# from google.adk.agents import Agent 

# question_answering_agent = Agent(
#     name="question_answering_agent",
#     model="gemini-2.0-flash",
#     description="Question Answering Agent",
#     instruction="""You are a helpful assistant that answers question about the user's hobbies.
#     Here is some content about it 
#     Name
#     {user_name}
#     Hobbies
#     {user_hobbies}
#     """,
# )

# #root_agent = question_answering_agent


from google.adk.agents import Agent

# Create the root agent
question_answering_agent = Agent(
    name="question_answering_agent",
    model="gemini-2.0-flash",
    description="Question answering agent",
    instruction="""
    You are a helpful assistant that answers questions about the user's preferences.

    Here is some information about the user:
    Name: 
    {user_name}
    Preferences: 
    {user_preferences}
    """,
)

root_agent = question_answering_agent