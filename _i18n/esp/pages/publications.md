<p>Puedes encontrar una lista actualizada en <a href="https://scholar.google.com/citations?user=4RU_vSQAAAAJ" target="_blank" rel="noopener noreferrer">Google Scholar</a>.</p>
<div class="publications">

<!-- <h2 class="year">Preprints</h2> -->
{% bibliography -f preprints %}


{%- for y in page.years %}
  <h2 class="year">{{y}}</h2>
  {% bibliography -f papers -q @*[year={{y}}]* %}
{% endfor %}

</div>
