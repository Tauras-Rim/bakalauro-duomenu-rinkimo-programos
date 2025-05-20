import subprocess
import os
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from collections import defaultdict
import csv
from datetime import timedelta
import argparse

def run_command(command, cwd=None, ignore_error=False):
    process = subprocess.Popen(
        command,
        cwd=cwd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8"
    )
    output, _ = process.communicate()
    if process.returncode != 0 and ignore_error != True:
        print(f"Command failed: {command}\n{output}")
    return output

def extract_total_libyear(output):
    match = re.search(r"Total\s+is\s+([\d,\.]+)\s+libyears\s+behind", output)
    if match:
        libyears = output.split("Total is")
        match = re.search(r"([\d,\.]+)\s+libyears\s+behind", libyears[1])
        value_str = match.group(1).replace(",", ".")
        try:
            return float(value_str)
        except ValueError:
            print(f"Error converting {value_str} to float.")
            return None
    
    match = re.search(r"Project\s+is\s+([\d,\.]+)\s+libyears\s+behind", output)
    if match:
        libyears = output.split("Project is")
        match = re.search(r"([\d,\.]+)\s+libyears\s+behind", libyears[1])
        value_str = match.group(1).replace(",", ".")
        try:
            return float(value_str)
        except ValueError:
            print(f"Error converting {value_str} to float.")
            return None

    return None

def extract_old_dependencies(output, threshold=100.0):
    old_deps = []
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("│") and line.endswith("│"):
            parts = [part.strip() for part in line.strip("│").split("│")]
            if len(parts) >= 6:
                package_name = parts[0]
                try:
                    age_str = parts[5].replace(",", ".")
                    age = float(age_str)
                    if age > threshold:
                        old_deps.append((package_name, age))
                except ValueError:
                    continue
    return old_deps

def get_monthly_commits(repo_path, min_month="2020-01"):
    log_output = run_command(
        'git log --date=short --pretty=format:"%H %ad"', cwd=repo_path
    )
    commits_by_month = defaultdict(list)

    for line in log_output.splitlines():
        parts = line.strip("'").split()
        if len(parts) >= 2:
            commit_hash = parts[0]
            date_str = parts[1]
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            key = date_obj.strftime("%Y-%m")

            if key >= min_month:
                commits_by_month[key].append((commit_hash, date_obj))

    latest_commits = {
        month: sorted(commits, key=lambda x: x[1])[-1][0]
        for month, commits in commits_by_month.items()
    }

    return dict(sorted(latest_commits.items()))


def find_valid_csproj_files(repo_path):
    valid_files = []

    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".csproj"):
                file_path = os.path.join(root, file)
                try:
                    tree = ET.parse(file_path)
                    root_elem = tree.getroot()

                    if root_elem.find(".//RuntimeVersion") is not None:
                        print(f"Skipping due to <RuntimeVersion>: {file_path}")
                        continue
                    if root_elem.find(".//DotNetVersion") is not None:
                        print(f"Skipping due to <DotNetVersion>: {file_path}")
                        continue

                    package_refs = root_elem.findall(".//PackageReference")
                    packages = set()
                    skip_file = False

                    for pr in package_refs:
                        include_attr = pr.attrib.get("Include")
                        version_attr = pr.attrib.get("Version")

                        if version_attr and "$(" in version_attr:
                            print(f"⚠Skipping due to variable version: {file_path}")
                            skip_file = True
                            break

                        if not include_attr:
                            continue
                        if include_attr in packages:
                            print(f"⚠Skipping due to duplicate packages: {file_path}")
                            skip_file = True
                            break
                        packages.add(include_attr)

                    if not skip_file:
                        valid_files.append(file_path)

                except Exception as e:
                    print(f"⚠Skipping {file_path} due to parse error: {e}")

    return valid_files


def find_dependabot_introduction_date(repo_path):
    yml_log = run_command("git log --diff-filter=A --pretty=format:'%ad' --date=short -- .github/dependabot.yml", cwd=repo_path)
    yaml_log = run_command("git log --diff-filter=A --pretty=format:'%ad' --date=short -- .github/dependabot.yaml", cwd=repo_path)

    dates = []

    for line in yml_log.splitlines() + yaml_log.splitlines():
        line = line.strip("'").strip()
        if re.match(r"\d{4}-\d{2}-\d{2}", line):
            dates.append(datetime.strptime(line, "%Y-%m-%d"))

    if not dates:
        return None
    earliest = min(dates)
    return earliest.strftime("%Y-%m")

