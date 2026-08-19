#!/usr/bin/env python3
import json
import os
import re
import sys
import urllib.request

USERNAME = "Hevin-CJ"
README_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "README.md"))
START_MARKER = "<!-- RECENT-REPOS:START -->"
END_MARKER = "<!-- RECENT-REPOS:END -->"


def fetch_repositories(username: str):
    url = f"https://api.github.com/users/{username}/repos?sort=pushed&direction=desc&per_page=100"
    token = os.environ.get("GITHUB_TOKEN")
    
    headers = {
        "User-Agent": f"Python-urllib/{username}-repo-updater",
        "Accept": "application/vnd.github.v3+json",
    }
    if token:
        headers["Authorization"] = f"token {token}"
        
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data
    except Exception as e:
        print(f"Error fetching repositories from GitHub API: {e}", file=sys.stderr)
        return []


def generate_markdown_table(repos):
    # Filter out forks and the profile configuration repo
    filtered_repos = [
        r for r in repos
        if not r.get("fork", False)
        and r.get("name", "").lower() != USERNAME.lower()
        and not r.get("private", False)
    ]

    if not filtered_repos:
        return "<p align=\"center\"><em>No public repositories found.</em></p>"

    # Take up to top 6 repositories
    top_repos = filtered_repos[:6]

    lines = [
        "<table>",
        "  <thead>",
        "    <tr>",
        "      <th align=\"left\">🚀 Project</th>",
        "      <th align=\"left\">📝 Description</th>",
        "      <th align=\"center\">🛠️ Language</th>",
        "      <th align=\"center\">⭐ Stars</th>",
        "      <th align=\"center\">🍴 Forks</th>",
        "    </tr>",
        "  </thead>",
        "  <tbody>"
    ]

    for repo in top_repos:
        name = repo.get("name", "")
        url = repo.get("html_url", f"https://github.com/{USERNAME}/{name}")
        desc = repo.get("description") or "No description provided."
        lang = repo.get("language") or "Markdown / Other"
        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)

        lines.append("    <tr>")
        lines.append(f"      <td><a href=\"{url}\"><b>{name}</b></a></td>")
        lines.append(f"      <td>{desc}</td>")
        lines.append(f"      <td align=\"center\"><code>{lang}</code></td>")
        lines.append(f"      <td align=\"center\">{stars}</td>")
        lines.append(f"      <td align=\"center\">{forks}</td>")
        lines.append("    </tr>")

    lines.append("  </tbody>")
    lines.append("</table>")

    return "\n".join(lines)


def update_readme():
    print(f"Fetching repositories for {USERNAME}...")
    repos = fetch_repositories(USERNAME)
    table_content = generate_markdown_table(repos)

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        f"{re.escape(START_MARKER)}[\\s\\S]*?{re.escape(END_MARKER)}",
        re.MULTILINE
    )

    replacement = f"{START_MARKER}\n{table_content}\n{END_MARKER}"

    if not pattern.search(content):
        print(f"Markers {START_MARKER} and {END_MARKER} not found in {README_PATH}", file=sys.stderr)
        return False

    new_content = pattern.sub(replacement, content)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("Successfully updated README.md with latest repositories.")
    return True


if __name__ == "__main__":
    if not update_readme():
        sys.exit(1)
