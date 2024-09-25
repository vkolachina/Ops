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

def main():
    comment_body = os.getenv('COMMENT_BODY')
    if not comment_body:
        print("Error: COMMENT_BODY not found. Please set the COMMENT_BODY environment variable.")
        sys.exit(1)

    users_data = [line.strip() for line in comment_body.split('\n') 
                  if line.strip() and not line.startswith('/')]

    for user_data in users_data:
        try:
            parts = user_data.split(',')
            if len(parts) != 3:
                print(f"Invalid format for user data: {user_data}")
                continue
            username, repo, permission = parts
            add_user_to_repo(username.strip(), repo.strip(), permission.strip())
        except ValueError as e:
            print(f"Error processing user data: {user_data}")
            print(f"Error message: {str(e)}")
        except Exception as e:
            print(f"Unexpected error processing user data: {user_data}")
            print(f"Error message: {str(e)}")

if __name__ == "__main__":
    main()