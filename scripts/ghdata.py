"""Public GitHub data for the profile. Works with or without GITHUB_TOKEN."""
import datetime as dt
import json
import os
import re
import urllib.error
import urllib.request

USER = os.environ.get("PROFILE_USER", "glebstarchikov")
API = "https://api.github.com"
LEVELS = {
    "NONE": 0,
    "FIRST_QUARTILE": 1,
    "SECOND_QUARTILE": 2,
    "THIRD_QUARTILE": 3,
    "FOURTH_QUARTILE": 4,
}


def _req(url, data=None, accept="application/vnd.github+json"):
    headers = {"Accept": accept, "User-Agent": f"{USER}-profile"}
    token = os.environ.get("GITHUB_TOKEN")
    if token and url.startswith(API):
        headers["Authorization"] = f"Bearer {token}"
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, body, headers), timeout=30) as r:
            return r.read().decode()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:300]
        raise RuntimeError(f"HTTP {exc.code} for {url}: {detail}") from exc


def get(path):
    return json.loads(_req(API + path))


def public_repos():
    repos = get(f"/users/{USER}/repos?type=owner&sort=pushed&per_page=100")
    return [r for r in repos if not r["fork"] and not r["archived"] and r["name"] != USER]


def recent_commits(limit=6, per_repo=8):
    out = []
    for repo in public_repos()[:8]:
        try:
            commits = get(f"/repos/{repo['full_name']}/commits?per_page={per_repo}")
        except Exception:
            continue
        for c in commits:
            msg = c["commit"]["message"].splitlines()[0].strip()
            if msg.lower().startswith("merge ") or "[skip ci]" in msg:
                continue
            out.append({
                "repo": repo["name"],
                "message": msg,
                "url": c["html_url"],
                "date": c["commit"]["committer"]["date"],
            })
    out.sort(key=lambda c: c["date"], reverse=True)
    return out[:limit]


def _finish(days, total, source):
    if not days:
        raise RuntimeError(f"{source} returned no contribution days")
    got = sum(n for _, n, _ in days)
    if got != total:
        raise RuntimeError(f"{source} day counts sum to {got}, not the reported total {total}")
    dates = [d for d, _, _ in days]
    if dates != sorted(dates) or len(set(dates)) != len(dates):
        raise RuntimeError(f"{source} dates are not a unique ordered calendar")
    if any(level not in range(5) or n < 0 for _, n, level in days):
        raise RuntimeError(f"{source} returned a contribution count or level that cannot be drawn")
    print(f"contributions {total} ({dates[0]} to {dates[-1]}) via {source}")
    return days


def _from_graphql():
    query = """query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{
             totalContributions weeks{contributionDays{date contributionCount contributionLevel}}}}}}"""
    res = json.loads(_req(API + "/graphql", {"query": query, "variables": {"u": USER}}))
    if res.get("errors"):
        message = res["errors"][0].get("message", "graphql error")
        raise RuntimeError(message)
    calendar = res["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = []
    for week in calendar["weeks"]:
        for day in week["contributionDays"]:
            days.append((
                day["date"],
                int(day["contributionCount"]),
                LEVELS[day["contributionLevel"]],
            ))
    return _finish(days, int(calendar["totalContributions"]), "github graphql")


def _count_from_tooltip(text):
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", text)).strip()
    matched = re.match(r"^(\d+) contributions?\b", text, re.I)
    if matched:
        return int(matched.group(1))
    if re.match(r"^no contributions?\b", text, re.I):
        return 0
    raise RuntimeError(f"unrecognized contribution tooltip: {text!r}")


def _from_profile():
    """Public profile calendar, used only when the API is unavailable."""
    html = _req(f"https://github.com/users/{USER}/contributions", accept="text/html")
    heading = re.search(
        r'id="js-contribution-activity-description"[^>]*>\s*([\d,]+)\s+contributions',
        html,
    )
    if not heading:
        raise RuntimeError("profile page has no contributions total")
    total = int(heading.group(1).replace(",", ""))
    tips = {}
    for match in re.finditer(r"<tool-tip\b([^>]*)>(.*?)</tool-tip>", html, re.S | re.I):
        attrs, body = match.group(1), match.group(2)
        target = re.search(r'\bfor="(contribution-day-component-[\d-]+)"', attrs)
        if target:
            tips[target.group(1)] = _count_from_tooltip(body)
    days = []
    for match in re.finditer(r"<td\b([^>]*)>", html, re.I):
        attrs = match.group(1)
        date = re.search(r'\bdata-date="([\d-]+)"', attrs)
        level = re.search(r'\bdata-level="(\d)"', attrs)
        cid = re.search(r'\bid="(contribution-day-component-[\d-]+)"', attrs)
        if not (date and level and cid):
            continue
        key = cid.group(1)
        if key not in tips:
            raise RuntimeError(f"no tooltip for {date.group(1)}")
        days.append((date.group(1), tips[key], int(level.group(1))))
    days.sort()
    return _finish(days, total, "github profile")


def contributions():
    """Daily contribution counts for the last year as [(date, count, level)].

    A token reads the GraphQL contribution calendar, and the drawn total has to
    match totalContributions. With no token, the public profile calendar is used.
    """
    if os.environ.get("GITHUB_TOKEN"):
        return _from_graphql()
    return _from_profile()


def today():
    return dt.datetime.now(dt.timezone.utc).astimezone().date()
