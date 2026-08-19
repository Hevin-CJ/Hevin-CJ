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
ASSETS_DIR = os.path.join(REPO_ROOT, "assets")
CARDS_DIR = os.path.join(ASSETS_DIR, "cards")
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
      <stop offset="0%" stop-color="#635BFF">
        <animate attributeName="stop-color" values="#635BFF;#00F5D4;#FF007A;#635BFF" dur="8s" repeatCount="indefinite" />
      </stop>
      <stop offset="100%" stop-color="#00F5D4">
        <animate attributeName="stop-color" values="#00F5D4;#FF007A;#635BFF;#00F5D4" dur="8s" repeatCount="indefinite" />
      </stop>
    </linearGradient>
  </defs>

  <!-- Background Card -->
  <rect x="1" y="1" width="408" height="133" class="card-bg" />

  <!-- Repo Icon & Title -->
  <g transform="translate(18, 26)">
    <path d="M4 1.75C4 .784 4.784 0 5.75 0h8.5C15.216 0 16 .784 16 1.75v12.5A1.75 1.75 0 0 1 14.25 16h-8.5A1.75 1.75 0 0 1 4 14.25V1.75ZM5.75 1.5a.25.25 0 0 0-.25.25v12.5c0 .138.112.25.25.25h8.5a.25.25 0 0 0 .25-.25V1.75a.25.25 0 0 0-.25-.25h-8.5Z" fill="#58A6FF" />
    <path d="M2 3.5a.75.75 0 0 1 .75-.75h.5a.75.75 0 0 1 0 1.5h-.5A.75.75 0 0 1 2 3.5Zm0 3a.75.75 0 0 1 .75-.75h.5a.75.75 0 0 1 0 1.5h-.5A.75.75 0 0 1 2 6.5Zm0 3a.75.75 0 0 1 .75-.75h.5a.75.75 0 0 1 0 1.5h-.5A.75.75 0 0 1 2 9.5Z" fill="#58A6FF" />
    <text x="24" y="13" class="title">{name}</text>
  </g>

  <!-- Description -->
  <text x="18" y="66" class="desc">{desc}</text>

  <!-- Language Chip, Commits, Stars, Forks -->
  <g transform="translate(18, 105)">
    <circle cx="5" cy="-4" r="5" fill="{lang_color}" />
    <text x="15" y="0" class="badge-text">{html.escape(lang)}</text>

    <g transform="translate(110, 0)">
      <text x="0" y="0" class="badge-text" fill="#FF8A00">🔥 {commits} commits</text>
    </g>

    <g transform="translate(240, 0)">
      <path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.75.75 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z" fill="#E3B341" transform="scale(0.85) translate(0, -12)"/>
      <text x="16" y="0" class="stat-text">{stars}</text>
    </g>

    <g transform="translate(305, 0)">
      <path d="M5 3.25a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0Zm0 2.122a2.25 2.25 0 1 0-1.5 0v.878A2.25 2.25 0 0 0 5.75 8.5h1.5v2.128a2.251 2.251 0 1 0 1.5 0V8.5A2.25 2.25 0 0 0 6.5 6.25h-1.5v-.878ZM8 12.75a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0Z" fill="#8B949E" transform="scale(0.85) translate(0, -12)"/>
      <text x="16" y="0" class="stat-text">{forks}</text>
    </g>
  </g>
</svg>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)


