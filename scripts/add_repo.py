import requests
import os
import re
import sys

GITHUB_API_URL = "https://api.github.com"
TOKEN = os.getenv('GITHUB_TOKEN')
COMMENT_BODY = os.getenv('COMMENT_BODY')

def parse_comment(comment):
    """
    Parses the comment body for the command to add a collaborator.
    Expects the format: /issueops add_repo collaborator owner/repo
    """
    pattern = r'/issueops add_repo\s+(\w+)\s+(\w+)/(\w+)'
    match = re.search(pattern, comment)
    if match:
        return match.groups()
    return None

def get_pending_invitations(owner, repo):
    """
    Fetches pending invitations for the given repository.
    Returns a set of usernames who have pending invitations.
    """
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
            print(f"Error: Failed to fetch invitations for {owner}/{repo}.")
            print(f"Exception: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Status code: {e.response.status_code}")
                print(f"Response body: {e.response.text}")
            break

    return pending_usernames

def add_collaborator(collaborator, owner, repo):
    """
    Adds a collaborator to a given repository. If the user has a pending invitation,
    it will be treated as already added.
    """
    pending_usernames = get_pending_invitations(owner, repo)

    if collaborator in pending_usernames:
        print(f"Info: Collaborator '{collaborator}' has a pending invitation for {owner}/{repo}.")
        return

    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/collaborators/{collaborator}"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "permission": "admin"  # You can adjust this to the desired permission: pull, push, admin
    }

    try:
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        if response.status_code == 201:
            print(f"Success: Collaborator '{collaborator}' was added to {owner}/{repo}.")
        elif response.status_code == 204:
            print(f"Info: Collaborator '{collaborator}' is already a member of {owner}/{repo}.")
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to add collaborator '{collaborator}' to {owner}/{repo}.")
        print(f"Exception: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            print(f"Response body: {e.response.text}")

def main():
    # Ensure the GITHUB_TOKEN is available
    if not TOKEN:
        print("Error: GitHub token not found. Please set the GITHUB_TOKEN environment variable.")
        return 1

    # Ensure the COMMENT_BODY is available
    if not COMMENT_BODY:
        print("Error: COMMENT_BODY not found. Please set the COMMENT_BODY environment variable.")
        return 1

    # Parse the comment for command information
    parsed_data = parse_comment(COMMENT_BODY)
    if parsed_data:
        collaborator, owner, repo = parsed_data
        print(f"Parsed data - Collaborator: {collaborator}, Owner: {owner}, Repo: {repo}")
        add_collaborator(collaborator, owner, repo)
    else:
        print("Error: Invalid command format. Use '/issueops add_repo username owner/repo'")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())