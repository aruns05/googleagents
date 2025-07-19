from google.adk.runners import Runner
from google.adk.artifacts import InMemoryArtifactService # Or GcsArtifactService
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.adk.agents import SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

from dotenv import load_dotenv

# # Load environment variables from the .env file (if present)
load_dotenv()

# Your agent definition
research_agent = LlmAgent(
    name="Researcher",
    model="gemini-2.5-flash",
 instruction="""
Conduct thorough web research on the subject given in the input. 
Gather key facts, recent information, and relevant details about the topic.
Summarize your research findings in a comprehensive but organized manner.
sing the research findings stored in state['research'], write a short, factual paragraph about the subject.
Base your writing on the research provided - don't make up facts.
Be concise and clear. Your output should be plain text only.
Dont show the website links
""",
    output_key="final_text",
    tools=[google_search],
    #after_agent_callbacks=[save_final_text_as_artifact],
)


generator_agent = LlmAgent(
    name="DraftWriter",
    model="gemini-2.5-flash",
    instruction="""
Using the research findings stored in state['research'], write a short, factual paragraph about the subject.
Base your writing on the research provided - don't make up facts.
Be concise and clear. Your output should be plain text only.
""",
    output_key="final_text",
)


# reviewer_agent = LlmAgent(
#     name="Critic",
#     model="gemini-2.5-flash",
#     instruction="""
# Analyze the paragraph stored in state['draft_text'].
# Also reference the research in state['research'] to check for factual accuracy.
# Always give a detailed critique, even if the text is factually correct, comment on style, clarity, possible improvements, or anything that could make it better. If there are factual problems, mention those. Output a short critique, not just 'valid'.
# """,
#     output_key="critique",
# )


# revision_agent = LlmAgent(
#     name="Rewriter",
#     model="gemini-2.5-flash",
#     instruction="""
# Your goal is to revise the paragraph in state['draft_text'] based on the feedback in state['critique'].
# You can also reference the research in state['research'] to ensure accuracy and completeness.
# Output only the improved paragraph, rewritten as needed.
# """,
#     output_key="revised_text",
# )

# # Define callback functions for the agent
def greet_on_first_message(callback_context: CallbackContext):
    if not callback_context.state.get("greeted"):
        callback_context.state["greeted"] = True
    return None

async def print_finished_message(callback_context: CallbackContext):
    print("Research process completed successfully.")
    #print(f"Final revised text: {callback_context.state.get('final_text', 'No text generated')}")
    final_text = callback_context.state.get("final_text")
    if not final_text:
        print("No final_text in state to save as artifact.")
        return
    
    report_bytes = final_text.encode("utf-8")
    text_artifact = types.Part.from_text(
        text=report_bytes,
        #mime_type="text/plain"        
    )
    
    filename = "final_research.txt"
    
    try:
        version = await callback_context.save_artifact(filename=filename, artifact=text_artifact.text)
        print(f"Successfully saved artifact '{filename}' as version {version}.")
        
        report_artifact = await callback_context.load_artifact(filename=filename)

        if report_artifact:
            print(f"Successfully loaded latest Python artifact '{filename}'.")
            print('report_artifact:', report_artifact)
            
            # ... further processing ...
        else:
            print(f"Python artifact '{filename}' not found.")
        
    except ValueError as e:
        print(f"Error saving artifact: {e}. Is ArtifactService configured in Runner?")
    except Exception as e:
        # Handle potential storage errors (e.g., GCS permissions)
        print(f"An unexpected error occurred during artifact save: {e}")
    return None

research_agent = SequentialAgent(
    name="research_agent",
    #before_agent_callback=greet_on_first_message, 
    sub_agents=[
        research_agent,
        #generator_agent,
        # reviewer_agent,
        # revision_agent
    ],
    after_agent_callback=print_finished_message
)

root_agent= research_agent
