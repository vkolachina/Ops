import requests
import os
import re
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

GITHUB_API_URL = "https://api.github.com"

def get_user_id(username, token):
    url = f"{GITHUB_API_URL}/users/{username}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()['id']
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get user ID for {username}. Error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Status code: {e.response.status_code}")
            logger.error(f"Response body: {e.response.text}")
        return None

def add_collaborator_to_org(org_name, user_id, permission, token):
    url = f"{GITHUB_API_URL}/orgs/{org_name}/invitations"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    data = {
        "invitee_id": user_id,
        "role": permission
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        logger.info(f"Successfully invited user with ID {user_id} to organization {org_name} with {permission} permission")
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code == 422:
                error_message = e.response.json().get('message', '')
                if "already_invited" in error_message:
                    logger.warning(f"User with ID {user_id} has already been invited to {org_name}")
                elif "user_is_org_member" in error_message:
                    logger.warning(f"User with ID {user_id} is already a member of {org_name}")
                else:
                    logger.error(f"Failed to invite user with ID {user_id} to {org_name}. Error: {error_message}")
            else:
                logger.error(f"Failed to invite user with ID {user_id} to {org_name}. Status code: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
        else:
            logger.error(f"Failed to invite user with ID {user_id} to {org_name}. Error: {str(e)}")

def parse_comment(comment):
    pattern = r'/issueops\s+add\s+(\S+)\s+(\S+)\s+(\S+)'
    match = re.search(pattern, comment)
    return match.groups() if match else None

def process_github_data(username, org_name, permission, token):
    user_id = get_user_id(username, token)
    if user_id:
        add_collaborator_to_org(org_name, user_id, permission, token)
    else:
        logger.error(f"Skipping invitation for {username} due to failure in getting user ID")

def main():
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        logger.error("GitHub token not found. Please set the GITHUB_TOKEN environment variable.")
        return 1

    comment_body = os.getenv('COMMENT_BODY')
    if not comment_body:
        logger.error("COMMENT_BODY not found. Please set the COMMENT_BODY environment variable.")
        return 1

    logger.info(f"Received comment: {comment_body}")

    parsed_data = parse_comment(comment_body)
    
    if parsed_data:
        username, org_name, permission = parsed_data
        logger.info(f"Parsed data - Username: {username}, Organization: {org_name}, Permission: {permission}")
        process_github_data(username, org_name, permission, token)
    else:
        logger.error("Invalid command format. Use '/issueops add username organization permission'")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())