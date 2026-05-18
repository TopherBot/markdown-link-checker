#!/usr/bin/env python3
"""markdown-link-checker

A small script that extracts HTTP/HTTPS links from a Markdown file (or all
Markdown files under a directory) and checks their HTTP status codes.

Usage:
    python link_checker.py <path> [--recursive]
"""

import argparse
import sys
import re
import urllib.request
import urllib.error
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Regular expression to capture markdown links: [text](url)
LINK_RE = re.compile(r"\[.*?\]\((https?://[^)\s]+)\)")

def extract_links(text: str) -> set:
    """Return a set of unique HTTP/HTTPS URLs found in *text*."""
    return set(LINK_RE.findall(text))

def check_link(url: str, timeout: int = 10) -> tuple:
    """Return (url, status_code, error_msg)."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return (url, resp.getcode(), "")
    except urllib.error.HTTPError as e:
        return (url, e.code, e.reason)
    except urllib.error.URLError as e:
        return (url, None, str(e.reason))
    except Exception as e:
        return (url, None, str(e))

def find_markdown_files(root: Path, recursive: bool) -> list:
    if recursive:
        return list(root.rglob("*.md"))
    else:
        return [p for p in root.iterdir() if p.suffix.lower() == ".md"]

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate HTTP/HTTPS links in Markdown files.")
    parser.add_argument("path", type=Path, help="File or directory to scan")
    parser.add_argument("--recursive", action="store_true", help="Search directories recursively")
    args = parser.parse_args()

    target = args.path
    if not target.exists():
        print(f"Error: {target} does not exist.", file=sys.stderr)
        return 2

    files_to_check = []
    if target.is_file() and target.suffix.lower() == ".md":
        files_to_check.append(target)
    elif target.is_dir():
        files_to_check = find_markdown_files(target, args.recursive)
    else:
        print("Error: Provide a .md file or a directory containing markdown files.", file=sys.stderr)
        return 2

    if not files_to_check:
        print("No markdown files found.")
        return 0

    all_links = set()
    for md_file in files_to_check:
        try:
            content = md_file.read_text(encoding="utf-8")
            links = extract_links(content)
            if links:
                all_links.update(links)
        except Exception as e:
            print(f"Failed to read {md_file}: {e}", file=sys.stderr)

    if not all_links:
        print("No HTTP/HTTPS links found.")
        return 0

    print(f"Found {len(all_links)} unique link(s). Checking...\n")
    broken = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(check_link, url): url for url in all_links}
        for future in as_completed(future_to_url):
            url, status, err = future.result()
            if status is None or status >= 400:
                broken.append((url, status, err))
                print(f"[BROKEN] {url} -> {status or 'ERROR'} {err}")
            else:
                print(f"[OK]     {url} -> {status}")

    if broken:
        print(f"\n{len(broken)} broken link(s) detected.")
        return 1
    else:
        print("\nAll links are reachable!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
