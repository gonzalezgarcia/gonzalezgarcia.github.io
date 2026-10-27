@README.md

## Notes for agents

- Default branch is `master`. PRs go to `gonzalezgarcia/gonzalezgarcia.github.io`, never to the `upstream` remote
  (alshedivat/al-folio). Pass `--repo gonzalezgarcia/gonzalezgarcia.github.io` to `gh` if `gh repo set-default`
  hasn't been run in this clone.
- `update-bibliography` and `cv-update` are written by automation (see README); don't commit to them by hand.
- `TOPIC_KEYWORDS` in `_scripts/update_bibliography.py` mirrors the topic `name`s in `_data/topics.yml` by hand.
  Change both together.
- When adding or fixing a `.bib` entry by hand, follow the conventions in the docstring of
  `_scripts/update_bibliography.py` so manual and bot entries look the same.
- INSTALL.md, CUSTOMIZE.md, FAQ.md and CONTRIBUTING.md are upstream al-folio docs. Leave them unchanged and put
  site-specific notes in README.md.
- Ignore `_site/` (build output) and `redesign/` (a gitignored local experiment with its own `node_modules`).
