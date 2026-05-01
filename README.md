# Palace GitHub Actions

Reusable GitHub Actions shared across Palace Project repositories.

## Versioning

Releases are tagged `vX.Y.Z`. A moving `vX` tag (and `vX.Y`) always points at the
latest matching release, updated automatically by `.github/workflows/release.yml`
when a release is published. Reference these moving tags from consumer
workflows:

```yaml
uses: ThePalaceProject/github-actions/<action>@v1
```

Pin to `vX.Y.Z` if you need an immutable reference.

## Reusable workflows

### `claude-review`

Runs Claude Code as a PR reviewer on `pull_request` events. The workflow owns
its trigger filter (skips Dependabot), concurrency group, permissions, and
review prompt — consumers just dispatch.

```yaml
name: Claude PR Review
on:
  pull_request:
    types: [opened, synchronize, reopened]
jobs:
  review:
    uses: ThePalaceProject/github-actions/.github/workflows/claude-review.yml@v1
    secrets:
      CLAUDE_CODE_OAUTH_TOKEN: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
```

Required secret: `CLAUDE_CODE_OAUTH_TOKEN`.

Optional input `additional_prompt` appends repo-specific guidance to the default
review prompt:

```yaml
jobs:
  review:
    uses: ThePalaceProject/github-actions/.github/workflows/claude-review.yml@v1
    with:
      additional_prompt: |
        Pay special attention to changes under db/migrations/.
    secrets:
      CLAUDE_CODE_OAUTH_TOKEN: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
```

## Actions

### `poetry`

Installs [Poetry](https://python-poetry.org/) with optional caching of both the
Poetry installation and the project's package cache.

```yaml
- uses: ThePalaceProject/github-actions/poetry@v1
  with:
    version: "2.1.1"
    cache: "true"
    cache-name: "ci"
```

Inputs: `version`, `cache`, `cache-restore-only`, `cache-name`.
Outputs: `version`, `home`, `cache-dir`.
See [`poetry/action.yml`](poetry/action.yml) for the full schema.

### `jira-release-sync`

On a published GitHub release, creates a matching Jira version, links the
release notes back to it, and updates `fixVersions` on every Jira issue
referenced in the release body.

```yaml
- uses: ThePalaceProject/github-actions/jira-release-sync@v1
  with:
    jira-base-url:    ${{ secrets.JIRA_BASE_URL }}
    jira-user-email:  ${{ secrets.JIRA_USER_EMAIL }}
    jira-api-token:   ${{ secrets.JIRA_API_TOKEN }}
    release-name:     "CM ${{ github.event.release.tag_name }}"
    release-url:      ${{ github.event.release.html_url }}
    release-body:     ${{ github.event.release.body }}
```

Required inputs: `jira-base-url`, `jira-user-email`, `jira-api-token`,
`release-name`, `release-url`. Exactly one of `release-body` or
`release-body-file` must be provided — `release-body-file` is read only when
`release-body` is empty.
Optional: `jira-project-key` (default `PP`).
See [`jira-release-sync/action.yml`](jira-release-sync/action.yml) for the full schema.

## License

Apache 2.0 — see [LICENSE](LICENSE).
