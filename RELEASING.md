# Releasing

1. Update the version in `pyproject.toml` and run `uv lock`.
2. Run `uv run ruff check .`, `uv run ruff format --check .`, and `uv run pytest`.
3. Run `uv build` and try the wheel in a clean environment.
4. Commit and push, then create and push a matching tag, for example `v0.2.0`.

The publish workflow runs the full CI matrix, checks that the tag matches the package version, builds and smoke-tests the distributions, and uploads them with `uv publish`. It also creates a GitHub release containing the wheel and source distribution. Failed publishes can be retried with the workflow's **Run workflow** action against the same tag.

The repository's existing `PYPI_API_TOKEN` Actions secret is supported. For tokenless publishing, configure a trusted publisher on the PyPI project with:

- Owner: `Times0`
- Repository: `PygameUIKit`
- Workflow: `publish-to-pypi.yml`
- Environment: `pypi`

After configuring trusted publishing, remove `PYPI_API_TOKEN` from GitHub Actions secrets; the workflow then uses OIDC automatically. No credentials belong in this repository.
