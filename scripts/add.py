import requests
import os
import re

def get_user_id(username, token):
    url = f"https://api.github.com/users/{username}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['id']
    else:
        print(f"Failed to get user ID for {username}. Status code: {response.status_code}")
        print(f"Response: {response.text}")
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

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        print(f"Successfully invited user with ID {user_id} to organization {org_name} with {permission} permission")
    elif response.status_code == 422 and "already_invited" in response.text:
        print(f"User with ID {user_id} has already been invited to {org_name}")
    elif response.status_code == 422 and "user_is_org_member" in response.text:
        print(f"User with ID {user_id} is already a member of {org_name}")
    else:
        print(f"Failed to invite user with ID {user_id} to {org_name}. Status code: {response.status_code}")
        print(f"Response: {response.text}")

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

if __name__ == "__main__":
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        print("Error: GitHub token not found. Please set the GITHUB_TOKEN environment variable.")
        exit(1)

    comment_body = os.getenv('COMMENT_BODY')
    parsed_data = parse_comment(comment_body)
    
    if parsed_data:
        username, org_name, permission = parsed_data
        process_github_data(username, org_name, permission, token)
    else:
        print("Error: Invalid command format. Use '/issueops add username organization permission'")