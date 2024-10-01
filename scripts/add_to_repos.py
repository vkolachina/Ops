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

def validate_input(username, repo, permission):
    valid_permissions = ['pull', 'push', 'admin']
    if not username or not repo or not permission:
        raise ValueError("Username, repository, and permission must be provided")
    if permission not in valid_permissions:
        raise ValueError(f"Invalid permission. Must be one of {valid_permissions}")
    if '/' not in repo:
        raise ValueError("Repository must be in the format 'owner/repo'")

def make_request(url, method='get', data=None, max_retries=3):
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    for attempt in range(max_retries):
        try:
            if method == 'get':
                response = requests.get(url, headers=headers)
            elif method == 'put':
                response = requests.put(url, headers=headers, json=data)
            
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

def add_user_to_repo(username, repo, permission):
    owner, repo_name = repo.split('/')
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo_name}/collaborators/{username}"
    data = {"permission": permission}
    try:
        response = make_request(url, method='put', data=data)
        logging.info(f"Successfully added {username} to {repo} with {permission} permission")
    except requests.RequestException as e:
        logging.error(f"Failed to add {username} to {repo}. Error: {str(e)}")

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
            username, repo, permission = user_data.split(',')
            validate_input(username.strip(), repo.strip(), permission.strip())
            add_user_to_repo(username.strip(), repo.strip(), permission.strip())
        except ValueError as e:
            logging.error(f"Invalid input: {user_data}. Error: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error processing: {user_data}. Error: {str(e)}")

if __name__ == "__main__":
    main()