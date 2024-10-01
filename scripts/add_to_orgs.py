import os
import sys
import requests
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

GITHUB_API_URL = "https://api.github.com"
TOKEN = os.getenv('GITHUB_TOKEN')

if not TOKEN:
    logging.error("GITHUB_TOKEN not found. Please set the GITHUB_TOKEN environment variable.")
    sys.exit(1)

def validate_input(username, org, role):
    valid_roles = ['admin', 'direct_member', 'billing_manager']
    if not username or not org or not role:
        raise ValueError("Username, organization, and role must be provided")
    if role not in valid_roles:
        raise ValueError(f"Invalid role. Must be one of {valid_roles}")

def make_request(url, method='get', data=None, max_retries=3):
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    for attempt in range(max_retries):
        try:
            if method == 'get':
                response = requests.get(url, headers=headers)
            elif method == 'post':
                response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 403 and 'rate limit' in response.text.lower():
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                sleep_time = max(reset_time - time.time(), 0) + 1
                logging.warning(f"Rate limit hit. Sleeping for {sleep_time} seconds.")
                time.sleep(sleep_time)
                continue
            
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise
            logging.warning(f"Request failed. Retrying... (Attempt {attempt + 1}/{max_retries})")
            time.sleep(2 ** attempt)  # Exponential backoff

def add_user_to_org(username, org, role):
    url = f"{GITHUB_API_URL}/orgs/{org}/invitations"
    data = {
        "invitee_id": get_user_id(username),
        "role": role
    }
    try:
        response = make_request(url, method='post', data=data)
        logging.info(f"Successfully invited {username} to {org} with {role} role")
    except requests.RequestException as e:
        logging.error(f"Failed to invite {username} to {org}. Error: {str(e)}")

def get_user_id(username):
    url = f"{GITHUB_API_URL}/users/{username}"
    try:
        response = make_request(url)
        return response.json()['id']
    except requests.RequestException as e:
        logging.error(f"Failed to get user ID for {username}. Error: {str(e)}")
        return None

def main():
    comment_body = os.getenv('COMMENT_BODY')
    if not comment_body:
        logging.error("COMMENT_BODY not found. Please set the COMMENT_BODY environment variable.")
        sys.exit(1)

    users_data = [line.strip() for line in comment_body.split('\n') 
                  if line.strip() and not line.startswith('/')]

    logging.info(f"Processing {len(users_data)} user(s)")

    for user_data in users_data:
        try:
            username, org, role = user_data.split(',')
            validate_input(username.strip(), org.strip(), role.strip())
            add_user_to_org(username.strip(), org.strip(), role.strip())
        except ValueError as e:
            logging.error(f"Invalid input: {user_data}. Error: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error processing: {user_data}. Error: {str(e)}")

if __name__ == "__main__":
    main()