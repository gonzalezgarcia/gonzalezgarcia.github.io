document.addEventListener("DOMContentLoaded", function () {
  const container = document.getElementById("resourceslist");
  if (!container) return;

  const cards = Array.from(container.querySelectorAll(".paper-card"));
  const searchInput = document.getElementById("resources-search");
  const limitSelect = document.getElementById("resources-limit");
  const activeTopicBar = document.getElementById("resources-active-topic");

  let activeType = null; // from the "Limit to" select (course/guide/dataset category)
  let activeTopic = null; // from clicking a topic pill

  // ---- cite toggle + copy-to-clipboard + topic-pill filter (event delegation) ----
  container.addEventListener("click", function (e) {
    const bibtexBtn = e.target.closest(".bibtex-toggle");
    const copyBtn = e.target.closest(".copy-bibtex-btn");
    const topicPill = e.target.closest("[data-topic-filter]");

    if (bibtexBtn) {
      const card = bibtexBtn.closest(".paper-card");
      const bibtexEl = card.querySelector(".paper-bibtex");
      if (bibtexEl) bibtexEl.classList.toggle("open");
    } else if (copyBtn) {
      const pre = copyBtn.parentElement.querySelector(".bibtex-pre");
      const text = pre ? pre.innerText : "";
      navigator.clipboard.writeText(text).then(() => {
        const label = copyBtn.querySelector(".copy-label");
        const original = label.textContent;
        label.textContent = "Copied!";
        setTimeout(() => (label.textContent = original), 1500);
      });
    } else if (topicPill) {
      e.preventDefault();
      const topic = topicPill.dataset.topicFilter;
      activeTopic = activeTopic === topic ? null : topic;
      applyFilters();
    }
  });

  if (activeTopicBar) {
    activeTopicBar.addEventListener("click", function (e) {
      if (e.target.closest(".clear-topic")) {
        activeTopic = null;
        applyFilters();
      }
    });
  }

  function matchesType(card) {
    if (!activeType) return true;
    return card.dataset.type === activeType;
  }

  function matchesTopic(card) {
    if (!activeTopic) return true;
    return (card.dataset.topics || "").split("|").filter(Boolean).includes(activeTopic);
  }

  function matchesSearch(card, term) {
    if (!term) return true;
    return (card.dataset.search || "").toLowerCase().includes(term);
  }

  function applyFilters() {
    const term = searchInput ? searchInput.value.trim().toLowerCase() : "";

    cards.forEach((card) => {
      const visible = matchesType(card) && matchesTopic(card) && matchesSearch(card, term);
      card.classList.toggle("filtered-out", !visible);
    });

    // hide a type-group heading (h2.bibliography) once every card under it is filtered out
    container.querySelectorAll("h2.bibliography").forEach((heading) => {
      let node = heading.nextElementSibling;
      let hasVisible = false;
      while (node && !(node.tagName === "H2" && node.classList.contains("bibliography"))) {
        if (node.classList.contains("paper-card") && !node.classList.contains("filtered-out")) {
          hasVisible = true;
          break;
        }
        node = node.nextElementSibling;
      }
      heading.classList.toggle("filtered-out", !hasVisible);
    });

    if (activeTopicBar) {
      if (activeTopic) {
        activeTopicBar.hidden = false;
        activeTopicBar.querySelector(".active-topic-name").textContent = activeTopic;
      } else {
        activeTopicBar.hidden = true;
      }
    }

    container.querySelectorAll("[data-topic-filter]").forEach((pill) => {
      pill.classList.toggle("active", pill.dataset.topicFilter === activeTopic);
    });
  }

  let debounceId;
  if (searchInput) {
    searchInput.addEventListener("input", function () {
      clearTimeout(debounceId);
      debounceId = setTimeout(applyFilters, 200);
    });
  }
  if (limitSelect) {
    limitSelect.addEventListener("change", function () {
      activeType = limitSelect.value === "all" ? null : limitSelect.value;
      applyFilters();
    });
  }

  applyFilters();
});
