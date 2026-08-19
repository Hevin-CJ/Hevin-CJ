#!/usr/bin/env python3
import html
import json
import os
import re
import sys
import urllib.request

USERNAME = "Hevin-CJ"
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
README_PATH = os.path.join(REPO_ROOT, "README.md")
CARDS_DIR = os.path.join(REPO_ROOT, "assets", "cards")
START_MARKER = "<!-- POPULAR-REPOS:START -->"
END_MARKER = "<!-- POPULAR-REPOS:END -->"

# Known GitHub language colors
LANGUAGE_COLORS = {
    "Kotlin": "#A97BFF",
    "Java": "#B07219",
    "Python": "#3572A5",
    "JavaScript": "#F1E05A",
    "TypeScript": "#3178C6",
    "C++": "#F34B7D",
    "C": "#555555",
    "Go": "#00ADD8",
    "Rust": "#DEA584",
    "HTML": "#E34C26",
    "CSS": "#563D7C",
    "Shell": "#89E051",
    "Dart": "#00B4AB",
    "Swift": "#F05138"
}


def get_headers():
    token = os.environ.get("GITHUB_TOKEN")
    headers = {
        "User-Agent": f"Python-urllib/{USERNAME}-card-generator",
        "Accept": "application/vnd.github.v3+json",
    }
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def fetch_public_repositories():
    url = f"https://api.github.com/users/{USERNAME}/repos?sort=pushed&direction=desc&per_page=100"
    req = urllib.request.Request(url, headers=get_headers())
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return [
                r for r in data
                if not r.get("private", False)
                and not r.get("fork", False)
                and r.get("name", "").lower() != USERNAME.lower()
            ]
    except Exception as e:
        print(f"Error fetching public repositories: {e}", file=sys.stderr)
        return []


def fetch_commit_count(repo_name: str) -> int:
    url = f"https://api.github.com/repos/{USERNAME}/{repo_name}/commits?per_page=1"
    req = urllib.request.Request(url, headers=get_headers())
    try:
        with urllib.request.urlopen(req) as resp:
            link = resp.headers.get("Link")
            if link and "last" in link:
                m = re.search(r"[?&]page=(\d+)>; rel=\"last\"", link)
                if m:
                    return int(m.group(1))
            data = json.loads(resp.read().decode("utf-8"))
            return len(data) if isinstance(data, list) else 0
    except Exception as e:
        print(f"Warning: Could not fetch commit count for {repo_name}: {e}", file=sys.stderr)
        return 0


def generate_svg_card(repo_data: dict, output_path: str):
    name = html.escape(repo_data.get("name", ""))
    raw_desc = repo_data.get("description") or "Modern open-source project."
    # Truncate description cleanly to 65 chars
    if len(raw_desc) > 65:
        desc = html.escape(raw_desc[:62].strip() + "...")
    else:
        desc = html.escape(raw_desc)

    lang = repo_data.get("language") or "Other"
    lang_color = LANGUAGE_COLORS.get(lang, "#635BFF")
    commits = repo_data.get("total_commits", 1)
    stars = repo_data.get("stargazers_count", 0)
    forks = repo_data.get("forks_count", 0)

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="410" height="135" viewBox="0 0 410 135" fill="none">
  <style>
    .card-bg {{
      fill: #0D1117;
      stroke: url(#border-grad);
      stroke-width: 1.5;
      rx: 12;
    }}
    .title {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
      font-size: 17px;
      font-weight: 700;
      fill: #58A6FF;
    }}
    .desc {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
      font-size: 12.5px;
      font-weight: 400;
      fill: #8B949E;
    }}
    .badge-text {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
      font-size: 11.5px;
      font-weight: 600;
      fill: #C9D1D9;
    }}
    .stat-text {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
      font-size: 11.5px;
      font-weight: 500;
      fill: #8B949E;
    }}
    @media (prefers-color-scheme: light) {{
      .card-bg {{
        fill: #FFFFFF;
        stroke: #D0D7DE;
      }}
      .title {{
        fill: #0969DA;
      }}
      .desc {{
        fill: #57606A;
      }}
      .badge-text {{
        fill: #24292F;
      }}
      .stat-text {{
        fill: #57606A;
      }}
    }}
  </style>

  <defs>
    <linearGradient id="border-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#635BFF" />
      <stop offset="50%" stop-color="#00F5D4" />
      <stop offset="100%" stop-color="#635BFF" />
    </linearGradient>
  </defs>

  <!-- Background Card -->
  <rect x="1" y="1" width="408" height="133" class="card-bg" />

  <!-- Repo Icon & Title -->
  <g transform="translate(18, 26)">
    <!-- Book/Repo Icon -->
    <path d="M4 1.75C4 .784 4.784 0 5.75 0h8.5C15.216 0 16 .784 16 1.75v12.5A1.75 1.75 0 0 1 14.25 16h-8.5A1.75 1.75 0 0 1 4 14.25V1.75ZM5.75 1.5a.25.25 0 0 0-.25.25v12.5c0 .138.112.25.25.25h8.5a.25.25 0 0 0 .25-.25V1.75a.25.25 0 0 0-.25-.25h-8.5Z" fill="#58A6FF" />
    <path d="M2 3.5a.75.75 0 0 1 .75-.75h.5a.75.75 0 0 1 0 1.5h-.5A.75.75 0 0 1 2 3.5Zm0 3a.75.75 0 0 1 .75-.75h.5a.75.75 0 0 1 0 1.5h-.5A.75.75 0 0 1 2 6.5Zm0 3a.75.75 0 0 1 .75-.75h.5a.75.75 0 0 1 0 1.5h-.5A.75.75 0 0 1 2 9.5Z" fill="#58A6FF" />
    <text x="24" y="13" class="title">{name}</text>
  </g>

  <!-- Description -->
  <text x="18" y="66" class="desc">{desc}</text>

  <!-- Language Chip, Commits, Stars, Forks -->
  <g transform="translate(18, 105)">
    <!-- Language Circle & Name -->
    <circle cx="5" cy="-4" r="5" fill="{lang_color}" />
    <text x="15" y="0" class="badge-text">{html.escape(lang)}</text>

    <!-- Commits Metric -->
    <g transform="translate(110, 0)">
      <text x="0" y="0" class="badge-text" fill="#FF8A00">🔥 {commits} commits</text>
    </g>

    <!-- Stars -->
    <g transform="translate(240, 0)">
      <path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.75.75 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z" fill="#E3B341" transform="scale(0.85) translate(0, -12)"/>
      <text x="16" y="0" class="stat-text">{stars}</text>
    </g>

    <!-- Forks -->
    <g transform="translate(305, 0)">
      <path d="M5 3.25a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0Zm0 2.122a2.25 2.25 0 1 0-1.5 0v.878A2.25 2.25 0 0 0 5.75 8.5h1.5v2.128a2.251 2.251 0 1 0 1.5 0V8.5A2.25 2.25 0 0 0 6.5 6.25h-1.5v-.878ZM8 12.75a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0Z" fill="#8B949E" transform="scale(0.85) translate(0, -12)"/>
      <text x="16" y="0" class="stat-text">{forks}</text>
    </g>
  </g>
