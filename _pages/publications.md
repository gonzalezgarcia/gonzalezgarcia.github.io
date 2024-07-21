---
layout: page
permalink: /publications/
title: publications
description:
years: [2024,2023,2022,2021,2020,2019,2018,2017,2016,2015,2014]
nav: true
nav_order: 2
---

<!-- _pages/publications.md -->

<!-- Bibsearch Feature -->


<p>An up-to-date list is available on <a href="https://scholar.google.com/citations?user=4RU_vSQAAAAJ" target="_blank" rel="noopener noreferrer">Google Scholar</a>.</p>
<div class="publications">

{% include bib_search.liquid %}


{% bibliography -f preprints --group_by type %}
{% bibliography -f papers%}



