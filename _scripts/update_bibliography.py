#!/usr/bin/env python3
"""
Check ORCID for works not yet in _bibliography/*.bib and add them, following
the same conventions used when adding entries by hand:

- bioRxiv preprints (detected via the bioRxiv API, not Crossref's generic
  "posted-content" type -- that type also covers things like eLife's
  reviewed preprints, which are filed as regular papers here) go into
  preprints.bib using bioRxiv's own citation fields, plus the fixed
  award/award_name "preprint" badge.
- Everything else goes into papers.bib using the BibTeX returned by DOI
  content negotiation (the same thing `curl -LH "Accept: application/x-bibtex"
  https://doi.org/<DOI>` gives you), with `abstract` (from Crossref, cleaned
  of JATS tags) and `html` (the DOI's resolved landing page) added.
- When a tracked preprint is linked by Crossref to a published version
  (relation.is-preprint-of / has-preprint, checked from both sides since
  publishers don't always deposit both directions), the preprint entry is
  removed from preprints.bib and the published version is added to
  papers.bib instead, reusing the preprint's abstract if the publisher
  didn't deposit one.
- A preprint on a server other than bioRxiv (no established template on
  this site) is flagged for manual review instead of guessed at.
- `pdf` is filled in via Unpaywall when an open-access copy exists;
  otherwise it's left out and the entry is flagged in the run summary so a
  human can upload an author copy to assets/pdf/ and add the field by hand.
- `topics` (the /papers/ page's tag pills) is auto-assigned via a keyword
  match against title+abstract (see TOPIC_KEYWORDS below, kept in sync by
  hand with _data/topics.yml's topic names). This is a rough heuristic, not
  the nuanced read a human would give it -- every entry goes out in a PR
  for review anyway, so it's fine if it's sometimes wrong or empty; an
  empty match is flagged in the run summary.

ORCID lists every work a researcher has ever touched, which is broader than
what belongs in a curated personal bibliography (e.g. large consortium
papers, superseded preprint versions). So this script never backfills: the
first run just records today's ORCID DOIs as a baseline (_scripts/
orcid_seen_dois.json) without adding anything. Every later run only
considers DOIs that are new *since* that baseline, and marks each one seen
the first time it's handled (added, migrated, deduped, or flagged) so it's
never re-proposed -- if you don't want something it flagged, just leave it
out of the bib and it won't come back.

Run manually with `python3 _scripts/update_bibliography.py`, or via the
"Update bibliography" GitHub Action (scheduled weekly, opens a PR). Set
SUMMARY_FILE to also write a markdown run summary (used for the PR body).
"""

import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
CONFIG_FILE = os.path.join(REPO_ROOT, "_config.yml")
PAPERS_BIB = os.path.join(REPO_ROOT, "_bibliography", "papers.bib")
PREPRINTS_BIB = os.path.join(REPO_ROOT, "_bibliography", "preprints.bib")
SEEN_DOIS_FILE = os.path.join(os.path.dirname(__file__), "orcid_seen_dois.json")

CONTACT_EMAIL = "cgonzalgarcia@gmail.com"
USER_AGENT = f"gonzalezgarcia.github.io bibliography bot (mailto:{CONTACT_EMAIL})"

# Keyword -> topic heuristic for auto-tagging new entries, kept in sync by hand
# with the `name` values in _data/topics.yml (that file also carries the pill
# color; this script only needs the matching logic). Matching is a simple
# lowercase substring count over title+abstract, so it's approximate -- new
# entries go through a PR either way, so a human reviews/corrects it before
# it's ever live.
TOPIC_KEYWORDS = {
    "Cognitive Control": [
        "cognitive control", "inhibition", "conflict monitoring", "conflict",
        "task-set", "task set", "proactive control", "reactive control",
        "interference",
    ],
    "Instructions & Task Implementation": [
        "instruction", "instructed", "instructions", "proceduralization",
        "proceduralize", "novel task", "verbal instruction",
    ],
    "Working Memory": [
        "working memory", "retro-cue", "retro-cues", "short-term memory",
        "maintenance of information",
    ],
    "Attention": [
        "attention", "attentional", "exogenous", "endogenous",
        "selective attention", "spatial cue", "spatial attention",
    ],
    "Visual Perception & Perceptual Learning": [
        "perception", "perceptual", "visual perception", "ambiguity",
        "ambiguous", "perceptual prior", "perceptual learning",
        "visual ambiguity",
    ],
    "Decision-Making": [
        "decision-making", "decision making", "choice", "drift-diffusion",
        "diffusion model", "evidence accumulation", "decision process",
    ],
    "Consciousness & Metacognition": [
        "consciousness", "conscious", "metacognition", "awareness",
        "insight", "unconscious", "subjective experience", "free will",
    ],
    "Social Cognition": [
        "social cognition", "social", "trust", "trustworthiness", "moral",
        "interpersonal", "valence", "ultimatum",
    ],
    "Neuroimaging Methods & Meta-science": [
        "fmri", "multivariate pattern", "mvpa", "decoding methods", "methodology",
        "meta-analysis", "reproducibility", "replication", "searchlight",
        "many teams", "statistical analysis", "analysis pipeline",
    ],
    "Memory": [
        "episodic memory", "long-term memory", "engram", "memory trace",
        "memory encoding", "memory retrieval", "memory transformation",
        "memory consolidation", "recognition memory", "false memory",
    ],
}


