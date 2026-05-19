import argparse
import os
import re
import sys
from dataclasses import dataclass
from typing import Optional

import requests


MAX_DIFF_CHARS = 60000
DEFAULT_MODEL = "claude-3-5-sonnet-20241022"


@dataclass
class PullRequest:
    owner: str
    repo: str
    number: int
    title: str
    body: str
    author: str
    base: str
    head: str
    html_url: str
    diff: str


def parse_pr_url(url: str) -> tuple[str, str, int]:
    match = re.match(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", url.rstrip("/"))
    if not match:
        raise ValueError("PR URL must look like https://github.com/owner/repo/pull/123")
    owner, repo, number = match.groups()
    return owner, repo, int(number)


def github_headers() -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "claude-pr-review-agent",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def fetch_pr(pr_url: str) -> PullRequest:
    owner, repo, number = parse_pr_url(pr_url)
    api = f"https://api.github.com/repos/{owner}/{repo}/pulls/{number}"
    response = requests.get(api, headers=github_headers(), timeout=30)
    response.raise_for_status()
    data = response.json()

    diff_headers = github_headers()
    diff_headers["Accept"] = "application/vnd.github.v3.diff"
    diff_response = requests.get(api, headers=diff_headers, timeout=30)
    diff_response.raise_for_status()
    diff = diff_response.text

    if len(diff) > MAX_DIFF_CHARS:
        diff = diff[:MAX_DIFF_CHARS] + "\n\n[Diff truncated for length.]"

    return PullRequest(
        owner=owner,
        repo=repo,
        number=number,
        title=data.get("title", ""),
        body=data.get("body") or "",
        author=data.get("user", {}).get("login", "unknown"),
        base=data.get("base", {}).get("ref", ""),
        head=data.get("head", {}).get("ref", ""),
        html_url=data.get("html_url", pr_url),
        diff=diff,
    )


def build_prompt(pr: PullRequest) -> str:
    return f"""You are a senior software engineer reviewing a GitHub pull request.

Return ONLY a structured Markdown PR review comment with these exact sections:

## Summary
2-3 concise sentences summarizing what changed.

## Identified Risks
- List concrete risks, bugs, regressions, missing tests, security issues, or edge cases.
- If none are obvious, say "- No major risks identified from the diff."

## Improvement Suggestions
- List actionable suggestions.
- If none are needed, say "- No blocking improvements suggested."

## Confidence Score
Low / Medium / High, followed by one short reason.

Review this PR:

Repository: {pr.owner}/{pr.repo}
PR: #{pr.number} - {pr.title}
Author: {pr.author}
Base: {pr.base}
Head: {pr.head}
URL: {pr.html_url}

PR description:
{pr.body}

Diff:
```diff
{pr.diff}
```
"""


def review_pr(pr: PullRequest, model: str, api_base: str, api_key: str) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": build_prompt(pr)}],
        "max_tokens": 1800,
        "temperature": 0.2,
    }
    response = requests.post(f"{api_base}/chat/completions", headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Review a GitHub PR with Claude and output structured Markdown.")
    parser.add_argument("--pr", required=True, help="GitHub PR URL, e.g. https://github.com/owner/repo/pull/123")
    parser.add_argument("--model", default=os.getenv("CLAUDE_REVIEW_MODEL", DEFAULT_MODEL))
    parser.add_argument("--api-base", default=os.getenv("OPENAI_API_BASE", "http://192.168.1.105:20128/v1"))
    parser.add_argument("--output", help="Write review Markdown to this file")
    args = parser.parse_args(argv)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY is required (9router API key)", file=sys.stderr)
        return 1

    try:
        pr = fetch_pr(args.pr)
        review = review_pr(pr, args.model, args.api_base, api_key)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(review + "\n")
        print(review)
        return 0
    except Exception as exc:
        print(f"claude-review error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
