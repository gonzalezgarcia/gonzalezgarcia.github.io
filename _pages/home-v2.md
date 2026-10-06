---
layout: home
title: home v2
permalink: /v2/
nav: false
sitemap: false
---

<section class="home-hero">
  <div class="home-hero-text">
    <p class="home-eyebrow">Cognitive neuroscience · University of Granada</p>
    <h1 class="home-name"><span class="font-weight-bold">{{ site.first_name }}</span> {{ site.last_name }}</h1>
    <p class="home-thesis">I study how a single experience can change what we see, and what we remember afterwards.</p>
    <p class="home-role">Ramón y Cajal fellow at CIMCYC, University of Granada. Principal investigator of <a href="{{ '/flare/' | relative_url }}">FLARE</a>.</p>
    <div class="paper-actions home-links">
      <a class="action-btn" href="mailto:{{ site.email | encode_email }}"><i class="fa-solid fa-envelope"></i><span class="action-label">Email</span></a>
      <a class="action-btn" href="https://scholar.google.com/citations?user={{ site.scholar_userid }}"><i class="ai ai-google-scholar"></i><span class="action-label">Google Scholar</span></a>
      <a class="action-btn" href="https://orcid.org/{{ site.orcid_id }}"><i class="ai ai-orcid"></i><span class="action-label">ORCID</span></a>
      <a class="action-btn" href="https://osf.io/{{ site.osf_id }}/"><i class="ai ai-osf"></i><span class="action-label">OSF</span></a>
      <a class="action-btn" href="https://github.com/{{ site.github_username }}"><i class="fa-brands fa-github"></i><span class="action-label">GitHub</span></a>
      <a class="action-btn" href="https://bsky.app/profile/{{ site.bluesky_url }}"><i class="fa-brands fa-bluesky"></i><span class="action-label">Bluesky</span></a>
    </div>
  </div>

  <figure class="home-demo" data-state="before">
    <button class="home-demo-frame" type="button" aria-pressed="false" aria-label="Reveal the photograph">
      <img class="home-demo-img home-demo-mooney" src="{{ '/assets/img/bee_mooney.jpg' | relative_url }}" alt="" width="800" height="800" loading="eager">
      <img class="home-demo-img home-demo-photo" src="{{ '/assets/img/bee_gray.jpg' | relative_url }}" alt="" width="800" height="800" loading="lazy">
    </button>
    <figcaption class="home-demo-caption" aria-live="polite"
      data-before="What is this?"
      data-revealed="A bee on a flower."
      data-after="Now you can't unsee it. That is one-shot perceptual learning, and it is what FLARE is about.">What is this?</figcaption>
  </figure>
</section>

<section class="home-section" id="work">
  <h2 class="home-heading">What I work on</h2>
  <div class="home-cards">
    <div class="paper-card">
      <div class="tags-row"><span class="topic-pill topic-purple">Visual Perception &amp; Perceptual Learning</span></div>
      <div class="paper-main">
        <span class="paper-title">One-shot perceptual learning</span>
        <span class="paper-venue">A single disambiguating exposure can turn an unrecognisable image into an obvious one. What does the prior it leaves behind contain?</span>
        <div class="paper-actions"><a class="action-btn" href="{{ '/flare/' | relative_url }}"><span class="action-label">About FLARE</span><i class="fa-solid fa-arrow-right"></i></a></div>
      </div>
    </div>
    <div class="paper-card">
      <div class="tags-row"><span class="topic-pill topic-green">Memory</span></div>
      <div class="paper-main">
        <span class="paper-title">From insight to memory</span>
        <span class="paper-venue">Moments of sudden understanding are encoded in seconds yet leave enduring traces. Which memory formats do they take, and what does the hippocampus add?</span>
        <div class="paper-actions"><a class="action-btn" href="{{ '/papers/' | relative_url }}"><span class="action-label">Related papers</span><i class="fa-solid fa-arrow-right"></i></a></div>
      </div>
    </div>
    <div class="paper-card">
      <div class="tags-row"><span class="topic-pill topic-yellow">Instructions &amp; Task Implementation</span></div>
      <div class="paper-main">
        <span class="paper-title">Novel instructions and control</span>
        <span class="paper-venue">People can carry out a new task correctly on the first try. How does the brain turn a verbal instruction into an action-ready representation?</span>
        <div class="paper-actions"><a class="action-btn" href="{{ '/papers/' | relative_url }}"><span class="action-label">Related papers</span><i class="fa-solid fa-arrow-right"></i></a></div>
      </div>
    </div>
  </div>
</section>

<section class="home-section" id="publications">
  <h2 class="home-heading">Selected publications</h2>
  <div class="publications">
    {% bibliography -q "@*[selected=true]" -T bib_papers --group_by none %}
  </div>
  <div class="paper-actions home-more"><a class="action-btn" href="{{ '/papers/' | relative_url }}"><span class="action-label">All publications</span><i class="fa-solid fa-arrow-right"></i></a></div>
</section>

<section class="home-section" id="materials">
  <h2 class="home-heading">Open materials</h2>
  <div class="home-cards">
    {% assign featured_resources = site.data.resources | where: "featured", true %}
    {% for resource in featured_resources %}
      {% include resource_card.liquid entry=resource %}
    {% endfor %}
  </div>
  <div class="paper-actions home-more"><a class="action-btn" href="{{ '/resources/' | relative_url }}"><span class="action-label">All resources</span><i class="fa-solid fa-arrow-right"></i></a></div>
</section>

<section class="home-section" id="about">
  <h2 class="home-heading">About</h2>
  <div class="home-about">
    <img class="home-about-pic" src="{{ '/assets/img/pic2026_small.png' | relative_url }}" alt="Portrait of Carlos González-García" width="110" height="145" loading="lazy">
    <div class="home-about-text">
      <p>I trained in the Human Neuroscience Lab in Granada, with Marcel Brass in Ghent and with Biyu He at NYU. What I took from those labs is a way of working: rigorous experimental control and advanced neuroimaging, aimed at useful, tractable theories of cognition.</p>
      <p>Alongside research I write analysis software and open teaching materials, think about how to mentor well, and follow the debates where neuroscience, cognition and AI meet.</p>
    </div>
  </div>
  <p class="home-positions">No open positions at the moment. To hear about future PhD or postdoc openings, write to <a href="mailto:{{ site.email | encode_email }}">{{ site.email | encode_email }}</a>.</p>
</section>
