## Summary
This PR replaces a lexicographic `python-multipart` version comparison with a numeric tuple comparison in `ensure_multipart_is_installed()`. The change fixes false rejections for future versions like `0.0.100` that compare incorrectly as strings.

## Identified Risks
- The new parsing can raise `ValueError` for valid non-plain-semver version strings such as `0.0.13.post1`, `0.0.13rc1`, `0.0.13.dev0`, or distro-local versions, and that exception is not caught by the existing `except (ImportError, AssertionError)` block.
- The PR description claims pre-release suffixes are handled by `[:3]`, but suffixes attached to the patch component, e.g. `0.0.13rc1`, are still included in the third split element and will fail `int(...)`.
- No regression test is included for the reported case (`0.0.100`) or for version strings with suffixes, so the behavior could regress or introduce install-time failures for common Python package version formats.
- The comparison still uses `assert`, which can be skipped when Python runs with optimization (`-O`), preserving an existing fragility in this check.

## Improvement Suggestions
- Use a robust version parser such as `packaging.version.Version` if available in the project dependencies, or a small helper that safely handles PEP 440 suffixes.
- Add tests for `0.0.100`, `0.1.0`, and suffix variants like `0.0.13.post1` / `0.0.13rc1`.
- Catch `ValueError` if keeping the tuple parser, and ensure malformed versions produce the intended multipart installation error rather than an uncaught exception.
- Consider replacing the `assert` version check with an explicit conditional raise to avoid behavior changes under optimized Python execution.

## Confidence Score
High, because the diff is small and the version-parsing edge cases are directly inferable from the changed line.