def split_projects_into_chunks(projects, max_length=3000):
    chunks = []
    current_chunk = []
    current_length = 0
    
    for project in projects:
        project_length = len(project)
        if current_length + project_length + len(current_chunk) > max_length:
            chunks.append(current_chunk)
            current_chunk = [project]
            current_length = project_length
        else:
            current_chunk.append(project)
            current_length += project_length
            
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def measure_libyear(repo_path):
    global DEP_ADDED
    original_branch = run_command("git rev-parse --abbrev-ref HEAD", cwd=repo_path).strip()
    monthly_commits = get_monthly_commits(repo_path)

    DEP_ADDED = find_dependabot_introduction_date(repo_path)

    print(f"\nDependabot was added in: {DEP_ADDED if DEP_ADDED else 'Not detected'}")

    results = {}

    for month, commit_hash in monthly_commits.items():
        print(f"\nChecking {month}...")

        checkout_output = run_command("git checkout main --force", cwd=repo_path, ignore_error=True)
        if "error" in checkout_output.lower() or "did not match any file(s)" in checkout_output.lower():
            run_command("git checkout master --force", cwd=repo_path)

        try:
            run_command("git reset --hard", cwd=repo_path)
            run_command(f"git checkout {commit_hash} --force", cwd=repo_path)

            global_json_path = os.path.join(repo_path, "global.json")   
            global_json_exists = os.path.isfile(global_json_path)
            if global_json_exists:
                global_json_backup_path = global_json_path + "renamed.bak"
                os.rename(global_json_path, global_json_backup_path)

            try:
                valid_projects = find_valid_csproj_files(repo_path)
                if not valid_projects:
                    print("⚠No valid .csproj files found, skipping.")
                    results[month] = None
                    continue

                project_chunks = split_projects_into_chunks(valid_projects)

                total_adjusted = 0.0
                for chunk in project_chunks:
                    print(f"Running 'dotnet libyear' for chunk of {len(chunk)} projects in month {month}...")
                    joined_projects = " ".join(f'"{proj}"' for proj in chunk)
                    result = run_command(f"dotnet libyear {joined_projects}", cwd=repo_path)

                    total = extract_total_libyear(result)
                    old_deps = extract_old_dependencies(result)
                    old_sum = sum(age for _, age in old_deps)

                    if total is not None:
                        adjusted = max(0.0, total - old_sum)
                        print(f"Chunk: {adjusted:.2f} libyears behind (adjusted, -{old_sum:.2f} from deprecated)")
                        total_adjusted += adjusted
                    else:
                        print(f"⚠Could not parse libyear for chunk")

                results[month] = total_adjusted

            finally:
                if global_json_exists and os.path.isfile(global_json_backup_path):
                    os.rename(global_json_backup_path, global_json_path)

        except Exception as e:
            print(f"Error checking {month}: {e}")
            results[month] = None

    run_command(f"git checkout {original_branch} --force", cwd=repo_path)

    return results

def write_results_to_csv(results, repo_path, start_year=2020, end_year=2025, output_file="results_non_bot_examine.csv"):
    all_months = [
        f"{year:04d}-{month:02d}"
        for year in range(start_year, end_year + 1)
        for month in range(1, 13)
    ]

    project_name = os.path.basename(repo_path.rstrip("\\/"))
    header_row = [""] + all_months
    dependabot_month = find_dependabot_introduction_date(repo_path)

    if dependabot_month is None:
        values_row = [project_name]
        for month in all_months:
            value = results.get(month)
            if value is not None:
                rounded_str = f"{round(value, 1):.1f}".replace(".", ",")
                if month == dependabot_month:
                    values_row.append(f"{rounded_str}d")
                else:
                    values_row.append(rounded_str)
            else:
                values_row.append("0")

        file_exists = os.path.isfile(output_file)

        with open(output_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            if not file_exists:
                writer.writerow(header_row)
            writer.writerow(values_row)

        print(f"\nCSV updated at: {output_file}")
    else:
        output_file = "results_bot_examine.csv"
        values_row = [project_name]
        for month in all_months:
            value = results.get(month)
            if value is not None:
                rounded_str = f"{round(value, 1):.1f}".replace(".", ",")
                if month == dependabot_month:
                    values_row.append(f"{rounded_str}d")
                else:
                    values_row.append(rounded_str)
            else:
                values_row.append("0")

        file_exists = os.path.isfile(output_file)

        with open(output_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            if not file_exists:
                writer.writerow(header_row)
            writer.writerow(values_row)

        print(f"\nCSV updated at: {output_file}")

def fill_missing_months(results, start_year=2020, end_year=2025):
    all_months = [
        f"{year:04d}-{month:02d}"
        for year in range(start_year, end_year + 1)
        for month in range(1, 13)
    ]

    filled_results = {}
    last_value = 0

    for month in all_months:
        if month in results and results[month] is not None:
            last_value = results[month]
        filled_results[month] = last_value

    return filled_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze .NET repository dependency freshness.")
    parser.add_argument("repo_path", help="Path to the .NET repository")
    args = parser.parse_args()

    all_results = measure_libyear(args.repo_path)
    filled_results = fill_missing_months(all_results)

    print("\nFinal Results:")
    for month, value in filled_results.items():
        if month == find_dependabot_introduction_date(args.repo_path):
            print(f"{month}: {round(value, 1)} libyears (dependabot added here)")
        else:
            print(f"{month}: {round(value, 1)} libyears")

    write_results_to_csv(filled_results, args.repo_path)
