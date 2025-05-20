import os
import csv
from datetime import datetime
from collections import defaultdict
import subprocess

def run_command(command, cwd=None):
    result = subprocess.run(
        command,
        cwd=cwd,
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {result.stderr}")
    return result.stdout.strip()

def checkout_main_or_master(repo_path):
    branches = run_command("git branch -a", cwd=repo_path)
    if "remotes/origin/main" in branches:
        run_command("git checkout main", cwd=repo_path)
    elif "remotes/origin/master" in branches:
        run_command("git checkout master", cwd=repo_path)
    else:
        raise RuntimeError("No 'main' or 'master' branch found.")

def get_all_months(start="2023-01"):
    """Generate all months from start (inclusive) to current month."""
    months = []
    current = datetime.strptime(start, "%Y-%m")
    now = datetime.now()
    while current <= now:
        months.append(current.strftime("%Y-%m"))
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)
    return months

def get_monthly_commits_since(repo_path, min_month="2023-01"):
    log_output = run_command(
        'git log --date=short --pretty=format:"%H %ad"', cwd=repo_path
    )
    commits_by_month = set()
    for line in log_output.splitlines():
        parts = line.strip("'").split()
        if len(parts) >= 2:
            date_str = parts[1]
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                month_key = date_obj.strftime("%Y-%m")
                if month_key >= min_month:
                    commits_by_month.add(month_key)
            except ValueError:
                continue
    return commits_by_month

def analyze_repos_in_folder(folder_path, min_month="2023-01", output_csv="non_bot_repo_activity.csv"):
    all_months = get_all_months(min_month)
    results = []

    for repo_name in os.listdir(folder_path):
        repo_path = os.path.join(folder_path, repo_name)
        if os.path.isdir(repo_path) and os.path.exists(os.path.join(repo_path, ".git")):
            print(f"\nChecking {repo_name}...")
            try:
                checkout_main_or_master(repo_path)
                active_months = get_monthly_commits_since(repo_path, min_month)
                row = [repo_name] + [1 if month in active_months else 0 for month in all_months]
                results.append(row)
            except Exception as e:
                print(f"Failed to process {repo_name}: {e}")

    with open(output_csv, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Repository"] + all_months)
        writer.writerows(results)

    print(f"\nDetailed activity results written to {output_csv}")

if __name__ == "__main__":
    folder_path = r"D:\\bakis\\additional_non_bot_repos"
    analyze_repos_in_folder(folder_path)