def classify_topics(text, max_topics=3):
    text = (text or "").lower()
    scored = []
    for topic, keywords in TOPIC_KEYWORDS.items():
        hits = sum(text.count(kw) for kw in keywords)
        if hits:
            scored.append((hits, topic))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [topic for _, topic in scored[:max_topics]]


PREPRINT_PUBLISHER = "Cold Spring Harbor Laboratory"
PREPRINT_AWARD = (
    "award={This is a **preprint**! [Read more](https://en.wikipedia.org/wiki/Preprint)},\n"
    "  award_name={preprint},"
)


def _get(url, accept=None, label="", retries=2):
    headers = {"User-Agent": USER_AGENT}
    if accept:
        headers["Accept"] = accept
    req = urllib.request.Request(url, headers=headers)
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return resp.read().decode("utf-8", errors="replace"), resp.geturl()
        except Exception as exc:
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
                continue
            print(f"  [warn] {label or url}: {exc}", file=sys.stderr)
            return None, None


def get_json(url, label=""):
    text, _ = _get(url, accept="application/json", label=label)
    if text is None:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        print(f"  [warn] {label or url}: bad JSON ({exc})", file=sys.stderr)
        return None


def get_orcid_id():
    with open(CONFIG_FILE, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"\s*orcid_id:\s*(\S+)", line)
            if m:
                return m.group(1).strip()
    return None


def normalize_doi(doi):
    doi = doi.strip().lower()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi)
    return doi


def load_seen_dois():
    if not os.path.exists(SEEN_DOIS_FILE):
        return None
    with open(SEEN_DOIS_FILE, encoding="utf-8") as f:
        return set(json.load(f))


def save_seen_dois(seen):
    with open(SEEN_DOIS_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(seen), f, indent=2)
        f.write("\n")


def existing_dois(*bib_paths):
    dois = set()
    for path in bib_paths:
        with open(path, encoding="utf-8") as f:
            content = f.read()
        for m in re.finditer(r"doi\s*=\s*\{([^}]*)\}", content, re.IGNORECASE):
            dois.add(normalize_doi(m.group(1)))
    return dois


def orcid_work_dois(orcid_id):
    data = get_json(
        f"https://pub.orcid.org/v3.0/{orcid_id}/works", label="ORCID works list"
    )
    if not data:
        return []
    dois = []
    for group in data.get("group", []):
        for ext_id in group.get("external-ids", {}).get("external-id", []):
            if ext_id.get("external-id-type") == "doi":
                dois.append(ext_id["external-id-value"])
                break
    return dois


def crossref_work(doi):
    url = f"https://api.crossref.org/works/{doi}?mailto={CONTACT_EMAIL}"
    data = get_json(url, label=f"Crossref {doi}")
    return data.get("message") if data else None


def related_dois(crossref_msg, relation_type):
    if not crossref_msg:
        return []
    rels = crossref_msg.get("relation", {}).get(relation_type, [])
    return [normalize_doi(r["id"]) for r in rels if r.get("id-type") == "doi"]


def biorxiv_details(doi):
    data = get_json(
        f"https://api.biorxiv.org/details/biorxiv/{doi}", label=f"bioRxiv {doi}"
    )
    if not data:
        return None
    collection = data.get("collection") or []
    if not collection:
        return None
    return collection[-1]  # latest version


def clean_jats(text):
    if not text:
        return ""
    text = re.sub(r"</?jats:title[^>]*>.*?</jats:title>", "", text, flags=re.DOTALL)
    text = re.sub(r"</?jats:[a-zA-Z]+[^>]*>", "", text)
    return re.sub(r"\s+", " ", text).strip()


