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
`release-name`, `release-url`, `release-body`.
Optional: `jira-project-key` (default `PP`).
See [`jira-release-sync/action.yml`](jira-release-sync/action.yml) for the full schema.

## License

Apache 2.0 — see [LICENSE](LICENSE).