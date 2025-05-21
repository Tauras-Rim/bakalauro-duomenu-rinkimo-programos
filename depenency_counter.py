import os
import csv
import xml.etree.ElementTree as ET

def count_dependencies_in_csproj(csproj_path):
    try:
        tree = ET.parse(csproj_path)
        root = tree.getroot()
        namespace = {'msbuild': 'http://schemas.microsoft.com/developer/msbuild/2003'}

        package_refs = root.findall('.//PackageReference') or root.findall('.//msbuild:PackageReference', namespace)
        return len(package_refs)
    except ET.ParseError:
        print(f"Failed to parse: {csproj_path}")
        return 0

def count_project_dependencies(repo_path):
    total = 0
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".csproj"):
                csproj_path = os.path.join(root, file)
                count = count_dependencies_in_csproj(csproj_path)
                total += count
    return total

def count_dependencies_in_all_repos(base_folder, output_csv="non_bot_dependency_counts.csv"):
    results = []
    grand_total = 0
    print("Dependency counts per project:\n")

    for repo_name in os.listdir(base_folder):
        repo_path = os.path.join(base_folder, repo_name)
        if os.path.isdir(repo_path) and os.path.exists(os.path.join(repo_path, ".git")):
            count = count_project_dependencies(repo_path)
            print(f"{repo_name}: {count} dependencies")
            results.append((repo_name, count))
            grand_total += count

    print(f"\nTotal dependencies across all projects: {grand_total}")

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Project", "Dependency Count"])
        writer.writerows(results)
        writer.writerow(["TOTAL", grand_total])

    print(f"Results written to {output_csv}")

if __name__ == "__main__":
    base_folder = r"D:\\bakis\\non_bot_repos_examine"
    count_dependencies_in_all_repos(base_folder)
