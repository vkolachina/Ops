import os
import sys
import requests

GITHUB_API_URL = "https://api.github.com"
TOKEN = os.getenv('GITHUB_TOKEN')

def add_user_to_repo(username, repo, permission):
    owner, repo_name = repo.split('/')
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo_name}/collaborators/{username}"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"permission": permission}
    
    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f"Successfully added {username} to {repo} with {permission} permission")
    else:
        print(f"Failed to add {username} to {repo}. Status code: {response.status_code}")
        print(response.json())

def main(users_data):
    for user_data in users_data:
        username, repo, permission = user_data.split(',')
        add_user_to_repo(username.strip(), repo.strip(), permission.strip())

if __name__ == "__main__":
    users_data = sys.argv[1].split(';')
    main(users_data)