def resolve_landing_page(doi):
    _, final_url = _get(f"https://doi.org/{doi}", label=f"resolve {doi}")
    return final_url


def unpaywall_pdf(doi):
    data = get_json(
        f"https://api.unpaywall.org/v2/{doi}?email={CONTACT_EMAIL}",
        label=f"Unpaywall {doi}",
    )
    if not data:
        return None
    locations = []
    if data.get("best_oa_location"):
        locations.append(data["best_oa_location"])
    locations.extend(data.get("oa_locations") or [])
    for loc in locations:
        if loc and loc.get("url_for_pdf"):
            return loc["url_for_pdf"]
    return None


def parse_bibtex_fields(bibtex_text):
    """Parse a single flat BibTeX entry (as returned by DOI content
    negotiation) into (entrytype, citekey, {field: value})."""
    header = re.match(r"\s*@(\w+)\{([^,]+),", bibtex_text)
    if not header:
        return None, None, {}
    entrytype, citekey = header.group(1), header.group(2).strip()
    fields = {}
    pos = header.end()
    for m in re.finditer(r"(\w+)\s*=\s*\{", bibtex_text[pos:]):
        start = pos + m.end()
        depth = 1
        i = start
        while i < len(bibtex_text) and depth:
            if bibtex_text[i] == "{":
                depth += 1
            elif bibtex_text[i] == "}":
                depth -= 1
            i += 1
        fields[m.group(1).lower()] = bibtex_text[start : i - 1]
    return entrytype, citekey, fields


def fetch_doi_bibtex(doi):
    text, _ = _get(
        f"https://doi.org/{doi}", accept="application/x-bibtex", label=f"bibtex {doi}"
    )
    if not text:
        return None, None, {}
    return parse_bibtex_fields(text)


def strip_diacritics(text):
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(c for c in normalized if not unicodedata.combining(c))


def slugify_key_component(text):
    ascii_text = strip_diacritics(text)
    return re.sub(r"[^A-Za-z0-9-]", "", ascii_text)


def unique_key(candidate, taken):
    if candidate not in taken:
        return candidate
    for suffix in "abcdefghijklmnopqrstuvwxyz":
        if f"{candidate}{suffix}" not in taken:
            return f"{candidate}{suffix}"
    raise RuntimeError(f"could not find a free citekey for {candidate}")


def format_entry(entrytype, citekey, field_order, fields, trailing_raw=None):
    lines = [f"@{entrytype}{{{citekey},"]
    for field in field_order:
        if field in fields and fields[field]:
            lines.append(f"  {field} = {{{fields[field]}}},")
    if trailing_raw:
        lines.append(f"  {trailing_raw}")
    lines.append("}")
    return "\n".join(lines) + "\n"


PAPER_FIELD_ORDER = [
    "author",
    "title",
    "journal",
    "year",
    "month",
    "volume",
    "number",
    "pages",
    "issn",
    "doi",
    "url",
    "html",
    "pdf",
    "abstract",
    "topics",
]

PREPRINT_FIELD_ORDER = [
    "author",
    "title",
    "elocation-id",
    "year",
    "doi",
    "publisher",
    "abstract",
    "url",
    "pdf",
    "journal",
    "topics",
]


def build_paper_entry(doi, taken_keys, crossref_msg=None, fallback_abstract=None):
    _, cr_key, cr_fields = fetch_doi_bibtex(doi)
    if not cr_key:
        print(f"  [warn] could not fetch BibTeX for {doi}", file=sys.stderr)
        return None

    if crossref_msg is None:
        crossref_msg = crossref_work(doi) or {}
    abstract = clean_jats(crossref_msg.get("abstract", "")) or fallback_abstract or ""
    html_url = resolve_landing_page(doi) or ""
    pdf_url = unpaywall_pdf(doi) or ""

    fields = dict(cr_fields)
    fields["doi"] = doi
    if html_url:
        fields["html"] = html_url
    if pdf_url:
        fields["pdf"] = pdf_url
    if abstract:
        fields["abstract"] = abstract

    topics = classify_topics(f"{cr_fields.get('title', '')} {abstract}")
    if topics:
        fields["topics"] = ", ".join(topics)

    key = unique_key(cr_key, taken_keys)
    taken_keys.add(key)
    entry = format_entry("article", key, PAPER_FIELD_ORDER, fields)
    needs_pdf = not pdf_url
    needs_abstract = not abstract
    needs_topics = not topics
    return key, entry, needs_pdf, needs_abstract, needs_topics


