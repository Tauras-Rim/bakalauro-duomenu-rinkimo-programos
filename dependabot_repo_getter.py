import requests
import time

GITHUB_TOKEN = ""  # Replace with GitHub token
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

OUTPUT_FILE = "matching_repos.txt"
SIZE_RANGES = [(500, 1200)]

def check_rate_limit():
    """Check GitHub API rate limits and wait if necessary."""
    url = "https://api.github.com/rate_limit"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code == 200:
        rate_data = response.json()      
        remaining = rate_data["rate"]["remaining"]
        reset_time = rate_data["rate"]["reset"]

        if remaining == 0:
            wait_time = reset_time - time.time()
            print(f"Rate limit exceeded! Waiting {int(wait_time)} seconds...")
            time.sleep(wait_time + 1)
    else:
        print(f"Failed to check rate limit: {response.status_code}, {response.json()}")

def make_request(url):
    """Make a request with rate limit handling."""
    retries = 0
    while retries < 5:
        check_rate_limit()
        response = requests.get(url, headers=HEADERS)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403 and "secondary rate limit" in response.text:
            wait_time = (2 ** retries) * 5
            print(f"Secondary rate limit hit. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
            retries += 1
        else:
            print(f"Request failed: {response.status_code}, {response.json()}")
            break

    return None

def search_repos_with_dependabot():
    """Search for repositories containing dependabot.yml using the size trick."""
    repos_with_dependabot = set()

    for min_size, max_size in SIZE_RANGES:
        page = 1
        while True:
            print(f"Searching in ranges: {min_size}-{max_size}")
            query = f"filename:dependabot.yml+language:YAML+size:{min_size}..{max_size}"
            url = f"https://api.github.com/search/code?q={query}&per_page=100&page={page}"
            response_data = make_request(url)

            if response_data:
                items = response_data.get("items", [])
                if not items:
                    break
                for item in items:
                    repo_name = item["repository"]["full_name"]
                    repos_with_dependabot.add(repo_name)
                if len(items) < 100:
                    break
                page += 1
            else:
                break

    return repos_with_dependabot

def filter_repos_by_language_and_stars(repos):
    """Filter repositories by language (C#) and 10+ stars."""
    matching_repos = {}

    for repo in repos:
        url = f"https://api.github.com/repos/{repo}"
        response_data = make_request(url)

        if response_data:
            stars = response_data.get("stargazers_count", 0)
            language = response_data.get("language", "")

            if language == "C#" and stars >= 10:
                matching_repos[repo] = stars

    return matching_repos

if __name__ == "__main__":
    print("Searching for repositories with dependabot.yml using size trick...")
    repos_with_dependabot = search_repos_with_dependabot()

    print("Filtering repositories (C#, 10+ stars)...")
    matching_repos = filter_repos_by_language_and_stars(repos_with_dependabot)

    print(f"Found {len(matching_repos)} repositories that meet all criteria.")

    with open(OUTPUT_FILE, "a") as file:
        for repo, stars in matching_repos.items():
            print(f"{repo} ({stars} stars)")
            file.write(f"{repo}\n")

    print(f"✅ Repositories saved to {OUTPUT_FILE}")
