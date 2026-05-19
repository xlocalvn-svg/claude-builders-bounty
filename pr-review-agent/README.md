# Claude PR Review Agent

A lightweight Claude Code-compatible PR review agent that fetches a GitHub pull request diff and produces a structured Markdown review comment.

## Setup

1. Install dependencies:
   ```bash
   cd pr-review-agent
   python3 -m venv .venv
   . .venv/bin/activate
   pip install -e .
   ```

2. Set API keys:
   ```bash
   export ANTHROPIC_API_KEY="your-anthropic-key"
   export GITHUB_TOKEN="your-github-token" # optional but recommended
   ```

3. Review a PR:
   ```bash
   claude-review --pr https://github.com/owner/repo/pull/123
   ```

## Usage

```bash
claude-review --pr https://github.com/owner/repo/pull/123
```

The command prints a structured Markdown comment containing:

- Summary of changes
- Identified risks
- Improvement suggestions
- Confidence score

To save output:

```bash
claude-review --pr https://github.com/owner/repo/pull/123 --output review.md
```

## GitHub Action

A workflow is included at `.github/workflows/claude-pr-review.yml`. Add these repository secrets:

- `ANTHROPIC_API_KEY`
- `GITHUB_TOKEN` is provided automatically by GitHub Actions

The workflow runs on pull requests and posts the structured review as a PR comment.

## Notes

- Large diffs are truncated by default to keep prompts within context limits.
- The CLI supports public PRs without `GITHUB_TOKEN`, but rate limits are lower.
- For private repositories, `GITHUB_TOKEN` is required.
