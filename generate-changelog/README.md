# Generate Changelog

A Claude Code skill and bash script that generates a structured `CHANGELOG.md` from git history.

## Setup (3 steps)

1. Copy this folder into your Claude Code skills directory:
   ```bash
   cp -r generate-changelog ~/.claude/skills/
   ```

2. Make the script executable:
   ```bash
   chmod +x ~/.claude/skills/generate-changelog/scripts/generate-changelog.sh
   ```

3. Run it in any git repository:
   ```bash
   bash ~/.claude/skills/generate-changelog/scripts/generate-changelog.sh
   ```

## Usage

### Generate `CHANGELOG.md`

```bash
bash scripts/generate-changelog.sh
```

### Preview without writing

```bash
bash scripts/generate-changelog.sh --dry-run
```

### Write to a custom file

```bash
bash scripts/generate-changelog.sh --output HISTORY.md
```

## What It Does

1. Finds the latest git tag with `git describe --tags --abbrev=0`
2. Fetches commits since that tag (`latest-tag..HEAD`)
3. If no tags exist, uses the full git history
4. Excludes merge commits for a cleaner changelog
5. Auto-categorizes commits into:
   - **Added** — `feat`, `add`, `new`, `implement`, `introduce`
   - **Fixed** — `fix`, `bug`, `patch`, `resolve`, `hotfix`
   - **Changed** — `change`, `update`, `refactor`, `improve`, `enhance`
   - **Removed** — `remove`, `delete`, `deprecate`, `drop`
6. Writes a Keep a Changelog-style `CHANGELOG.md`

## Example Output

See [`CHANGELOG-sample.md`](CHANGELOG-sample.md) for sample output generated from a real GitHub repository.

## Requirements

- Git
- Bash
- Standard Unix tools: `date`, `grep`, `tr`, `mktemp`

## Notes

- If no git tags exist, the script uses all commits from project start.
- If a commit does not match a category keyword, it defaults to **Changed**.
- The script is safe to run repeatedly; it overwrites the configured output file.
