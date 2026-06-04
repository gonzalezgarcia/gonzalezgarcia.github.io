---
layout: page
title: open science
permalink: /open-science/
description: >
  Transparent, reproducible science — preregistrations, open code, teaching materials, and outreach.
nav: false
nav_order: 6
published: false
body_class: open-science-page
---

{% assign gh        = site.data.open_science_stats.github %}
{% assign osf       = site.data.open_science_stats.osf %}
{% assign generated = site.data.open_science_stats.generated_at %}

{% assign ap_entries = site.data.aspredicted | where_exp: "item", "item.title != ''" %}
{% assign ap_count = ap_entries | size %}
{% assign total_prereg_count = osf.preregistrations | plus: ap_count %}
{% assign years_active = site.time | date: "%Y" | plus: 0 | minus: 2018 %}

<!-- ════════════════════════════════════════════════════════════
     HERO
     ════════════════════════════════════════════════════════════ -->

<div class="os-hero">
  <h1 class="os-hero-headline">Transparent.<br>Reproducible.<br>Shared.</h1>
  <!-- EDIT: lede sentence -->
  <p class="os-hero-lede">
    This page documents the open-science practices that run through my research —
    from preregistered hypotheses to publicly available code, teaching materials,
    and engagement beyond the lab.
  </p>
</div>

<!-- ════════════════════════════════════════════════════════════
     01 — PREREGISTRATION
     ════════════════════════════════════════════════════════════ -->

<section class="os-chapter" id="preregistration">

<div class="os-chap-header">
  <span class="os-chap-num" aria-hidden="true">01</span>
  <div class="os-chap-meta">
    <span class="os-chap-label">practice</span>
    <h2 class="os-chap-title">Pre-<br>registration</h2>
  </div>
</div>

<div class="os-stat-trio">
  <div class="os-big-stat">
    <span class="stat-value">{{ total_prereg_count }}</span>
    <span class="stat-label">preregistrations</span>
  </div>
  <div class="os-big-stat">
    <span class="stat-value">{{ years_active }}</span>
    <span class="stat-label">years active</span>
  </div>
  <div class="os-big-stat">
    <span class="stat-value">2</span>
    <span class="stat-label">registries</span>
  </div>
</div>

<p class="os-micro">A selection of recent preregistrations.</p>

{% assign sorted_ap  = site.data.aspredicted | sort: "date" | reverse %}
{% assign featured_ap = sorted_ap | where: "featured", true %}

{% if featured_ap.size > 0 %}
<table class="os-prereg-table" id="preregs-featured">
{% for item in featured_ap %}
{% if item.title and item.title != "" %}
<tr>
  <td class="prereg-title-cell">
    {% if item.url and item.url != "" %}
    <a href="{{ item.url }}" target="_blank" rel="noopener noreferrer" class="prereg-title-link">{{ item.title }}</a>
    {% else %}<span class="prereg-title-link">{{ item.title }}</span>{% endif %}
    {% if item.description and item.description != "" %}
    <span class="prereg-desc">{{ item.description }}</span>
    {% endif %}
  </td>
  <td class="prereg-year-cell">
    {% if item.date and item.date != "" %}
    <span class="prereg-year-pill">{{ item.date | slice: 0, 7 }}</span>
    {% endif %}
  </td>
</tr>
{% endif %}
{% endfor %}
</table>
{% endif %}

<!-- Full list revealed by toggle -->
<div id="preregs-full" class="d-none">
<table class="os-prereg-table">
{% for item in sorted_ap %}
{% if item.title and item.title != "" %}
<tr>
  <td class="prereg-title-cell">
    {% if item.url and item.url != "" %}
    <a href="{{ item.url }}" target="_blank" rel="noopener noreferrer" class="prereg-title-link">{{ item.title }}</a>
    {% else %}<span class="prereg-title-link">{{ item.title }}</span>{% endif %}
    {% if item.description and item.description != "" %}
    <span class="prereg-desc">{{ item.description }}</span>
    {% endif %}
  </td>
  <td class="prereg-year-cell">
    {% if item.date and item.date != "" %}
    <span class="prereg-year-pill">{{ item.date | slice: 0, 7 }}</span>
    {% endif %}
  </td>
</tr>
{% endif %}
{% endfor %}
</table>
</div>

{% if ap_count > 0 %}
<button type="button" class="os-show-more mt-2" id="preregs-toggle"
  onclick="(function(){
    var full = document.getElementById('preregs-full');
    var feat = document.getElementById('preregs-featured');
    var opening = full.classList.contains('d-none');
    full.classList.toggle('d-none', !opening);
    if(feat) feat.classList.toggle('d-none', opening);
    document.getElementById('preregs-toggle').textContent =
      opening ? 'Show fewer ↑' : 'Show all {{ ap_count }} preregistrations →';
  })()">
  Show all {{ ap_count }} preregistrations →
</button>
{% endif %}

</section>

<!-- ════════════════════════════════════════════════════════════
     02 — CODE & DATA
     ════════════════════════════════════════════════════════════ -->

<section class="os-chapter" id="code-data">

<div class="os-chap-header">
  <span class="os-chap-num" aria-hidden="true">02</span>
  <div class="os-chap-meta">
    <span class="os-chap-label">open source</span>
    <h2 class="os-chap-title">Code &amp;<br>data</h2>
  </div>
