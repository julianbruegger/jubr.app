#!/usr/bin/env python3
"""Find live *.jubr.app subdomains and write them into index.html.

Subdomains come from certificate transparency logs (crt.sh): every subdomain
with a valid, unexpired certificate is listed. Name and description are taken
from each site's <title> and <meta name="description">, unless overrides.json
says otherwise. Standard library only.
"""
import html
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

DOMAIN = "jubr.app"
ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
OVERRIDES = ROOT / "overrides.json"
START, END = "// PROJECTS:START", "// PROJECTS:END"
UA = {"User-Agent": "Mozilla/5.0 (project-overview-bot)"}


def fetch(url, timeout=20, limit=None):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(limit)


def discover():
    url = f"https://crt.sh/?q=%25.{DOMAIN}&output=json&exclude=expired"
    for attempt in range(4):
        try:
            certs = json.loads(fetch(url, timeout=90))
            break
        except Exception as e:  # crt.sh is often slow or flaky
            print(f"crt.sh attempt {attempt + 1} failed: {e}", file=sys.stderr)
            time.sleep(10 * (attempt + 1))
    else:
        sys.exit("crt.sh unreachable, leaving index.html unchanged")

    subs = set()
    for cert in certs:
        for name in cert["name_value"].lower().split("\n"):
            name = name.strip()
            if name.endswith("." + DOMAIN) and "*" not in name:
                subs.add(name[: -len(DOMAIN) - 1])
    return subs


def page_meta(sub):
    """Return (reachable, title, description) for a subdomain."""
    for attempt in range(2):
        try:
            body = fetch(f"https://{sub}.{DOMAIN}", timeout=15, limit=300_000)
            break
        except urllib.error.HTTPError as e:
            body = e.read(300_000)
            break
        except Exception:
            time.sleep(3)
    else:
        return False, None, None
    text = body.decode("utf-8", "ignore")
    title = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
    desc = re.search(
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)', text, re.I
    )
    clean = lambda m: html.unescape(" ".join(m.group(1).split())) if m else None
    return True, clean(title), clean(desc)


def current(src):
    """Projects already listed in index.html, keyed by subdomain."""
    m = re.search(re.escape(START) + r"\s*const PROJECTS = (.*?);\s*" + re.escape(END), src, re.S)
    return {p["sub"]: p for p in json.loads(m.group(1))} if m else {}


def main():
    overrides = json.loads(OVERRIDES.read_text()) if OVERRIDES.exists() else {}
    hide = set(overrides.get("hide", []))
    custom = overrides.get("projects", {})
    src = INDEX.read_text()
    old = current(src)
    found = discover()

    # crt.sh sometimes returns incomplete results, so a project already on the
    # page is only dropped when it's missing from crt.sh AND not reachable.
    projects = []
    for sub in sorted((found | set(old)) - hide):
        reachable, title, desc = page_meta(sub)
        if sub not in found and not reachable:
            print(f"{sub}: removed")
            continue
        prev, o = old.get(sub, {}), custom.get(sub, {})
        projects.append({
            "sub": sub,
            "name": o.get("name") or title or prev.get("name") or sub,
            "desc": o.get("desc", desc or prev.get("desc", "")),
        })
        print(f"{sub}: {projects[-1]['name']}")

    block = "const PROJECTS = " + json.dumps(projects, indent=2, ensure_ascii=False) + ";"
    new = re.sub(
        re.escape(START) + r".*?" + re.escape(END),
        lambda _: f"{START}\n    {block.replace(chr(10), chr(10) + '    ')}\n    {END}",
        src,
        flags=re.S,
    )
    if new != src:
        INDEX.write_text(new)
        print("index.html updated")
    else:
        print("no changes")


if __name__ == "__main__":
    main()
