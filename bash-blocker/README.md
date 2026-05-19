# Destructive Bash Command Blocker

A Claude Code pre-tool-use hook that intercepts and blocks dangerous bash commands before execution.

## What It Blocks

- `rm -rf` / `rm -fr` recursive force deletion
- `DROP TABLE` SQL statements
- `git push --force`
- `TRUNCATE` SQL statements
- `DELETE FROM` without a `WHERE` clause

## Installation

```bash
mkdir -p ~/.claude/hooks && cp pre-tool-use ~/.claude/hooks/pre-tool-use && chmod +x ~/.claude/hooks/pre-tool-use
```

That's it. Claude Code will run the hook before tool use.

## How It Works

The hook intercepts bash/shell/exec/terminal tool calls before Claude Code executes them. If a dangerous pattern is detected:

1. **Blocks execution** immediately with a non-zero exit code
2. **Logs the attempt** to `~/.claude/hooks/blocked.log` with:
   - Timestamp
   - Project path
   - Blocked reason
   - Full attempted command
3. **Notifies Claude** with a clear JSON message explaining why the command was blocked

## Example Block Message

```json
{
  "error": "Command blocked: rm -rf recursive force delete",
  "message": "Claude Code safety hook blocked this Bash command because it matched: rm -rf recursive force delete.\n\nAttempted command:\nrm -rf /tmp/data\n\nThis can destroy files, rewrite remote history, or damage database data. If this action is truly intended, review it manually and run it outside Claude Code.\n\nBlocked attempt logged to: ~/.claude/hooks/blocked.log"
}
```

## Log Format

```text
2026-05-19T12:05:00.000000 | /home/user/project | rm -rf recursive force delete | rm -rf /tmp/data
2026-05-19T12:06:15.123456 | /home/user/project | DROP TABLE SQL statement | DROP TABLE users;
```

## Testing

Run the included test suite:

```bash
python3 test_hook.py
```

Expected result:

```text
Results: 23 passed, 0 failed
✅ All tests passed!
```

## Supported Hook Payloads

The hook supports common Claude Code hook payload shapes:

```json
{
  "tool": {
    "name": "bash",
    "input": { "command": "rm -rf /tmp/data" }
  },
  "project_path": "/home/user/project"
}
```

It also supports `tool_name`, `tool_input`, `toolName`, `toolInput`, top-level `command` / `script`, and `cwd` variants for compatibility.

## Safe Commands Are Allowed

These commands are **not blocked**:

```bash
rm file.txt
rm -f file.txt
rm -r directory
git push origin main
git push --force-with-lease origin main
DELETE FROM users WHERE id = 1
echo 'DROP TABLE' > note.txt
```

## Disabling

To temporarily disable:

```bash
mv ~/.claude/hooks/pre-tool-use ~/.claude/hooks/pre-tool-use.disabled
```

To re-enable:

```bash
mv ~/.claude/hooks/pre-tool-use.disabled ~/.claude/hooks/pre-tool-use
```

## Requirements

- Python 3.6+
- Claude Code with hooks support

## Notes

- Only bash-like tool calls are inspected
- Non-bash tools are not affected
- Hook errors fail open so malformed payloads do not break normal Claude Code usage
- SQL checks ignore quoted strings to avoid false positives like `echo 'DROP TABLE' > note.txt`
