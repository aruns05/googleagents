import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv
from utility import utils
import base64
import json

# Jira credentials
# JIRA_DOMAIN = "your-domain.atlassian.net"
# https://cdeproducts.atlassian.net/jira/software/c/projects/TP1/boards/26
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

def get_user_stories():
    # Define the path to your text file
    file_path = "output\enhanced_user_story.txt"

    # Read the file content and store it in a variable
    with open(file_path, "r", encoding="windows-1252") as file:
        long_string = file.read()
    return long_string

def get_epic_comment():
    # Define the path to your text file
    file_path = "logs/user_story_log.txt"

    # Read the file content and store it in a variable
    with open(file_path, "r", encoding="windows-1252") as file:
        epic_comment = file.read()
    return epic_comment

def add_comment_to_epic(epic_key, comment_text):
    url = f"{JIRA_BASE_URL}/rest/api/2/issue/{epic_key}/comment"

    credentials = f"{JIRA_EMAIL}:{JIRA_API_TOKEN}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/json"
    }
    # print("Line No: 49 JIRA Comment",comment_text)
    # print("Line No: 50 JIRA User Story",user_stories_epics)
    payload = {
        "body": comment_text
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 201:
        print(f"Comment added to Epic {epic_key}")
    else:
        print(f"Failed to add comment: {response.status_code} - {response.text}")
        return "Failed to add epic comment"


def create_story_and_link_to_epic():
    url = f"{JIRA_BASE_URL}/rest/api/2/issue"
 
    credentials = f"{JIRA_EMAIL}:{JIRA_API_TOKEN}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/json"
    }
    
    user_story_response = get_user_stories()
    user_stories_epics = utils.format_user_stories(user_story_response)
    print("user_stories_epics==",user_stories_epics)
    if not user_stories_epics:
        print("Failed Uploading User Stories to JIRA")
        return "Failed Uploading User Stories to JIRA" #failed due to empty user_stories_epics
    for epic_data in user_stories_epics:
      epic_key = create_epic_in_jira(epic_data)
      if not epic_key:
          print(f"Skipping stories for epic '{epic_data['epic']}' due to epic creation failure.")
          continue

      # Add comment to the created epic
      epic_comment = get_epic_comment()
      comment_status = add_comment_to_epic(epic_key, epic_comment)
      if comment_status == "Failed to add epic comment":
          return "Failed to Add Epic Comment"
      for story in epic_data['user_stories']:
        payload = {
            "fields": {
                "project": {
                    "key": JIRA_PROJECT_KEY
                },
                "summary": story['title'],
                "description": f"{story['description']}\n\nAcceptance Criteria:\n" + "\n".join(story['acceptance_criteria'] if isinstance(story['acceptance_criteria'], list) else [story['acceptance_criteria']]),
                "issuetype": {
                    "name": "Story"
                }
            }
        }
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201: 
          story_key = response.json()["key"]
          map_story_to_epic(story_key, epic_key, JIRA_EMAIL, JIRA_API_TOKEN)
          print(f"Created and linked story {story_key} to epic {epic_key}")
        else:
          print(f"Failed to create story '{story['title']}': {response.status_code} - {response.text}")
    return "success"


def create_epic_in_jira(epic_data, labels_list="JiraBot"):
    url = f"{JIRA_BASE_URL}/rest/api/2/issue"
 
    credentials = f"{JIRA_EMAIL}:{JIRA_API_TOKEN}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/json"
    }

    fields_payload = {
        "project": {
            "key": JIRA_PROJECT_KEY
        },
        "summary": epic_data['epic'],
        "description": epic_data['description'],
        "issuetype": {
            "name": "Epic"
        }
    }

    # If a list of labels is provided and it's not empty, add the 'labels' field
    if labels_list and isinstance(labels_list, list) and len(labels_list) > 0:
        fields_payload["labels"] = labels_list

    payload = {
        "fields": fields_payload
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 201:
        epic_key = response.json()["key"]
        labels_str = f" with labels {labels_list}" if labels_list else ""
        print(f"Successfully created epic {epic_key}: {epic_data['epic']}{labels_str}")
        return epic_key
    else:
        print(f"Failed to create epic '{epic_data['epic']}': {response.status_code} - {response.text}")
        return None 

def map_story_to_epic(story_key, epic_key,  username, api_token):
    """
    Links a story to an epic by updating the story's parent field.
    Uses only the payload that works for your Jira configuration.
    """
    try:
        auth = HTTPBasicAuth(username, api_token)
        update_url = f"{JIRA_BASE_URL}/rest/api/2/issue/{story_key}"
        
        # For Jira Cloud, the epic link is set via a custom field.
        # You need to find the correct custom field ID for "Epic Link".
        # Common IDs are 'customfield_10014', 'customfield_10010', etc.
        # You can find this by:
        # 1. Going to a story in Jira, viewing its details.
        # 2. Adding the "Epic Link" field if it's not visible.
        # 3. Using your browser's developer tools to inspect the "Epic Link" field's HTML element
        #    to find its ID (e.g., id="customfield_XXXXX-val").
        # OR by querying the Jira API for field information:
        # GET /rest/api/2/field  (and search for "Epic Link")

        # Assuming 'customfield_10014' is the Epic Link field for Jira Cloud.
        # For Jira Server, you might use the "parent" field as you had.
        # Adjust this payload based on your Jira version (Cloud vs Server) and configuration.

        # Payload for Jira Cloud (using custom field for Epic Link)
        payload = {
            "fields": {
                "customfield_10014": epic_key  # Replace with your actual Epic Link field ID
            }
        }
        
        # Payload for Jira Server (using parent field - this might also work for some Cloud instances if configured)
        # payload = {
        #     "fields": {
        #         "parent": {
        #             "key": epic_key
        #         }
        #     }
        # }

        headers = {'Content-Type': 'application/json'}
        # print(f"Attempting to link story {story_key} to epic {epic_key} with payload: {json.dumps(payload, indent=2)}")
        response = requests.put(update_url, json=payload, auth=auth, headers=headers)
        
        if response.status_code == 204:
            # print(f"Successfully linked story {story_key} to epic {epic_key}")
            return True
        else:
            print(f"Failed to link story {story_key} to epic {epic_key}. Status: {response.status_code}, Response: {response.text}")
            #     return False
            return False
            
    except Exception as error:  
      print(f"Exception while linking story {story_key} to epic {epic_key}: {error}")
      return False

def jira_upload_process():
    # Ensure your JIRA credentials and project key are set at the top of the script

    if not all([JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_PROJECT_KEY]):
        print("Jira configuration is missing. Please set JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, and JIRA_PROJECT_KEY.")
        return 
    
    try:
        print("Starting Jira upload process...")
        create_story = create_story_and_link_to_epic()
        if "failed" in create_story.lower():
            print("create_story==",create_story)
            return create_story
            
        print("Jira upload process finished.")
        return "success"
    except Exception as e:
        return f"Failed Due to Error: {e}"



# jira_upload_process()