import os
import re
import csv
import subprocess
import xml.etree.ElementTree as ET
from datetime import datetime
from collections import defaultdict
import argparse

def run_command(command, cwd=None):
    result = subprocess.run(
        command,
        cwd=cwd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        encoding='utf-8',
        errors='ignore'
    )
    return result.stdout.strip()


def get_monthly_commits(repo_path, min_month="2020-01"):
    log_output = run_command('git log --date=short --pretty=format:"%H %ad"', cwd=repo_path)
    commits_by_month = defaultdict(list)

    for line in log_output.splitlines():
        parts = line.strip('"').split()
        if len(parts) == 2:
            commit_hash, date_str = parts
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            key = date_obj.strftime("%Y-%m")
            if key >= min_month:
                commits_by_month[key].append((commit_hash, date_obj))

    latest_commits = {
        month: sorted(commits, key=lambda x: x[1])[-1][0]
        for month, commits in commits_by_month.items()
    }
    return dict(sorted(latest_commits.items()))

def count_dependencies_in_csproj(csproj_path):
    try:
        tree = ET.parse(csproj_path)
        root = tree.getroot()
        ns = {'msbuild': 'http://schemas.microsoft.com/developer/msbuild/2003'}
        package_refs = root.findall(".//PackageReference") or root.findall(".//msbuild:PackageReference", ns)
        return len(package_refs)
    except Exception:
        return 0

def count_total_dependencies(repo_path):
    total = 0
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".csproj"):
                csproj_path = os.path.join(root, file)
                total += count_dependencies_in_csproj(csproj_path)
    return total

def analyze_dependency_trends(repo_path):
    original_branch = run_command("git rev-parse --abbrev-ref HEAD", cwd=repo_path).strip()
    monthly_commits = get_monthly_commits(repo_path)
    results = {}

    for month, commit_hash in monthly_commits.items():
        print(f"🔄 Checking {month}...")
        run_command("git reset --hard", cwd=repo_path)
        run_command(f"git checkout {commit_hash} --force", cwd=repo_path)
        count = count_total_dependencies(repo_path)
        print(f"{month}: {count} dependencies")
        results[month] = count

    run_command(f"git checkout {original_branch} --force", cwd=repo_path)
    return results

def write_results_to_csv(results, repo_path, output_file="non_bot_dependency_trend.csv", start_year=2020, end_year=2025):
    all_months = [
        f"{year:04d}-{month:02d}"
        for year in range(start_year, end_year + 1)
        for month in range(1, 13)
    ]

    project_name = os.path.basename(repo_path.rstrip("\\/"))
    header_row = ["Project"] + all_months
    values_row = [project_name]

    last_value = 0
    for month in all_months:
        if month in results:
            last_value = results[month]
        values_row.append(last_value)

    file_exists = os.path.isfile(output_file)
    with open(output_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        if not file_exists:
            writer.writerow(header_row)
        writer.writerow(values_row)

    print(f"\nResults saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Track total dependency count over time for a .NET project.")
    parser.add_argument("repo_path", help="Path to the repository")
    args = parser.parse_args()

    results = analyze_dependency_trends(args.repo_path)
    write_results_to_csv(results, args.repo_path)
