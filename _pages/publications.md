---
layout: page
permalink: /publications/
title: publications
description: "* denotes equal contribution."
years: [2022,2021,2020,2019,2018,2017,2016,2015,2014]
nav: true
nav_order: 1

---
<!-- _pages/publications.md -->
<p>An up-to-date list is available on <a href="https://scholar.google.com/citations?user=4RU_vSQAAAAJ" target="_blank" rel="noopener noreferrer">Google Scholar</a>.</p>
<div class="publications">

<h2 class="year">Preprints</h2>
{% bibliography -f preprints %}


{%- for y in page.years %}
  <h2 class="year">{{y}}</h2>
  {% bibliography -f papers -q @*[year={{y}}]* %}
{% endfor %}

</div>