def generate_activity_svg(total_commits: int, total_repos: int, output_path: str):
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="830" height="150" viewBox="0 0 830 150" fill="none">
  <style>
    .card-bg {{
      fill: #0D1117;
      stroke: url(#act-border-grad);
      stroke-width: 1.5;
      rx: 14;
    }}
    .act-title {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
      font-size: 16px;
      font-weight: 700;
      fill: #FFFFFF;
      letter-spacing: 0.5px;
    }}
    .metric-value {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
      font-size: 26px;
      font-weight: 800;
      fill: #00F5D4;
    }}
    .metric-label {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
      font-size: 12px;
      font-weight: 600;
      fill: #8B949E;
      text-transform: uppercase;
      letter-spacing: 1px;
    }}
    .shimmer-track {{
      fill: rgba(99, 91, 255, 0.15);
      rx: 4;
    }}
    .shimmer-bar {{
      fill: url(#shimmer-grad);
      rx: 4;
      animation: shimmerFlow 3s ease-in-out infinite alternate;
    }}
    @keyframes shimmerFlow {{
      0% {{ width: 240px; transform: translateX(0px); }}
      100% {{ width: 380px; transform: translateX(410px); }}
    }}
    @media (prefers-color-scheme: light) {{
      .card-bg {{
        fill: #FFFFFF;
        stroke: #D0D7DE;
      }}
      .act-title {{
        fill: #24292F;
      }}
      .metric-value {{
        fill: #0969DA;
      }}
      .metric-label {{
        fill: #57606A;
      }}
      .shimmer-track {{
        fill: rgba(9, 105, 218, 0.1);
      }}
    }}
  </style>

  <defs>
    <linearGradient id="act-border-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#635BFF">
        <animate attributeName="stop-color" values="#635BFF;#00F5D4;#FF007A;#635BFF" dur="6s" repeatCount="indefinite" />
      </stop>
      <stop offset="50%" stop-color="#FF007A">
        <animate attributeName="stop-color" values="#FF007A;#635BFF;#00F5D4;#FF007A" dur="6s" repeatCount="indefinite" />
      </stop>
      <stop offset="100%" stop-color="#00F5D4">
        <animate attributeName="stop-color" values="#00F5D4;#FF007A;#635BFF;#00F5D4" dur="6s" repeatCount="indefinite" />
      </stop>
    </linearGradient>

    <linearGradient id="shimmer-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#635BFF" />
      <stop offset="50%" stop-color="#00F5D4" />
      <stop offset="100%" stop-color="#FF007A" />
    </linearGradient>
  </defs>

  <!-- Background Card -->
  <rect x="1" y="1" width="828" height="148" class="card-bg" />

  <!-- Title & Icon -->
  <g transform="translate(24, 28)">
    <circle cx="8" cy="8" r="7" fill="#00F5D4" opacity="0.85">
      <animate attributeName="r" values="6;8;6" dur="2s" repeatCount="indefinite"/>
    </circle>
    <text x="24" y="13" class="act-title">⚡ REAL-TIME CONTRIBUTION &amp; ENGINEERING METRICS</text>
  </g>

  <!-- 3 Big Metric Columns -->
  <g transform="translate(45, 80)">
    <!-- Total Commits -->
    <g transform="translate(0, 0)">
      <text x="0" y="0" class="metric-value">🔥 {total_commits}+</text>
      <text x="0" y="20" class="metric-label">Total Verified Commits</text>
    </g>

    <!-- Active Projects -->
    <g transform="translate(280, 0)">
      <text x="0" y="0" class="metric-value">🚀 {total_repos} Public Apps</text>
      <text x="0" y="20" class="metric-label">Open Source Codebases</text>
    </g>

    <!-- Streak Level -->
    <g transform="translate(560, 0)">
      <text x="0" y="0" class="metric-value">⭐ Active Daily</text>
      <text x="0" y="20" class="metric-label">Continuous Builder</text>
    </g>
  </g>

  <!-- Animated Bottom Shimmer Bar -->
  <g transform="translate(24, 128)">
    <rect x="0" y="0" width="782" height="6" class="shimmer-track" />
    <rect x="0" y="0" width="300" height="6" class="shimmer-bar" />
  </g>
</svg>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)


