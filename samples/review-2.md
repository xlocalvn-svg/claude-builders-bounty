## Summary
This PR moves automatic `OPTIONS` handling from a per-request dispatch special case into routing by registering an internal `_automatic_options` route. It also hides that internal endpoint from `flask routes`, updates displayed methods to preserve visible `OPTIONS` behavior, and replaces the static lambda/weakref with a module-level view.

## Identified Risks
- `src/flask/sansio/app.py`: the broad `except Exception: pass` around adding the internal `OPTIONS` rule can silently hide unrelated routing/configuration errors, making real regressions difficult to diagnose until Werkzeug exposes a narrower duplicate-rule exception.
- `src/flask/cli.py`: `methods = rule.methods or set()` mutates `rule.methods` in place when `provide_automatic_options` is true, because `methods.add("OPTIONS")` operates on the original set. Running `flask routes` can therefore change application routing metadata unexpectedly.
- `src/flask/sansio/app.py`: automatic `OPTIONS` is registered with the same `**options` as the user rule. Options such as aliases, redirects, host/subdomain behavior, or future rule arguments may interact differently for the synthetic endpoint and should be covered by tests.
- `tests/test_basic.py`: coverage verifies view args for the new `_options_view`, but there does not appear to be regression coverage for mixed-method duplicate URL registrations such as separate `@app.get` and `@app.post` handlers sharing the same rule.
- `tests/test_cli.py`: CLI coverage checks hiding `HEAD` / `OPTIONS`, but does not assert that invoking `flask routes` is side-effect free with respect to `rule.methods`.

## Improvement Suggestions
- Replace `methods = rule.methods or set()` with a copy before adding `OPTIONS`, for example `methods = set(rule.methods or ())`, to avoid mutating the URL map during CLI display.
- Narrow the `except Exception` as soon as Werkzeug exposes the duplicate-rule exception; until then, consider at least documenting why the broad catch is intentionally temporary.
- Add tests for separate view functions on the same URL with different methods to confirm only one effective automatic `OPTIONS` response is exposed and the `Allow` header remains correct.
- Add a CLI regression test that captures `rule.methods` before and after `flask routes` to ensure route inspection does not mutate routing state.
- Add targeted tests for automatic `OPTIONS` with host matching or subdomains if those rule options are expected to be preserved for the synthetic route.

## Confidence Score
High, because the diff is small and the main behavioral change is localized to route registration, dispatch, and CLI route rendering.
