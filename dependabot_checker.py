import requests
from time import sleep
import time

GITHUB_TOKEN = ""  # Replace with GitHub token
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

REPOS = [
    "NetFabric/NetFabric.Numerics",
    "beardgame/utilities",
    "exercism/csharp-analyzer",
    "lAnubisl/LostFilmTorrentsFeed",
    "TheJoeFin/Text-Grab",
    "fluentassertions/fluentassertions",
    "AwesomeAssertions/AwesomeAssertions",
    "morganstanley/Crossroads",
    "quasarke/arke",
    "CoreWebForms/CoreWebForms",
    "ConsumerDataRight/mock-data-recipient",
    "microsoft/axe-windows",
    "AzureAD/microsoft-identity-web",
    "Bullabs/Qitar",
    "hanabi1224/Programming-Language-Benchmarks",
    "ubisoft/NGitLab",
    "ConsumerDataRight/mock-data-holder",
    "microsoft/XmlNotepad",
    "dotnet/aspire-samples",
    "NetSparkleUpdater/NetSparkle",
    "microsoft/Comparative-Analysis-for-Sustainability-Solution-Accelerator",
    "microsoft/data-accelerator",
    "microsoft/kiota",
    "dotnet/aspnetcore",
    "apache/arrow-adbc",
    "dotnet/maui",
    "wabbajack-tools/wabbajack",
    "masesgroup/KNet",
    "DiverOfDark/BudgetTracker",
    "Azure/Bridge-To-Kubernetes",
    "godaddy/asherah",
    "dotnet/iot",
    "aws/cta",
    "Analogy-LogViewer/Analogy.LogViewer",
    "DataDog/dd-trace-dotnet",
    "borisdj/EFCore.BulkExtensions",
    "edumserrano/dotnet-sdk-extensions",
    "skst/LicenseManager",
    "dbolin/Apex.Analyzers",
    "vsantele/ArsenalMenuExtractor",
    "tcfialho/Herald.MessageQueue",
    "Tim-Maes/Bindicate",
    "devlooped/SponsorLink",
    "yellowfeather/dbf",
    "Vectron/PlcInterface",
    "desjarlais/ScintillaLexers",
    "glennawatson/GitSMimeSign",
    "danielmonettelli/dotnetmaui-meow-app-oss",
    "VladislavAntonyuk/WorldExplorer",
    "Eventuous/eventuous",
    "mganss/AhoCorasick",
    "Helco/zzio",
    "y-iihoshi/ThScoreFileConverter",
    "FirelyTeam/firely-cql-sdk",
    "dnnsoftware/Dnn.Platform",
    "JaCraig/SQLHelper",
    "midaskira/Hellstrap",
    "JaCraig/Enlighten",
    "JaCraig/BigBookOfDataTypes",
    "microsoft/teams-ai",
    "MarimerLLC/csla",
    "domaindrivendev/Swashbuckle.AspNetCore",
    "nsubstitute/NSubstitute",
    "Analogy-LogViewer/Analogy.LogViewer.Serilog",
    "aws/aws-toolkit-common",
    "eclipse-tractusx/portal-backend",
    "JaCraig/SQLParser",
    "nikosdaridis/qr-barcode-maui-blazor-hybrid",
    "GuVAnj8Gv3RJ/NeosAccountDownloader",
    "inthehand/32feet",
    "dotnet/efcore",
    "dotnet/extensions",
    "loresoft/NLog.Mongo",
    "TongjiPetWelfareProject/TongjiPetWelfare",
    "linkdotnet/Blog",
    "timonkrebs/MemoizR",
    "arition/SubRenamer",
    "microsoftgraph/msgraph-sdk-dotnet",
    "e-potashkin/BuberDinner",
    "karb0f0s/Telegram.Bot.Extensions.Markup",
    "linkdotnet/StringBuilder",
    "merken/Prise",
    "serilog-contrib/serilog-sinks-grafana-loki",
    "Washi1337/AsmResolver"
]

GITHUB_API_URL = "https://api.github.com"

def safe_get(url, headers, retries=3, wait=10):
    for attempt in range(retries):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response
        elif response.status_code == 403 and "secondary rate limit" in response.text.lower():
            print("Secondary rate limit hit. Waiting before retry...")
            time.sleep(wait * (attempt + 1))
        else:
            break
    return response

def get_dependabot_merged_prs_count(repo_full_name):
    """Returns the number of merged PRs by Dependabot for a repo."""
    query = f'repo:{repo_full_name} is:pr is:merged author:app/dependabot'
    url = f'{GITHUB_API_URL}/search/issues?q={query}'
    response = safe_get(url, headers=HEADERS)

    if response.status_code == 200:
        return response.json().get("total_count", 0)
    else:
        print(f"Failed to fetch PRs for {repo_full_name}: {response.status_code} {response.text}")
        return 0

def main():
    matching_repos = []
    low_activity_repos = []

    for repo in REPOS:
        print(f"Checking {repo}...")
        count = get_dependabot_merged_prs_count(repo)
        print(f"  -> Merged Dependabot PRs: {count}")
        if count >= 10:
            matching_repos.append((repo, count))
        else:
            low_activity_repos.append((repo, count))
        sleep(2)

    print("\n✅ Repositories with ≥ 10 merged Dependabot PRs:")
    for repo, count in matching_repos:
        print(f"- {repo}: {count} PRs")

    print("\n⚠️ Repositories with < 10 merged Dependabot PRs:")
    for repo, count in low_activity_repos:
        print(f"- {repo}: {count} PRs")


if __name__ == "__main__":
    main()
