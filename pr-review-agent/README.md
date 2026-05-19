# Claude PR Review Agent

A lightweight PR review agent that fetches a GitHub pull request diff and produces a structured Markdown review comment.

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
   export OPENAI_API_KEY="your-openai-compatible-api-key"
   export GITHUB_TOKEN="your-github-token" # optional for public PRs
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

- Summary of changes (2-3 sentences)
- Identified risks (concrete issues, bugs, edge cases)
- Improvement suggestions (actionable recommendations)
- Confidence score (Low/Medium/High with reasoning)

To save output:

```bash
claude-review --pr https://github.com/owner/repo/pull/123 --output review.md
```

## GitHub Action

A workflow is included at `.github/workflows/claude-pr-review.yml`. Add these repository secrets:

- `OPENAI_API_KEY` (or `ANTHROPIC_API_KEY` if using Anthropic directly)
- `GITHUB_TOKEN` is provided automatically by GitHub Actions

The workflow runs on pull requests and posts the structured review as a PR comment.

## Configuration

- `--model`: Model name (default: `Nova`, works with OpenAI-compatible APIs)
- `--api-base`: API base URL (default: `http://192.168.1.105:20128/v1`)
- `--output`: Save review to file

## Notes

- Large diffs are truncated to 60,000 characters to keep prompts within context limits.
- The CLI supports public PRs without `GITHUB_TOKEN`, but rate limits are lower.
- For private repositories, `GITHUB_TOKEN` is required.
- Works with any OpenAI-compatible API (9router, OpenRouter, etc.)

## Sample Output

See `samples/review-1.md` and `samples/review-2.md` for real PR review examples.