def build_preprint_entry(doi, taken_keys, details=None):
    details = details or biorxiv_details(doi)
    if not details:
        return None
    _, _, cr_fields = fetch_doi_bibtex(doi)
    author = cr_fields.get("author", details.get("authors", ""))
    title = cr_fields.get("title", details.get("title", ""))

    doi_suffix = doi.split("/", 1)[1] if "/" in doi else doi
    date_parts = (details.get("date") or "").split("-")
    if len(date_parts) == 3:
        url = f"https://www.biorxiv.org/content/early/{date_parts[0]}/{date_parts[1]}/{date_parts[2]}/{doi_suffix}"
    else:
        url = f"https://www.biorxiv.org/content/10.1101/{doi_suffix}"
    pdf = url + ".full.pdf"
    abstract = details.get("abstract", "")
    topics = classify_topics(f"{title} {abstract}")

    fields = {
        "author": author,
        "title": title,
        "elocation-id": doi_suffix,
        "year": (details.get("date") or "")[:4],
        "doi": doi,
        "publisher": PREPRINT_PUBLISHER,
        "abstract": abstract,
        "url": url,
        "pdf": pdf,
        "journal": "bioRxiv",
    }
    if topics:
        fields["topics"] = ", ".join(topics)

    first_author_surname = author.split(",")[0].split(" and ")[0]
    key = unique_key(
        slugify_key_component(first_author_surname) + doi_suffix, taken_keys
    )
    taken_keys.add(key)
    entry = format_entry(
        "preprint", key, PREPRINT_FIELD_ORDER, fields, trailing_raw=PREPRINT_AWARD
    )
    return key, entry, not topics


def find_citekeys(content):
    return set(re.findall(r"@\w+\{\s*([^,\s]+)\s*,", content))


def find_preprint_doi_entries(content):
    """Return [(doi, full_entry_text)] for each entry in preprints.bib."""
    entries = []
    for m in re.finditer(r"@\w+\s*\{[^@]*?\n\}\n?", content, re.DOTALL):
        entry_text = m.group(0)
        doi_m = re.search(r"doi\s*=\s*\{([^}]*)\}", entry_text, re.IGNORECASE)
        if doi_m:
            entries.append((normalize_doi(doi_m.group(1)), entry_text))
    return entries


def main():
    summary_lines = []

    def summarize(line):
        print(line)
        summary_lines.append(line)

    try:
        _run(summarize)
    finally:
        summary_file = os.environ.get("SUMMARY_FILE")
        if summary_file:
            with open(summary_file, "w", encoding="utf-8") as f:
                f.write("\n".join(summary_lines) + "\n" if summary_lines else "Nothing to report.\n")


