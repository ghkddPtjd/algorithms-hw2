# Repository instructions

## Project constraints

- Read `SPEC.md` before changing implementation or behavior.
- Use only the Python standard library.
- In `src/`, do not use built-in `dict`, `set`, or `hash()`. Use the project hash-table
  implementation and explicit lists/nodes instead.
- Generate short codes from the monotonically increasing ID with `src/base62.py`;
  never derive codes from a URL's hash.
- Write or extend tests for behavior before implementing it. Once implementation
  work starts, do not weaken or modify those tests to make the change pass.
- Keep URL validation, error behavior, hash probing/comparison counts, and `/table`
  diagnostics consistent with `SPEC.md`.

## Git flow

- `main` is the stable branch; do not commit directly to `main`.
- Start each issue from the latest `develop` in
  `feature/<issue-number>-<short-name>`.
- Post meaningful progress updates on that GitHub issue while working.
- Commit each completed step with the message format
  `Step N: 한 일 (#이슈번호)`.
- Push the feature branch, merge it into `develop`, then push `develop`.
- Use a local `--no-ff` merge into `develop`; open a pull request only if requested.
- If a merge conflict occurs, resolve it on the feature branch, rerun relevant checks,
  and push the updated feature branch before merging.
- Close the issue only after its work is merged into `develop` and relevant checks pass.
- Do not merge feature work directly into `main`.

## Validation

- Run focused tests while iterating and `make test` before merging implementation.
- Run `git diff --check` before committing.
- Do not claim external checks (for example, phone access through a public port)
  unless they were actually performed.
