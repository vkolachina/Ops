import requests
import os
import re
import sys

def get_user_id(username, token):
    url = f"https://api.github.com/users/{username}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()['id']
    except requests.exceptions.RequestException as e:
        print(f"Failed to get user ID for {username}.")
        print(f"Exception: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        return None

def add_collaborator_to_org(org_name, user_id, permission, token):
    url = f"https://api.github.com/orgs/{org_name}/invitations"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }
    data = {
        "invitee_id": user_id,
        "role": permission
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print(f"Successfully invited user with ID {user_id} to organization {org_name} with {permission} permission")
    except requests.exceptions.RequestException as e:
        if e.response.status_code == 422:
            if "already_invited" in e.response.text:
                print(f"User with ID {user_id} has already been invited to {org_name}")
            elif "user_is_org_member" in e.response.text:
                print(f"User with ID {user_id} is already a member of {org_name}")
            else:
                print(f"Failed to invite user with ID {user_id} to {org_name}.")
                print(f"Status code: {e.response.status_code}")
                print(f"Response body: {e.response.text}")
        else:
            print(f"Failed to invite user with ID {user_id} to {org_name}.")
            print(f"Exception: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Status code: {e.response.status_code}")
                print(f"Response body: {e.response.text}")

def parse_comment(comment):
    pattern = r'/issueops add\s+(\w+)\s+(\w+)\s+(\w+)'
    match = re.search(pattern, comment)
    if match:
        return match.groups()
    return None

def process_github_data(username, org_name, permission, token):
    user_id = get_user_id(username, token)
    if user_id:
        add_collaborator_to_org(org_name, user_id, permission, token)
    else:
        print(f"Skipping invitation for {username} due to failure in getting user ID")

def main():
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GitHub token not found. Please set the GITHUB_TOKEN environment variable.")
        return 1

    comment_body = os.getenv('COMMENT_BODY')
    if not comment_body:
        print("Error: COMMENT_BODY not found. Please set the COMMENT_BODY environment variable.")
        return 1

    parsed_data = parse_comment(comment_body)
    
    if parsed_data:
        username, org_name, permission = parsed_data
        process_github_data(username, org_name, permission, token)
    else:
        print("Error: Invalid command format. Use '/issueops add username organization permission'")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())