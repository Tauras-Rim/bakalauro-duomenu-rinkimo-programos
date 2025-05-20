import os
import subprocess
import requests
import time
import re

GITHUB_TOKEN = ""  # # Replace with GitHub token
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

BOT_NAMES = {"dependabot", "depfu", "greenkeeper", "pyup", "renovate"}

ROOT_FOLDER = "D:\\bakis\\non_bot_repos_examine"

def check_rate_limit():
    """Check and wait for GitHub API rate limit reset if necessary."""
    url = "https://api.github.com/rate_limit"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        rate_data = response.json()
        remaining = rate_data["rate"]["remaining"]
        reset_time = rate_data["rate"]["reset"]
        if remaining == 0:
            wait_time = reset_time - time.time()
            print(f"Waiting {int(wait_time)} seconds for rate limit reset...")
            time.sleep(wait_time + 1)

def make_request(url):
    """Make API request with retry and rate-limit logic."""
    for attempt in range(5):
        check_rate_limit()
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            print(f"⚠Rate limit or access issue. Retrying ({attempt+1}/5)...")
            time.sleep((2 ** attempt) * 5)
        else:
            print(f"Error {response.status_code}: {response.text}")
            break
    return None

def extract_github_repo_url(repo_path):
    """Extract GitHub repo owner/name from git remote."""
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "remote", "get-url", "origin"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        url = result.stdout.strip()

        if url.startswith("git@github.com:"):
            match = re.match(r"git@github.com:(.+/.+?)(\.git)?$", url)
        else:
            match = re.match(r"https://github.com/(.+/.+?)(\.git)?$", url)

        if match:
            return match.group(1)
    except subprocess.CalledProcessError:
        return None
    return None

def has_bot_merged_prs(repo_full_name):
    """Check if repo has merged PRs by known bots."""
    page = 1
    while True:
        url = f"https://api.github.com/repos/{repo_full_name}/pulls?state=closed&per_page=100&page={page}"
        pr_data = make_request(url)
        if not pr_data:
            return False

        for pr in pr_data:
            if pr.get("merged_at"):
                author = pr["user"]["login"].lower()
                if any(bot in author for bot in BOT_NAMES):
                    return True

        if len(pr_data) < 100:
            break
        page += 1
    return False

def main():
    print("Scanning repositories for bot-authored merged PRs...")
    for repo_dir in os.listdir(ROOT_FOLDER):
        full_path = os.path.join(ROOT_FOLDER, repo_dir)
        if not os.path.isdir(full_path):
            continue
        if not os.path.isdir(os.path.join(full_path, ".git")):
            continue

        repo_full_name = extract_github_repo_url(full_path)
        if not repo_full_name:
            continue

        print(f"Checking {repo_full_name}...", end=" ", flush=True)
        if has_bot_merged_prs(repo_full_name):
            print("BOT PR FOUND")
            print(f"{repo_dir}")
        else:
            print("No bot PRs")

if __name__ == "__main__":
    main()