def _run(summarize):
    orcid_id = get_orcid_id()
    if not orcid_id:
        summarize("No orcid_id configured in _config.yml, nothing to do.")
        return

    with open(PAPERS_BIB, encoding="utf-8") as f:
        papers_content = f.read()
    with open(PREPRINTS_BIB, encoding="utf-8") as f:
        preprints_content = f.read()

    taken_keys = find_citekeys(papers_content) | find_citekeys(preprints_content)
    tracked_dois = existing_dois(PAPERS_BIB, PREPRINTS_BIB)

    new_paper_entries = []
    new_preprint_entries = []
    flagged_for_pdf = []
    flagged_for_abstract = []
    flagged_for_topics = []
    flagged_for_review = []

    # 1. Migrate any tracked preprint that Crossref now links to a published version.
    for preprint_doi, entry_text in find_preprint_doi_entries(preprints_content):
        msg = crossref_work(preprint_doi)
        published_doi = next(iter(related_dois(msg, "is-preprint-of")), None)
        if not published_doi or published_doi in tracked_dois:
            continue
        old_abstract_m = re.search(
            r"abstract\s*=\s*\{([^}]*)\}", entry_text, re.IGNORECASE
        )
        fallback_abstract = old_abstract_m.group(1) if old_abstract_m else None
        summarize(f"Migrating preprint {preprint_doi} -> published {published_doi}")
        result = build_paper_entry(
            published_doi, taken_keys, fallback_abstract=fallback_abstract
        )
        if not result:
            continue
        key, entry, needs_pdf, needs_abstract, needs_topics = result
        new_paper_entries.append(entry)
        if needs_pdf:
            flagged_for_pdf.append(key)
        if needs_abstract:
            flagged_for_abstract.append(key)
        if needs_topics:
            flagged_for_topics.append(key)
        preprints_content = preprints_content.replace(entry_text, "")
        tracked_dois.add(published_doi)

    # 2. Establish a baseline on first run; never backfill the existing gap
    #    between ORCID and the curated bib files.
    seen_dois = load_seen_dois()
    orcid_dois = {normalize_doi(d) for d in orcid_work_dois(orcid_id)}
    if seen_dois is None:
        save_seen_dois(orcid_dois | tracked_dois)
        summarize(
            f"First run: recorded a baseline of {len(orcid_dois)} ORCID work(s). "
            "Nothing was added -- only works appearing on ORCID after today will "
            "be proposed in future runs."
        )
        _write_if_changed(new_paper_entries, new_preprint_entries, papers_content, preprints_content)
        return

    candidates = [d for d in orcid_dois if d not in seen_dois and d not in tracked_dois]

    # Papers first, so a same-run preprint+published pair doesn't add both.
    def classify(doi):
        details = biorxiv_details(doi)
        return ("preprint", details) if details else ("paper", None)

    classified = {doi: classify(doi) for doi in candidates}

    for doi, (kind, _details) in classified.items():
        if kind != "paper":
            continue
        msg = crossref_work(doi)
        preprint_sibling = next(iter(related_dois(msg, "has-preprint")), None)
        result = build_paper_entry(doi, taken_keys, crossref_msg=msg)
        seen_dois.add(doi)
        if not result:
            flagged_for_review.append((doi, "could not fetch BibTeX"))
            continue
        key, entry, needs_pdf, needs_abstract, needs_topics = result
        new_paper_entries.append(entry)
        if needs_pdf:
            flagged_for_pdf.append(key)
        if needs_abstract:
            flagged_for_abstract.append(key)
        if needs_topics:
            flagged_for_topics.append(key)
        tracked_dois.add(doi)
        if preprint_sibling:
            seen_dois.add(preprint_sibling)
            for pre_doi, entry_text in find_preprint_doi_entries(preprints_content):
                if pre_doi == preprint_sibling:
                    preprints_content = preprints_content.replace(entry_text, "")
                    summarize(f"Removed superseded preprint {pre_doi} (now published as {doi})")

    for doi, (kind, details) in classified.items():
        if kind != "preprint" or doi in seen_dois:
            continue
        msg = crossref_work(doi)
        published_sibling = next(iter(related_dois(msg, "is-preprint-of")), None)
        seen_dois.add(doi)
        if published_sibling and (
            published_sibling in tracked_dois or published_sibling in seen_dois
        ):
            summarize(f"Skipping preprint {doi}: already published as {published_sibling}")
            continue
        result = build_preprint_entry(doi, taken_keys, details=details)
        if not result:
            flagged_for_review.append((doi, "could not build preprint entry"))
            continue
        key, entry, needs_topics = result
        new_preprint_entries.append(entry)
        if needs_topics:
            flagged_for_topics.append(key)
        tracked_dois.add(doi)

    _write_if_changed(new_paper_entries, new_preprint_entries, papers_content, preprints_content)
    save_seen_dois(seen_dois | orcid_dois)

    if not new_paper_entries and not new_preprint_entries and not flagged_for_review:
        summarize("No new works found.")
        return

    summarize(
        f"Added {len(new_paper_entries)} paper(s), {len(new_preprint_entries)} preprint(s)."
    )
    if flagged_for_pdf:
        summarize(
            "No open-access PDF found for: "
            + ", ".join(flagged_for_pdf)
            + " -- add `pdf`/`html` by hand once you have an author copy."
        )
    if flagged_for_abstract:
        summarize(
            "No abstract available from Crossref for: "
            + ", ".join(flagged_for_abstract)
            + " -- paste one in by hand."
        )
    if flagged_for_topics:
        summarize(
            "Could not confidently auto-tag a topic for: "
            + ", ".join(flagged_for_topics)
            + " -- add a `topics` field by hand (see _data/topics.yml for the list)."
        )
    if flagged_for_review:
        summarize("Needs manual review (not added automatically):")
        for doi, reason in flagged_for_review:
            summarize(f"  - {doi}: {reason}")


def _write_if_changed(new_paper_entries, new_preprint_entries, papers_content, preprints_content):
    if new_paper_entries:
        with open(PAPERS_BIB, "w", encoding="utf-8") as f:
            f.write("\n".join(new_paper_entries) + "\n\n" + papers_content)
    current_preprints = open(PREPRINTS_BIB, encoding="utf-8").read()
    if new_preprint_entries or preprints_content != current_preprints:
        with open(PREPRINTS_BIB, "w", encoding="utf-8") as f:
            f.write("\n".join(new_preprint_entries) + "\n\n" + preprints_content)


if __name__ == "__main__":
    main()
