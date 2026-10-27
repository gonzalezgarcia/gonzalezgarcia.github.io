# gonzalezgarcia.github.io

Source for my academic website, **<https://gonzalezgarcia.github.io>**.

Built on [al-folio](https://github.com/alshedivat/al-folio) (MIT, see [LICENSE](LICENSE)). The theme docs
([INSTALL.md](INSTALL.md), [CUSTOMIZE.md](CUSTOMIZE.md), [FAQ.md](FAQ.md)) come from upstream unchanged.
This file only covers what is specific to this site.

## How content gets updated

**Publications.** Every Monday, [update-bibliography.yml](.github/workflows/update-bibliography.yml) checks my
ORCID for new works and, if there are any, opens a PR from the `update-bibliography` branch that adds them to
`_bibliography/papers.bib` or `_bibliography/preprints.bib`. Before merging, read the PR body: it flags entries
with no open-access PDF (upload one to `assets/pdf/` and add a `pdf` field) and entries the keyword heuristic
couldn't tag with a topic. The bot skips any DOI that is already in the `.bib` files or listed in
[`_scripts/orcid_seen_dois.json`](_scripts/orcid_seen_dois.json), and adds every DOI it handles to that list, so
leaving an unwanted entry out of the bib is enough to stop it coming back. The full filing rules are in the
docstring of [`_scripts/update_bibliography.py`](_scripts/update_bibliography.py).

**CV.** The CV is built in my private `cv` repository, which opens a PR here from the `cv-update` branch replacing
`assets/pdf/CV-Gonzalez-Garcia.pdf` and its plain-text copy. Those PRs are opened with my own token, so GitHub
doesn't notify me; [notify-cv-pr.yml](.github/workflows/notify-cv-pr.yml) posts a comment that @mentions me instead.

**Open-science stats.** `_data/open_science_stats.yml` is regenerated from the GitHub and OSF APIs on every deploy
but never committed back, so the copy in the repo is usually stale. Run
`python3 _scripts/fetch_open_science_stats.py` before a local preview if you need current numbers.

**Deploying.** A push to `master` runs [deploy.yml](.github/workflows/deploy.yml), which builds the site and
pushes it to the `gh-pages` branch that GitHub Pages serves. PRs run the same build as a check without deploying.
Editing this README doesn't trigger a deploy.

## Local preview

```bash
bundle install
bundle exec jekyll serve   # http://localhost:4000
```

Or `docker compose up` (<http://localhost:8080>). See [INSTALL.md](INSTALL.md) for details.

## Folders that aren't from al-folio

- `_scripts/`: the bibliography bot and the open-science stats fetcher described above.
- `_archive/`: retired pages kept for reference. Jekyll doesn't build or publish it; each subfolder has a README
  explaining how to restore it.
