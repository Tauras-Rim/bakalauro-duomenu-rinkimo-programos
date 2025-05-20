import requests
import time

GITHUB_TOKEN = ""  # Replace with GitHub token
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

BOT_AUTHORS = ["dependabot", "renovate-bot", "depfu", "greenkeeper[bot]"]
SEARCH_QUERY = "language:C# stars:>=10"
MAX_REPOS = 200
OUTPUT_FILE = "non_bot_repos.txt"
EXISTING_FILE = "non_bot_repos_done.txt"


def load_existing_repos():
    """Load previously found repositories from file."""
    try:
        with open(EXISTING_FILE, "r") as file:
            return set(file.read().splitlines())
    except FileNotFoundError:
        return set()

def fetch_repositories(existing_repos):
    """Fetch new repositories that haven't been checked yet, using created-date-based queries."""
    repos = []
    
    for start_date, end_date in DATE_RANGES:
        page = 1

        DATE_RANGES = [("2022-01-01", "2022-01-15"), ("2022-01-16", "2022-01-30"),
                ("2022-02-01", "2022-02-15"), ("2022-02-16", "2022-02-28"),
                ("2022-03-01", "2022-03-15"), ("2022-03-16", "2022-03-30"),
                ("2022-04-01", "2022-04-15"), ("2022-04-16", "2022-04-30"),
                ("2022-05-01", "2022-05-15"), ("2022-05-16", "2022-05-30"),
                ("2022-06-01", "2022-06-15"), ("2022-06-16", "2022-06-30"),
                ("2022-07-01", "2022-07-15"), ("2022-07-16", "2022-07-30"),
                ("2022-08-01", "2022-08-15"), ("2022-08-16", "2022-08-30"),
                ("2022-09-01", "2022-09-15"), ("2022-09-16", "2022-09-30"),
                ("2022-10-01", "2022-10-15"), ("2022-10-16", "2022-10-30"),
                ("2022-11-01", "2022-11-15"), ("2022-11-16", "2022-11-30"),
                ("2022-12-01", "2022-12-15"), ("2022-12-16", "2022-12-30")]
        
        while len(repos) < MAX_REPOS:
            exclude_query = " ".join(f"-repo:{repo}" for repo in existing_repos)
            search_query = f"language:C#+stars:>=10+created:{start_date}..{end_date} {exclude_query}"

            url = f"https://api.github.com/search/repositories?q={search_query}&per_page=30&page={page}"
            response = requests.get(url, headers=HEADERS).json()

            if "items" not in response:
                print("Error:", response)
                break
            
            for item in response["items"]:
                repo_full_name = item["full_name"]
                if repo_full_name not in existing_repos:
                    repos.append(item)

            if len(response["items"]) < 30:  # No more results
                break

            page += 1
            time.sleep(2)  # Avoid hitting rate limits

        if len(repos) >= MAX_REPOS:
            break  # Stop if we reached enough new repositories

    return repos[:MAX_REPOS]

def has_bot_pr(owner, repo):
    """Check all PRs for bot-created ones, paginating if necessary."""
    page = 1
    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=all&per_page=100&page={page}"
        response = requests.get(url, headers=HEADERS).json()

        if isinstance(response, dict) and "message" in response:
            print(f"Error fetching PRs for {owner}/{repo}: {response['message']}")
            return True 

        if not response:
            break

        for pr in response:
            author = pr.get("user", {}).get("login", "").lower()
            if any(bot in author for bot in BOT_AUTHORS):
                return True

        page += 1
        time.sleep(1)  # Avoid rate limits

    return False  # No bot-created PRs found

def main():
    existing_repos = load_existing_repos()
    print(f"Loaded {len(existing_repos)} previously found repositories.")

    print("Fetching additional repositories using created-date filtering...")
    new_repos = fetch_repositories(existing_repos)

    filtered_repos = []
    for repo in new_repos:
        owner = repo["owner"]["login"]
        repo_name = repo["name"]
        full_name = f"{owner}/{repo_name}"
        
        print(f"Checking PRs for {full_name}...")
        if not has_bot_pr(owner, repo_name):
            filtered_repos.append(full_name)

        if len(filtered_repos) >= MAX_REPOS:
            break  # Stop when we reach the required count

    # Save new results
    with open(OUTPUT_FILE, "a") as file:  # Append to the existing file
        for repo in filtered_repos:
            file.write(repo + "\n")

    print(f"\nAdded {len(filtered_repos)} new repositories to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()