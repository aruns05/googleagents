from google.adk.agents import LlmAgent
from pydantic import Field, BaseModel


class EmailContent(BaseModel):
    subject: str = Field(
        description="The subject of the email. This should be concise and relevant to the content of the email.",
        example="Meeting Reminder"
    )
    body: str = Field(
        description="The main content of the email.Should be well-formatted with proper greeting. This should provide all necessary information in a clear and concise manner.",
    )

root_agent = LlmAgent(
    name="email_agent",
    model="gemini-2.0-flash",
    description="GENERATES professional Email with subject and body",
    instruction="""You are a helpful email generation assistant. 
    Your task is to generate a professional email based on the user's request.
    
    GUIDELINES
    - Use a clear and concise subject line.
    - Start with a polite greeting.
    - Write the body of the email in a professional tone.
        * Clear and concise main content
        * Appropriate closing statement
        * Polite closing statement
    - Suggest relevant attachments if necessary.
    - Use proper formatting for readability.
    IMPORTANT: YOUR RESPONSE MUST BE A VALID EMAIL CONTENT JSON OBJECT MATCHING BELOW STRUCTURE
    {
       "subject": "Your email subject here",
         "body": "Your email body here"
    }
        
    DO NOT INCLUDE ANY ADDITIONAL TEXT OR EXPLANATION OUTSIDE THE JSON OBJECT.    
    """,
    output_schema=EmailContent,
    output_key="email",
)