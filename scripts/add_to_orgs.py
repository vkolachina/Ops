import os
import sys
import requests
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

GITHUB_API_URL = "https://api.github.com"
TOKEN = os.getenv('GITHUB_TOKEN')

if not TOKEN:
    logging.error("GITHUB_TOKEN not found. Please set the GITHUB_TOKEN environment variable.")
    sys.exit(1)

def add_user_to_org(username, org, role):
    url = f"{GITHUB_API_URL}/orgs/{org}/invitations"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "invitee_id": get_user_id(username),
        "role": role
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        logging.info(f"Successfully invited {username} to {org} with {role} role")
    else:
        logging.error(f"Failed to invite {username} to {org}. Status code: {response.status_code}")
        logging.error(response.json())

def get_user_id(username):
    url = f"{GITHUB_API_URL}/users/{username}"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['id']
    else:
        logging.error(f"Failed to get user ID for {username}")
        return None

def main():
    comment_body = os.getenv('COMMENT_BODY')
    if not comment_body:
        logging.error("COMMENT_BODY not found. Please set the COMMENT_BODY environment variable.")
        sys.exit(1)

    # Extract user data from comment body
    users_data = [line.strip() for line in comment_body.split('\n') 
                  if line.strip() and not line.startswith('/')]

    logging.info(f"Processing {len(users_data)} user(s)")

    for user_data in users_data:
        try:
            username, org, role = user_data.split(',')
            add_user_to_org(username.strip(), org.strip(), role.strip())
        except ValueError:
            logging.error(f"Invalid user data format: {user_data}")
            continue

if __name__ == "__main__":
    main()