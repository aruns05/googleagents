from typing import Optional
from google.adk.agents import Agent, LlmAgent
#from google.adk.tools import google_search
from google.adk.agents.callback_context import CallbackContext

from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse

from google.adk.agents import SequentialAgent

from ...tools.tools import (
    query_rag_corpus_tool,
    search_all_corpora_tool,
)

def _remove_other_content_from_llm_request(llm_request:LlmRequest, parent_agent,calling_agent):
#     x= Content(
#   parts=[
#     Part(
#       text='For context:'
#     ),
#     Part(
#       text="[manager] `transfer_to_agent` tool returned result: {'result': None}"
#     ),
#   ],
#   role='user'
# )]
    
    # loop_count=0
    # loop_count_delete=0
    # #print("initial_contents",llm_request.contents)
    # if llm_request.contents:
    #     # Find the most recent message with role 'user'
    #     for content in llm_request.contents:
    #         loop_count =loop_count+1
    #         if content.role == 'user' and content.parts:
    #             for part in content.parts:
    #                 print("loop_count_delete", loop_count_delete)
    #                 # Assuming text is in the 'text' attribute of each part
    #                 loop_count_delete += 1
    #                 if part.text:
    #                     if part.text.find(calling_agent) or part.text.find(parent_agent) == -1:
    #                         print("removing part.text",part.text)
    #                         llm_request.contents.remove(content)
    
    if not llm_request.contents:
        return None

    # Create a new list containing only the contents we want to keep.
    # This avoids issues with modifying a list while iterating over it.
    contents_to_keep = []
    for content in llm_request.contents:
        # A content object is considered "other content" if it's from the 'user'
        # (as the framework injects agent messages with role 'user') and contains
        # markers that it's not the original user's prompt.
        is_context_from_parent = False
        if content.role == 'user' and content.parts:
            for part in content.parts:
                if part.text and (f'[{parent_agent}]' in part.text or f'[{calling_agent}]' in part.text or 'For context:' in part.text):
                    is_context_from_parent = True
                    break  # This content is from the parent, no need to check other parts.
        if not is_context_from_parent:
            contents_to_keep.append(content)
    llm_request.contents = contents_to_keep

        
    print("final_content",llm_request.contents)                    
    
    return None
    

def print_after_model_callback_message(callback_context: CallbackContext, llm_request:LlmRequest)-> Optional[LlmResponse]:
    print("EPIC_STORY_CREATOR_after_model_callback_message")
    

def _before_model_callback_message(callback_context: CallbackContext, llm_request:LlmRequest)-> Optional[LlmResponse]:
    print("EPIC_STORY_CREATOR_before_model_callback_message")
    
    parent_agent = callback_context._invocation_context.agent.parent_agent.name
    calling_agent = callback_context.agent_name
    print("parent_agent", parent_agent)
    print("calling_agent", calling_agent)
    
    _remove_other_content_from_llm_request(llm_request,parent_agent,calling_agent)
    
    
    # Extract the text from the latest user message in the request history
    # last_user_message_text = ""
    # print("llm_request.contents",llm_request.contents)
    # if llm_request.contents:
    #     # Find the most recent message with role 'user'
    #     for content in llm_request.contents:
    #         print("content.parts", len(content.parts))
    #         if content.role == 'user' and content.parts:
    #             # Assuming text is in the first part for simplicity
    #             if content.parts[0].text:
    #                 last_user_message_text = last_user_message_text + content.parts[0].text
    #                 break # Found the last user message text
    
    return None 

def _before_agent_callback_message(callback_context: CallbackContext,llm_request:LlmRequest):
    print("EPIC_STORY_CREATOR_before_agent_callback_message")
    
    parent_agent = callback_context._invocation_context.agent.parent_agent.name
    print("parent_agent", parent_agent)
    
    llm_request.append_instructions(
        """ Please follow the below instructions
            Please use the output  fetched from search_all_corpora(query_text="your question")
            to search across ALL available corpora. 
            Please use the 
            Please dont use any other tools or methods to search for information.
            Remove the remaining content from the llm_request.contents
            If you find any other content in llm_request.contents, please remove it.
        """
    )
    
    # Extract the text from the latest user message in the request history
    last_user_message_text = ""
    #print("llm_request.contents",llm_request.contents)
    if llm_request.contents:
        # Find the most recent message with role 'user'
        for content in llm_request.contents:
            print("content.parts", len(content.parts))
            if content.role == 'user' and content.parts:
                # Assuming text is in the first part for simplicity
                if content.parts[0].text:
                    last_user_message_text = last_user_message_text + content.parts[0].text
                    break # Found the last user message text
    
    return None
    #callback_context.user_content.parts[0].text
    
def print_after_agent_callback_message(callback_context: CallbackContext):
    print("EPIC_STORY_CREATOR_after_agent_callback_message")
    
    # print("EPIC_STORY_print_after_agent_callback_message_arun:" )
    # #print(callback_context.invocation_id)
    # print(callback_context.agent_name)
    # #print("qna_results",callback_context.state.get('qna_results'))
    # #print("epic_story_results",callback_context.state.get('epic_story_results'))
    # print(callback_context.user_content.parts[0].text)    
    

