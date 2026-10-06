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
