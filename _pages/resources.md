---
layout: page
permalink: /resources/
title: resources
description: 
nav: true
nav_order: 6
toc: false
show_title: false
---

<div class="papers-page">
  <p>
    Open Educational Resources (teaching materials, guides) and research tools (datasets, code)
    that are free to use, share, copy and edit with attribution. Check the license badge and the
    specific license of each resource before using it. Click a topic tag to filter by it, or search
    below.
  </p>


  <div class="papers-controls" style="grid-template-columns: repeat(2, 1fr); max-width: 480px;">
    <div class="papers-control">
      <label for="resources-limit">Limit to</label>
      <select id="resources-limit">
        <option value="all" selected>Everything</option>
        {% for type in site.data.resource_types %}
          <option value="{{ type.name }}">{{ type.name }}</option>
        {% endfor %}
      </select>
    </div>
    <div class="papers-control papers-control-search">
      <label for="resources-search">Search</label>
      <input type="text" id="resources-search" placeholder="titles, descriptions, collaborators" autocomplete="off">
    </div>
  </div>

  <div id="resources-active-topic" class="papers-active-topic" hidden>
    Filtered by topic: <strong class="active-topic-name"></strong>
    <button type="button" class="clear-topic">&times; clear</button>
  </div>

  <div class="publications paperslist" id="resourceslist">
    {% assign grouped_resources = site.data.resources | group_by: "type" %}
    {% for group in grouped_resources %}
      <h2 class="bibliography">{{ group.name }}</h2>
      {% for resource in group.items %}
        {% include resource_card.liquid entry=resource %}
      {% endfor %}
    {% endfor %}
  </div>
</div>

<script src="{{ '/assets/js/resourceslist.js' | relative_url | bust_file_cache }}"></script>