initial_epic_user_story_creator = LlmAgent(
    name="initial_epic_user_story_creator",
    model="gemini-2.0-flash",
    description="An agent that creates Epics, User Stories, and Acceptance Criteria based on request.",
    instruction="""
    You are an expert assistant specializing in Agile methodologies, 
    focusing on creating well-formed Epics, User Stories, and Acceptance Criteria for software
    development. Your goal is to help users translate their ideas and requirements into a 
    structured and actionable format.
    Please  use ONLY search_all_corpora(query_text="your question") to search across ALL available corpora
        Please dont use any other tools or methods to search for information.
    **DEFINITIONS & FORMATS:**

    **1. EPIC:** A large body of work that can be broken down into smaller, manageable user stories.
    -   **FORMAT:** `EPIC: [Epic Title]`

    **2. USER STORY:** A short, simple description of a feature from the perspective of the end-user.
    -   **FORMAT:** `As a [type of user], I want to [perform some action] so that I can [achieve some goal].`

    **3. ACCEPTANCE CRITERIA (AC):** The conditions that a software product must meet to be accepted by a user. Use Gherkin syntax.
    -   **FORMAT:**
        ```gherkin
        Scenario: [A specific scenario]
          Given [some context]
          When [I take some action]
          Then [I should see some outcome]
        ```

    **YOUR TASK:**
    1.  **Analyze the Request:** Carefully read the user's input to understand the high-level goal or feature.
    2.  **Gather Context:Use the `search_all_corpora` tool to gather context and information related to the request.
    3.  **Remove Other Content:** Remove any other content from the llm_request.contents that is not related to the user request.
    4.  **Decompose into Epics:** If the request is large (e.g., "build an authentication system"), break it down into one or more Epics. For smaller requests, an Epic may not be necessary.
    5.  **Create User Stories:** For each Epic or for the main request, create specific user stories.
        -   **Identify User Persona:** Who is the user? (e.g., "registered user", "site administrator").
        -   **Identify Action:** What does the user want to do?
        -   **Identify Goal/Value:** What is the benefit for the user?
    6.  **Define Acceptance Criteria:** For each user story, write clear, testable acceptance criteria using the Gherkin `Given/When/Then` format. Create multiple scenarios to cover different paths (e.g., success, failure, edge cases).
    7.  **Maintain Hierarchy:** Structure your output clearly:
        -   Start with the EPIC.
        -   Nest the corresponding USER STORY underneath it.
        -   Nest the ACCEPTANCE CRITERIA for that story underneath it.
        -   Use separators (like '***') between distinct user stories.
    8.  **Ask for Clarification:** If a request is vague, ask clarifying questions to get the necessary details.
    9.  **Use Tools for Research:** If the request involves a concept you are unfamiliar with, use the available search tools to gather context before creating the artifacts.

    **COMPREHENSIVE EXAMPLE:**
    -   **User Input:** "I need features for managing user accounts on my website."
    -   **Your Output:**
        EPIC: User Account Management

        USER STORY:
        As a new user, I want to register for an account so that I can make purchases and save my information.

        ACCEPTANCE CRITERIA:
        Scenario: Successful registration with valid details
          Given I am on the website's homepage and not logged in
          When I navigate to the registration page
          And I enter a valid email, a strong password, and confirm the password
          And I click the "Sign Up" button
          Then I should be redirected to my account dashboard
          And I should see a welcome message.

        Scenario: Registration attempt with an existing email
          Given I am on the registration page
          When I enter an email address that is already registered
          And I fill out the other fields
          And I click the "Sign Up" button
          Then I should see an error message stating that the email is already in use.

        ***

        USER STORY:
        As a registered user, I want to log in to my account so that I can access my order history and saved addresses.

        ACCEPTANCE CRITERIA:
        Scenario: Successful login with correct credentials
          Given I am a registered user and I am on the login page
          When I enter my correct email and password
          And I click the "Log In" button
          Then I should be redirected to my account dashboard.

        Scenario: Failed login with incorrect password
          Given I am a registered user and I am on the login page
          When I enter my correct email and an incorrect password
          And I click the "Log In" button
          Then I should see an error message about invalid credentials.
          
        store the information in state['initial_epic_story_results'] as a list of dictionaries,
         and return the control to the manager agent.
         
         
    """,
    tools=[query_rag_corpus_tool, search_all_corpora_tool],
    output_key="initial_epic_story_results",
    before_model_callback=_before_model_callback_message,
    # #after_model_callback=print_after_model_callback_message,
    # before_agent_callback=print_before_agent_callback_message,
    # #after_agent_callback=print_after_agent_callback_message,
    include_contents='default'
)

reviewer_agent = LlmAgent(
    name="reviewer_agent",
    model="gemini-2.5-flash",
    instruction="""
    
You are an expert assistant specializing in Agile methodologies, 
    focusing on creating well-formed Epics, User Stories, and Acceptance Criteria for software
    development. Your goal is to analyze the epic, user stories stored in state['initial_epic_story_results'].
and provide critique to them . 
You can use search_all_corpora(query_text="your question") to get context if needed.
Always give a detailed critique, even if the text is factually correct, comment on style, clarity, possible improvements, 
or anything that could make it better. If there are factual problems,
mention those. Output a short critique, not just 'valid'.
store the output in state['critique']
""",
    output_key="critique",
)


revision_agent = LlmAgent(
    name="revision_agent",
    model="gemini-2.5-flash",
    instruction="""
Your goal is to revise the epic and user stories stored in state['initial_epic_story_results']
based on the feedback in state['critique'].
Store the output in state['final_output'] 
Return the control to the manager agent.
""",
    output_key="final_output",
)

epic_user_story_creator = SequentialAgent(
    name="epic_user_story_creator",
    sub_agents=[
        initial_epic_user_story_creator,
        reviewer_agent,
        revision_agent
    ],
)

root_agent= epic_user_story_creator