def generate_stats_svg(total_stars: int, total_forks: int, total_repos: int, total_commits: int, output_path: str):
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="410" height="175" viewBox="0 0 410 175" fill="none">
  <style>
    .card-bg {{
      fill: #0D1117;
      stroke: url(#stats-border);
      stroke-width: 1.5;
      rx: 12;
    }}
    .stats-title {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
      font-size: 15px;
      font-weight: 700;
      fill: #58A6FF;
    }}
    .stat-row-label {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
      font-size: 13px;
      font-weight: 500;
      fill: #C9D1D9;
    }}
    .stat-row-val {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
      font-size: 13px;
      font-weight: 700;
      fill: #00F5D4;
    }}
    @media (prefers-color-scheme: light) {{
      .card-bg {{
        fill: #FFFFFF;
        stroke: #D0D7DE;
      }}
      .stats-title {{
        fill: #0969DA;
      }}
      .stat-row-label {{
        fill: #24292F;
      }}
      .stat-row-val {{
        fill: #0969DA;
      }}
    }}
  </style>

  <defs>
    <linearGradient id="stats-border" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#635BFF">
        <animate attributeName="stop-color" values="#635BFF;#00F5D4;#635BFF" dur="5s" repeatCount="indefinite" />
      </stop>
      <stop offset="100%" stop-color="#00F5D4">
        <animate attributeName="stop-color" values="#00F5D4;#635BFF;#00F5D4" dur="5s" repeatCount="indefinite" />
      </stop>
    </linearGradient>
  </defs>

  <rect x="1" y="1" width="408" height="173" class="card-bg" />

  <!-- Header -->
  <g transform="translate(20, 24)">
    <text x="0" y="12" class="stats-title">📊 GitHub Overview Stats</text>
  </g>

  <!-- Metrics Table -->
  <g transform="translate(20, 60)">
    <!-- Commits -->
    <g transform="translate(0, 0)">
      <text x="0" y="0" class="stat-row-label">🔥 Total Commits</text>
      <text x="370" y="0" text-anchor="end" class="stat-row-val">{total_commits}+</text>
    </g>

    <!-- Public Repos -->
    <g transform="translate(0, 26)">
      <text x="0" y="0" class="stat-row-label">📦 Public Repositories</text>
      <text x="370" y="0" text-anchor="end" class="stat-row-val">{total_repos}</text>
    </g>

    <!-- Total Stars -->
    <g transform="translate(0, 52)">
      <text x="0" y="0" class="stat-row-label">⭐ Total Stars Earned</text>
      <text x="370" y="0" text-anchor="end" class="stat-row-val">{total_stars}</text>
    </g>

    <!-- Forks -->
    <g transform="translate(0, 78)">
      <text x="0" y="0" class="stat-row-label">🍴 Total Forks</text>
      <text x="370" y="0" text-anchor="end" class="stat-row-val">{total_forks}</text>
    </g>
  </g>
</svg>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)


def generate_languages_svg(repos: list, output_path: str):
    # Count languages
    lang_counts = {}
    for r in repos:
        lang = r.get("language")
        if lang:
            lang_counts[lang] = lang_counts.get(lang, 0) + 1

    total = sum(lang_counts.values()) or 1
    sorted_langs = sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)[:4]

    # Calculate segments
    segments = []
    current_x = 0
    bar_width = 370
    legend_items = []

    for i, (lang, count) in enumerate(sorted_langs):
        pct = (count / total) * 100
        w = (count / total) * bar_width
        color = LANGUAGE_COLORS.get(lang, "#635BFF")
        segments.append(f'<rect x="{current_x}" y="0" width="{w:.1f}" height="10" fill="{color}" />')
        current_x += w
        legend_items.append((lang, f"{pct:.1f}%", color))

    segments_svg = "\n    ".join(segments)

    # Render legends in 2x2 grid
    legend_svg = []
    for idx, (lang, pct_str, color) in enumerate(legend_items):
        gx = 0 if (idx % 2 == 0) else 190
        gy = 0 if (idx < 2) else 26
        legend_svg.append(f"""<g transform="translate({gx}, {gy})">
        <circle cx="5" cy="5" r="5" fill="{color}" />
        <text x="16" y="9" class="lang-name">{html.escape(lang)}</text>
        <text x="140" y="9" text-anchor="end" class="lang-pct">{pct_str}</text>
      </g>""")

    legends_rendered = "\n      ".join(legend_svg)

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="410" height="175" viewBox="0 0 410 175" fill="none">
  <style>
    .card-bg {{
      fill: #0D1117;
      stroke: url(#lang-border);
      stroke-width: 1.5;
      rx: 12;
    }}
    .langs-title {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
      font-size: 15px;
      font-weight: 700;
      fill: #58A6FF;
    }}
    .lang-name {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
      font-size: 12px;
      font-weight: 600;
      fill: #C9D1D9;
    }}
    .lang-pct {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
      font-size: 12px;
      font-weight: 700;
      fill: #8B949E;
    }}
    .bar-track {{
      rx: 5;
    }}
    @media (prefers-color-scheme: light) {{
      .card-bg {{
        fill: #FFFFFF;
        stroke: #D0D7DE;
      }}
      .langs-title {{
        fill: #0969DA;
      }}
      .lang-name {{
        fill: #24292F;
      }}
      .lang-pct {{
        fill: #57606A;
      }}
    }}
  </style>

  <defs>
    <linearGradient id="lang-border" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00F5D4">
        <animate attributeName="stop-color" values="#00F5D4;#FF007A;#00F5D4" dur="5s" repeatCount="indefinite" />
      </stop>
      <stop offset="100%" stop-color="#635BFF">
        <animate attributeName="stop-color" values="#635BFF;#00F5D4;#635BFF" dur="5s" repeatCount="indefinite" />
      </stop>
    </linearGradient>

    <clipPath id="bar-clip">
      <rect x="0" y="0" width="370" height="10" rx="5" />
    </clipPath>
  </defs>

  <rect x="1" y="1" width="408" height="173" class="card-bg" />

  <!-- Header -->
  <g transform="translate(20, 24)">
    <text x="0" y="12" class="langs-title">🚀 Top Languages</text>
  </g>

  <!-- Progress Bar -->
  <g transform="translate(20, 56)" clip-path="url(#bar-clip)">
    {segments_svg}
  </g>

  <!-- Legends -->
  <g transform="translate(20, 88)">
    {legends_rendered}
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
        
        if (i + 1) % 2 == 0 and (i + 1) < len(selected_repos):
            lines.append("    <br/>")
            
    lines.append("  </p>")
    return "\n".join(lines)