</svg>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)


def generate_popular_repos_markdown(selected_repos: list) -> str:
    if not selected_repos:
        return "<p align=\"center\"><em>No public repositories found.</em></p>"

    lines = ["  <p align=\"center\">"]
    for i, repo in enumerate(selected_repos):
        name = repo.get("name", "")
        url = repo.get("html_url", f"https://github.com/{USERNAME}/{name}")
        svg_rel_path = f"assets/cards/{name}.svg"
        
        lines.append(f"    <a href=\"{url}\">")
        lines.append(f"      <img src=\"{svg_rel_path}\" width=\"48%\" alt=\"{name} Repository Card\" />")
        lines.append("    </a>")
        
        # Add line break every 2 cards
        if (i + 1) % 2 == 0 and (i + 1) < len(selected_repos):
            lines.append("    <br/>")
            
    lines.append("  </p>")
    return "\n".join(lines)


def update_popular_repositories():
    print(f"Fetching public repositories for {USERNAME}...")
    repos = fetch_public_repositories()
    if not repos:
        print("No public repositories retrieved.")
        return False

    print(f"Discovered {len(repos)} public repositories. Fetching commit metrics...")
    for repo in repos:
        name = repo.get("name", "")
        commits = fetch_commit_count(name)
        repo["total_commits"] = commits
        print(f"  → {name}: {commits} commits")

    # Sort by total commits DESC, then pushed_at DESC
    repos.sort(key=lambda r: (r.get("total_commits", 0), r.get("pushed_at", "")), reverse=True)

    # Select top 4 public repositories
    selected = repos[:4]
    print(f"Selected top {len(selected)} repositories: {[r['name'] for r in selected]}")

    # Ensure assets/cards directory exists
    os.makedirs(CARDS_DIR, exist_ok=True)

    # Generate SVGs
    for repo in selected:
        out_file = os.path.join(CARDS_DIR, f"{repo['name']}.svg")
        generate_svg_card(repo, out_file)
        print(f"Generated SVG: {out_file}")

    # Generate markdown injection
    markdown_cards = generate_popular_repos_markdown(selected)

    # Update README
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        f"{re.escape(START_MARKER)}[\\s\\S]*?{re.escape(END_MARKER)}",
        re.MULTILINE
    )

    if not pattern.search(content):
        print(f"Markers {START_MARKER} and {END_MARKER} not found in {README_PATH}", file=sys.stderr)
        return False

    replacement = f"{START_MARKER}\n{markdown_cards}\n{END_MARKER}"
    new_content = pattern.sub(replacement, content)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

    print("Successfully updated README.md with popular project cards.")
    return True


if __name__ == "__main__":
    if not update_popular_repositories():
        sys.exit(1)
