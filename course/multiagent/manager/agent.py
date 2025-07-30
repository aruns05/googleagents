from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool


from .sub_agents.qna_creator_master_agent.agent import qna_creator_master_agent
from .sub_agents.epic_user_story_creator.agent import epic_user_story_creator

from google.adk.agents.callback_context import CallbackContext

async def print_before_agent_callback_message(callback_context: CallbackContext):
    print("manager_before_callback_context",callback_context.state.get('final_text'))
    
async def print_after_agent_callback_message(callback_context: CallbackContext):
    
    print("invocation_id",callback_context.invocation_id)
    print("manager_after_callback_context",callback_context.state.get('final_text'))


manager_root_agent = Agent(
    name="manager",
    model="gemini-2.0-flash",
    description="Manager agent",
    instruction="""
    You are a manager agent that is responsible for overseeing the work of the other agents.

    Always delegate the task to the appropriate agent. Use your best judgement 
    to determine which agent to delegate to.

    You are responsible for delegating tasks to the following agent based on the request text:
    - epic_user_story_creator
    - qna_creator

    You also have access to the following tools:
    - query_rag_corpus_tool
    - search_all_corpora_tool
    """,
    sub_agents=[epic_user_story_creator, qna_creator_master_agent],
    # tools=[
    #     AgentTool(news_analyst),
    #     get_current_time,
    # ],
    output_key="final_text",
    #before_agent_callback=print_before_agent_callback_message,
    #after_agent_callback=print_after_agent_callback_message,

)

root_agent=manager_root_agent