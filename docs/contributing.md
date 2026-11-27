# Contributing

Fork the [upstream repository](https://github.com/hiperhealth/pydantic-djmodel)
and create a working branch from its `main` branch. The package lives in
`src/pydantic_djmodel`, and the sample Django app lives in `tests`.

Use Python 3.12 with Poetry 2 for local development:

```bash
poetry env use python3.12
poetry install
poetry run pre-commit install
poetry run pre-commit run --all-files
poetry run pytest
poetry run mkdocs build --strict
poetry build
```

The pytest suite creates an SQLite database and checks both migration
generation and an ORM write and read. Open issues and pull requests in the
[upstream repository](https://github.com/hiperhealth/pydantic-djmodel).

## Release

This project uses semantic-release in order to cut a new release based on the
commit-message.

### Commit message format

**semantic-release** uses the commit messages to determine the consumer impact
of changes in the codebase. Following formalized conventions for commit
messages, **semantic-release** automatically determines the next
[semantic version](https://semver.org) number, generates a changelog and
publishes the release.

By default, **semantic-release** uses
[Angular Commit Message Conventions](https://github.com/angular/angular/blob/master/CONTRIBUTING.md#-commit-message-format).
The commit message format can be changed with the `preset` or `config` options\_
of the
[@semantic-release/commit-analyzer](https://github.com/semantic-release/commit-analyzer#options)
and
[@semantic-release/release-notes-generator](https://github.com/semantic-release/release-notes-generator#options)
plugins.

Tools such as [commitizen](https://github.com/commitizen/cz-cli) or
[commitlint](https://github.com/conventional-changelog/commitlint) can be used
to help contributors and enforce valid commit messages.

The table below shows which commit message gets you which release type when
`semantic-release` runs (using the default configuration):

| Commit message                                                 | Release type     |
| -------------------------------------------------------------- | ---------------- |
| `fix(pencil): stop graphite breaking when pressure is applied` | Fix Release      |
| `feat(pencil): add 'graphiteWidth' option`                     | Feature Release  |
| `perf(pencil): remove graphiteWidth option`                    | Chore            |
| `feat(pencil)!: The graphiteWidth option has been removed`     | Breaking Release |

Note: For a breaking change release, uses `!` at the end of the message prefix.

source:
<https://github.com/semantic-release/semantic-release/blob/master/README.md#commit-message-format>

As this project uses the `squash and merge` strategy, ensure to apply the commit
message format to the PR's title.
