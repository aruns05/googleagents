from google.adk.agents import LlmAgent, Agent

from google.adk.agents.callback_context import CallbackContext

from google.adk.models.llm_request import LlmRequest
#from google.adk.models.llm_response import LlmResponse
from google.adk.agents import SequentialAgent

from ...tools.tools import (
    query_rag_corpus_tool,
    search_all_corpora_tool,
)

def _remove_other_content_from_llm_request(llm_request:LlmRequest, parent_agent,calling_agent, user_content):
    if not llm_request.contents:
        return None
    

    # print("parent_agent", parent_agent)
    # print("calling_agent", calling_agent)
    
    print("Initial_Content", llm_request.contents)
    # Filter out contents that are not from the parent agent or calling agent
    # and do not contain 'For context:' in their text parts.
    
    # contents_to_keep = []
    # for content in llm_request.contents:
    #     is_context_from_parent = False
    #     if content.role == 'user' and content.parts:
    #         for part in content.parts:
    #             if part.text and (f'[{parent_agent}]' in part.text or f'[{calling_agent}]' in part.text or 'For context:' in part.text):
    #                 is_context_from_parent = True
    #                 break  # This content is from the parent, no need to check other parts.
    #     if is_context_from_parent:
    #         contents_to_keep.append(content)
    # if user_content:
    #     contents_to_keep.append(user_content)  # Always keep the user content
    
    # llm_request.contents = contents_to_keep
    # print("final_content",llm_request.contents)                    
    
    return None

def _before_sub_model_callback_message(callback_context: CallbackContext, llm_request:LlmRequest):
    print("QNA_CREATOR_SUB_before_model_callback_message:")
    user_content =  callback_context.user_content
    parent_agent = callback_context._invocation_context.agent.parent_agent.name
    calling_agent = callback_context.agent_name
    print("parent_agent", parent_agent)
    print("calling_agent", calling_agent)
    _remove_other_content_from_llm_request(llm_request,parent_agent,calling_agent, user_content)
    
    return None
    
def print_after_model_callback_message(callback_context: CallbackContext):
    print("QNA_CREATOR_print_after_model_callback_message:")

def print_before_agent_callback_message(callback_context: CallbackContext):
    print("QNA_CREATOR_print_before_agent_callback_message:")
    
def print_after_agent_callback_message(callback_context: CallbackContext):
    print("QNA_CREATOR_print_after_agent_callback_message" )
    
qna_creator_child_agent = LlmAgent(
    name="qna_creator_child_agent",
    model="gemini-2.0-flash",
    description="An agent that gives answer to every question based on RAG corpora in Vertex AI and Google Cloud Storage buckets.",
    instruction="""
        You are a helpful assistant who manages and searches RAG corpora in Vertex AI and Google Cloud Storage buckets.
        You can help users with task:
        
        CORPUS SEARCHING:
        - SEARCH ALL CORPORA: Use search_all_corpora(query_text="your question") to search across ALL available corpora
        - SEARCH SPECIFIC CORPUS: Use query_rag_corpus(corpus_id="ID", query_text="your question") for a specific corpus
        - When the user asks a question or for information, use the search_all_corpora tool by default.
        - If the user specifies a corpus ID, use the query_rag_corpus tool for that corpus.
        
        - IMPORTANT - CITATION FORMAT:
            - When presenting search results, ALWAYS include the citation information
            - Format each result with its citation at the end: "[Source: Corpus Name (Corpus IDName)]"
            - You can find citation information in each result's "citation" field
            - At the end of all results, include a Citations section with the citation_summary information
            
            store the information in state['qna_results'] as a list of dictionaries,
            and return the control to the manager agent.

        """,

    #before_agent_callback=print_before_agent_callback_message,
    #after_agent_callback=print_after_agent_callback_message,
    before_model_callback=_before_sub_model_callback_message,
    #after_model_callback=print_after_agent_callback_message,
    tools=[query_rag_corpus_tool,search_all_corpora_tool],
    output_key="qna_results",
    include_contents='default'
)
    #print(f"✅ Agent '{qna_creator.name}' created using model '{qna_creator.model}'.")

qna_creator_master_agent = SequentialAgent(
        name="qna_creator_master_agent",
        sub_agents=[
            qna_creator_child_agent
        ],        
    )
    
# except Exception as e:
#     print(f"❌ Could not create Greeting agent. Check API Key ({qna_creator_agent.model}). Error: {e}")

root_agent = qna_creator_master_agent