def update_all_metrics():
    print(f"Fetching public repositories for {USERNAME}...")
    repos = fetch_public_repositories()
    if not repos:
        print("No public repositories retrieved.")
        return False

    print(f"Discovered {len(repos)} public repositories. Fetching commit metrics...")
    total_commits = 0
    total_stars = 0
    total_forks = 0

    for repo in repos:
        name = repo.get("name", "")
        commits = fetch_commit_count(name)
        repo["total_commits"] = commits
        total_commits += commits
        total_stars += repo.get("stargazers_count", 0)
        total_forks += repo.get("forks_count", 0)
        print(f"  → {name}: {commits} commits")

    # Sort by total commits DESC, then pushed_at DESC
    repos.sort(key=lambda r: (r.get("total_commits", 0), r.get("pushed_at", "")), reverse=True)

    # Select top 4 public repositories
    selected = repos[:4]
    print(f"Selected top {len(selected)} repositories: {[r['name'] for r in selected]}")

    # Ensure directories exist
    os.makedirs(CARDS_DIR, exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)

    # 1. Generate Popular Repo SVG Cards
    for repo in selected:
        out_file = os.path.join(CARDS_DIR, f"{repo['name']}.svg")
        generate_svg_card(repo, out_file)
        print(f"Generated Repo SVG: {out_file}")

    # 2. Generate Activity SVG
    activity_file = os.path.join(ASSETS_DIR, "activity.svg")
    generate_activity_svg(total_commits, len(repos), activity_file)
    print(f"Generated Activity SVG: {activity_file}")

    # 3. Generate Overview Stats SVG
    stats_file = os.path.join(ASSETS_DIR, "stats.svg")
    generate_stats_svg(total_stars, total_forks, len(repos), total_commits, stats_file)
    print(f"Generated Stats SVG: {stats_file}")

    # 4. Generate Top Languages SVG
    langs_file = os.path.join(ASSETS_DIR, "top-langs.svg")
    generate_languages_svg(repos, langs_file)
    print(f"Generated Languages SVG: {langs_file}")

    # 5. Inject Popular Repos Markdown
    markdown_cards = generate_popular_repos_markdown(selected)

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

    print("Successfully updated README.md and all animated SVG assets.")
    return True


if __name__ == "__main__":
    if not update_all_metrics():
        sys.exit(1)
