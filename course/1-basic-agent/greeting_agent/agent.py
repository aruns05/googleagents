from google.adk.agents import Agent


root_agent = Agent(
    name="greeting_agent",
    model="gemini-2.0-flash",
    description="Greeting agent",
    instruction="""You are a helpful assistant that greets users.
    Ask for the user's name and greet them by name.
    """
)