import os
import subprocess

REPO_FILE = "non_bot_repos.txt" 
CLONE_DIR = "D:\\bakis\\additional_non_bot_repos"

def ensure_directory_exists(directory):
    """Creates the target directory if it does not exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def clone_repositories():
    """Reads repo names from a file and clones them into the target folder."""
    ensure_directory_exists(CLONE_DIR)

    with open(REPO_FILE, "r") as file:
        repos = [line.strip() for line in file.readlines() if line.strip()]

    for repo in repos:
        repo_name = repo.split("/")[-1]
        repo_path = os.path.join(CLONE_DIR, repo_name)

        if os.path.exists(repo_path):
            print(f"Skipping {repo}, already cloned.")
            continue

        clone_url = f"https://github.com/{repo}.git"
        print(f"Cloning {repo}...")

        result = subprocess.run(["git", "clone", clone_url, repo_path], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Successfully cloned {repo}")
        else:
            print(f"Failed to clone {repo}: {result.stderr}")

if __name__ == "__main__":
    clone_repositories()
