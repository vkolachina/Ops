import requests
import os
import re
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

GITHUB_API_URL = "https://api.github.com"
TOKEN = os.getenv('GITHUB_TOKEN')
COMMENT_BODY = os.getenv('COMMENT_BODY')

def get_user_id(username):
    url = f"{GITHUB_API_URL}/users/{username}"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    try:
        logger.info(f"Sending request to get user ID for {username}")
        logger.info(f"Token used (first 10 chars): {TOKEN[:10]}...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        user_id = response.json()['id']
        logger.info(f"Successfully retrieved user ID for {username}: {user_id}")
        return user_id
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get user ID for {username}. Error: {str(e)}")
        logger.error(f"Request URL: {url}")
        logger.error(f"Request headers: {headers}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Status code: {e.response.status_code}")
            logger.error(f"Response body: {e.response.text}")
        return None

def parse_comment(comment):
    pattern = r'/issueops add_repo\s+(\w+)\s+(\w+)/(\w+)'
    match = re.search(pattern, comment)
    return match.groups() if match else None

def get_pending_invitations(owner, repo):
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/invitations"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    pending_usernames = set()
    page = 1
    per_page = 100

    while True:
        params = {'page': page, 'per_page': per_page}
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            invitations = response.json()
            if not invitations:
                break
            for invite in invitations:
                invitee = invite.get('invitee', {})
                username = invitee.get('login')
                if username:
                    pending_usernames.add(username)
            page += 1
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch invitations for {owner}/{repo}. Error: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Status code: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            break

    return pending_usernames

def add_collaborator(collaborator, owner_repo):
    owner, repo = owner_repo.split('/')
    pending_usernames = get_pending_invitations(owner, repo)

    if collaborator in pending_usernames:
        logger.info(f"Collaborator '{collaborator}' has a pending invitation for {owner}/{repo}.")
        return

    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/collaborators/{collaborator}"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "permission": "admin"
    }

    try:
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        if response.status_code == 201:
            logger.info(f"Successfully added collaborator '{collaborator}' to {owner}/{repo}.")
        elif response.status_code == 204:
            logger.info(f"Collaborator '{collaborator}' is already a member of {owner}/{repo}.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to add collaborator '{collaborator}' to {owner}/{repo}. Error: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Status code: {e.response.status_code}")
            logger.error(f"Response body: {e.response.text}")

def main():
    if not TOKEN:
        logger.error("GitHub token not found. Please set the GITHUB_TOKEN environment variable.")
        return 1

    if not COMMENT_BODY:
        logger.error("COMMENT_BODY not found. Please set the COMMENT_BODY environment variable.")
        return 1

    logger.info(f"Received comment: {COMMENT_BODY}")

    parsed_data = parse_comment(COMMENT_BODY)
    if parsed_data:
        collaborator, owner, repo = parsed_data
        logger.info(f"Parsed data - Collaborator: {collaborator}, Owner: {owner}, Repo: {repo}")
        user_id = get_user_id(collaborator)
        if user_id:
            add_collaborator(collaborator, f"{owner}/{repo}")
        else:
            logger.error(f"Failed to get user ID for {collaborator}. Skipping invitation.")
    else:
        logger.error("Invalid command format. Use '/issueops add_repo username owner/repo'")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())