import os
import subprocess

def run_script_for_all_repos(parent_folder, script_path):
    for root, dirs, files in os.walk(parent_folder):
        for dir_name in dirs:
            repo_path = os.path.join(root, dir_name)
            if os.path.isdir(repo_path):
                if(".git" in repo_path):
                    return
                print(f"\nRunning the script for repo: {repo_path}")
                try:
                    subprocess.run(['python', script_path, repo_path], check=True)
                    print(f"Finished processing repo: {repo_path}")
                except subprocess.CalledProcessError as e:
                    print(f"Error processing repo {repo_path}: {e}")

if __name__ == "__main__":
    parent_folder = "D:\\bakis\\non_bot_repos_examine"
    script_path = "D:\\GitHub api script\\libyear_tracker.py"

    run_script_for_all_repos(parent_folder, script_path)
