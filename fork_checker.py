import requests

repo_file_path = 'non_bot_repos.txt'

api_url = "https://api.github.com/repos/"

token = ''  # Replace with GitHub token

def check_if_fork(owner, repo):
    url = f"{api_url}{owner}/{repo}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        repo_data = response.json()
        return repo_data['fork']
    elif response.status_code == 403:
        print("Error 403: Rate limit exceeded or authentication failed.")
    else:
        print(f"Error: {response.status_code} for {owner}/{repo}")
    return None

with open(repo_file_path, 'r') as file:
    repos = file.readlines()
forks = 0
for repo in repos:
    repo = repo.strip()

    if '/' in repo:
        owner, repo_name = repo.split('/')
        is_fork = check_if_fork(owner, repo_name)
        
        if is_fork is not None:
            if is_fork:
                print(f"{owner}/{repo_name} is a fork.")
                forks += 1
            else:
                print(f"{owner}/{repo_name} is NOT a fork.")
        else:
            print(f"Could not fetch data for {owner}/{repo_name}")
    else:
        print(f"Invalid repository format: {repo}")
print(f"total forks: {forks}")