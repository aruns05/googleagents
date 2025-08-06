import base64
import json
import requests  # Ensure you have the `requests` library installed

def create_user_story(summary, description, acceptance_criteria):
    JIRA_API_TOKEN = ""
    url = "https://tanny-uat.atlassian.net/rest/api/2/issue"
    JIRA_EMAIL="tanx2107@gmail.com"
    
    # Jira issue payload
    user_story = {
        "fields": {
            "project": {
                "key": "MBA"  # Replace with your Jira project key
            },
            "summary": summary,
            "description": description,
            "issuetype": {
                "name": "Story"  # Ensure "Story" is a valid issue type in your Jira instance
            },
            #"customfield_12345": acceptance_criteria  # Replace with the actual custom field ID for acceptance criteria
        }
    }
    
    # headers = {
    #     "Authorization": f"Basic {api_key}",  # Use Basic Auth with API key
    #     "Content-Type": "application/json"
    # }
    
    credentials = f"{JIRA_EMAIL}:{JIRA_API_TOKEN}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/json"
    }
    
    # Make the POST request
    response = requests.post(url, headers=headers, data=json.dumps(user_story))
    print("response.status_code", response.status_code)
    # Check response status
    if response.status_code == 201:
        print("User story created successfully!")
        return response.json()
    else:
        print(f"Failed to create user story: {response.status_code}, {response.text}")
        return None
    
    
if __name__ == "__main__":
    # Example usage
    op = create_user_story("First UST Summary", "First Description", "First Acceptance Criteria")
    print(op)