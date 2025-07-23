from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext

from ...tools.tools import (
    query_rag_corpus_tool,
    search_all_corpora_tool,
)

def print_before_model_callback_message(callback_context: CallbackContext):
    print("QNA_CREATOR_print_before_model_callback_message:")
    
def print_after_model_callback_message(callback_context: CallbackContext):
    print("QNA_CREATOR_print_after_model_callback_message:")

def print_before_agent_callback_message(callback_context: CallbackContext):
    #callback_context.user_content.parts[0].text
    print("QNA_CREATOR_print_before_agent_callback_message:")
    
def print_after_agent_callback_message(callback_context: CallbackContext):
    print("QNA_CREATOR_print_after_agent_callback_message" )
    #print(callback_context.invocation_id)
    # print(callback_context.agent_name)
    # print(callback_context.state.get('qna_results'))
    # print(callback_context.user_content.parts[0].text)  
    
qna_creator= None  
    
try:
    qna_creator = Agent(
        name="qna_creator",
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
        #before_model_callback=print_before_agent_callback_message,
        #after_model_callback=print_after_agent_callback_message,
        tools=[query_rag_corpus_tool,search_all_corpora_tool],
        output_key="qna_results",
        include_contents='default'
)
    print(f"✅ Agent '{qna_creator.name}' created using model '{qna_creator.model}'.")

except Exception as e:
    print(f"❌ Could not create Greeting agent. Check API Key ({qna_creator.model}). Error: {e}")