</div>

<p class="os-micro">Analysis scripts and datasets shared publicly alongside published work.</p>

<div class="os-code-grid">
{% assign repo_shown = 0 %}
{% for repo in gh.pinned_repos %}
  {% if repo.description and repo.description != "" and repo_shown < 4 %}
  {% assign repo_shown = repo_shown | plus: 1 %}
  <div class="os-code-card">
    <div class="code-name">
      <a href="{{ repo.url }}" target="_blank" rel="noopener noreferrer">{% if repo.owner and repo.owner != "" and repo.owner != site.github_username %}<span style="opacity:0.45">{{ repo.owner }}/</span>{% endif %}{{ repo.name }}</a>
    </div>
    <div class="code-desc">{{ repo.description }}</div>
    <div class="code-meta">{% if repo.language and repo.language != "" %}{{ repo.language }}{% endif %}{% if repo.updated_at and repo.updated_at != "" %} &middot; {{ repo.updated_at | slice: 0, 4 }}{% endif %}</div>
  </div>
  {% endif %}
{% endfor %}
</div>

<p class="os-link-line"><a href="{{ gh.profile_url }}" target="_blank" rel="noopener noreferrer">See all {{ gh.repos }} repositories on GitHub &nearr;</a></p>
<p class="os-link-line"><a href="{{ osf.profile_url }}" target="_blank" rel="noopener noreferrer">{{ osf.projects }} projects on OSF &nearr;</a></p>

</section>

<!-- ════════════════════════════════════════════════════════════
     03 — TEACHING
     ════════════════════════════════════════════════════════════ -->

{% assign teaching_entries = site.data.teaching | where_exp: "item", "item.title != ''" %}
{% if teaching_entries.size > 0 %}

<section class="os-chapter" id="teaching">

<div class="os-chap-header">
  <span class="os-chap-num" aria-hidden="true">03</span>
  <div class="os-chap-meta">
    <span class="os-chap-label">education</span>
    <h2 class="os-chap-title">Teaching &amp;<br>materials</h2>
  </div>
</div>

<p class="os-micro">Courses and open resources for students in cognitive neuroscience.</p>

<table class="os-teaching-table">
{% for item in site.data.teaching %}
{% if item.title and item.title != "" %}
<tr>
  <td class="teach-year">{{ item.year }}</td>
  <td class="teach-title">
    {% if item.url and item.url != "" %}
    <a href="{{ item.url }}" target="_blank" rel="noopener noreferrer">{{ item.title }}</a>
    {% else %}{{ item.title }}{% endif %}
    {% if item.description and item.description != "" %}
    <span class="teach-desc">{{ item.description }}</span>
    {% endif %}
  </td>
  <td class="teach-audience">{{ item.audience }}</td>
</tr>
{% endif %}
{% endfor %}
</table>

</section>
{% endif %}

<!-- ════════════════════════════════════════════════════════════
     04 — OUTREACH
     ════════════════════════════════════════════════════════════ -->

{% assign has_outreach = false %}
{% assign outreach_count = 0 %}
{% if site.data.outreach %}
  {% for item in site.data.outreach %}
    {% if item.title and item.title != "" %}
      {% assign has_outreach = true %}
      {% assign outreach_count = outreach_count | plus: 1 %}
    {% endif %}
  {% endfor %}
{% endif %}

{% if has_outreach %}
<section class="os-chapter" id="outreach">

<div class="os-chap-header">
  <span class="os-chap-num" aria-hidden="true">04</span>
  <div class="os-chap-meta">
    <span class="os-chap-label">engagement</span>
    <h2 class="os-chap-title">Out-<br>reach</h2>
  </div>
</div>

<p class="os-micro">Talks, workshops, and public communication beyond academic venues.</p>

{% assign sorted_outreach = site.data.outreach | sort: "date" | reverse %}
{% if outreach_count < 2 %}
<div class="os-outreach-grid os-single-col">
{% else %}
<div class="os-outreach-grid">
{% endif %}
{% for item in sorted_outreach %}
{% if item.title and item.title != "" %}
<div class="os-outreach-card">
  {% if item.type and item.type != "" %}
  <span class="outreach-type">{{ item.type }}</span>
  {% endif %}
  <div class="outreach-title">
    {% if item.url and item.url != "" %}
    <a href="{{ item.url }}" target="_blank" rel="noopener noreferrer">{{ item.title }}</a>
    {% else %}{{ item.title }}{% endif %}
  </div>
  <div class="outreach-venue">
    {% if item.venue and item.venue != "" %}{{ item.venue }}{% endif %}{% if item.venue and item.venue != "" and item.date and item.date != "" %} &middot; {% endif %}{% if item.date and item.date != "" %}{{ item.date | slice: 0, 7 }}{% endif %}
  </div>
</div>
{% endif %}
{% endfor %}
</div>

</section>
{% endif %}

<!-- ════════════════════════════════════════════════════════════
     FOOTER
     ════════════════════════════════════════════════════════════ -->

<p class="os-footer-note">
  GitHub and OSF stats fetched automatically at each site build.{% if generated and generated != "never" %} Last updated: {{ generated | slice: 0, 10 }}.{% endif %}
</p>
