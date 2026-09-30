---
layout: page
permalink: /papers/
title: publications
description:
nav: true
nav_order: 2
---

<div class="papers-page">
  <p>
    The following is a list of papers and preprints. Use the controls below to sort, filter, or search
    by title, author, abstract, or topic. Click a topic tag to filter by it; click "Cite" on any entry
    to view and copy its BibTeX.
  </p>
  <p>* denotes equal contribution</p>

  <div class="papers-controls">
    <div class="papers-control">
      <label for="papers-sort">Sort by</label>
      <select id="papers-sort">
        <option value="year_desc" selected>Year</option>
        <option value="year_asc">Year (reverse)</option>
      </select>
    </div>
    <div class="papers-control">
      <label for="papers-limit">Limit to</label>
      <select id="papers-limit">
        <option value="all" selected>Everything</option>
        <option value="published">Published</option>
        <option value="preprints">Pre-prints</option>
      </select>
    </div>
    <div class="papers-control papers-control-search">
      <label for="papers-search">Search</label>
      <input type="text" id="papers-search" placeholder="titles, authors, abstracts, topics" autocomplete="off">
    </div>
  </div>

  <div id="papers-active-topic" class="papers-active-topic" hidden>
    Filtered by topic: <strong class="active-topic-name"></strong>
    <button type="button" class="clear-topic">&times; clear</button>
  </div>

  <div class="publications paperslist">
    <h2 class="bibliography">Preprints</h2>
    {% bibliography -f preprints -T bib_papers --group_by none %}
    {% bibliography -f papers -T bib_papers %}
  </div>
</div>

<script src="{{ '/assets/js/paperslist.js' | relative_url | bust_file_cache }}"></script>
