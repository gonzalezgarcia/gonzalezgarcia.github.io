document.addEventListener("DOMContentLoaded", function () {
  const container = document.querySelector(".paperslist");
  if (!container) return;

  const cards = Array.from(container.querySelectorAll(".paper-card"));
  const searchInput = document.getElementById("papers-search");
  const limitSelect = document.getElementById("papers-limit");
  const sortSelect = document.getElementById("papers-sort");
  const activeTopicBar = document.getElementById("papers-active-topic");

  let activeTopic = null;

  // ---- abstract / bibtex toggles + copy-to-clipboard (event delegation) ----
  container.addEventListener("click", function (e) {
    const abstractBtn = e.target.closest(".abstract-toggle");
    const bibtexBtn = e.target.closest(".bibtex-toggle");
    const copyBtn = e.target.closest(".copy-bibtex-btn");
    const topicPill = e.target.closest("[data-topic-filter]");

    if (abstractBtn) {
      const card = abstractBtn.closest(".paper-card");
      card.querySelector(".paper-abstract")?.classList.toggle("open");
    } else if (bibtexBtn) {
      const card = bibtexBtn.closest(".paper-card");
      card.querySelector(".paper-bibtex")?.classList.toggle("open");
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

  function clearActiveTopic() {
    activeTopic = null;
    applyFilters();
  }
  if (activeTopicBar) {
    activeTopicBar.addEventListener("click", function (e) {
      if (e.target.closest(".clear-topic")) clearActiveTopic();
    });
  }

  function matchesLimit(card, limit) {
    switch (limit) {
      case "published":
        return card.dataset.type !== "preprint";
      case "preprints":
        return card.dataset.type === "preprint";
      default:
        return true;
    }
  }

  function matchesTopic(card) {
    if (!activeTopic) return true;
    const topics = (card.dataset.topics || "").split("|").filter(Boolean);
    return topics.includes(activeTopic);
  }

  function matchesSearch(card, term) {
    if (!term) return true;
    return (card.dataset.search || "").toLowerCase().includes(term);
  }

  function applyFilters() {
    const term = searchInput ? searchInput.value.trim().toLowerCase() : "";
    const limit = limitSelect ? limitSelect.value : "all";

    cards.forEach((card) => {
      const visible = matchesLimit(card, limit) && matchesTopic(card) && matchesSearch(card, term);
      card.classList.toggle("filtered-out", !visible);
    });

    // hide year headers (h2.bibliography) whose following <ol> has no visible entries left
    container.querySelectorAll("h2.bibliography").forEach((heading) => {
      const ol = heading.nextElementSibling;
      if (!ol || ol.tagName !== "OL") return;
      const visibleInGroup = ol.querySelectorAll(".paper-card:not(.filtered-out)").length;
      heading.classList.toggle("filtered-out", visibleInGroup === 0);
      ol.classList.toggle("filtered-out", visibleInGroup === 0);
    });

    if (activeTopicBar) {
      if (activeTopic) {
        activeTopicBar.hidden = false;
        activeTopicBar.querySelector(".active-topic-name").textContent = activeTopic;
      } else {
        activeTopicBar.hidden = true;
      }
    }

    // pressed state on topic pills
    container.querySelectorAll("[data-topic-filter]").forEach((pill) => {
      pill.classList.toggle("active", pill.dataset.topicFilter === activeTopic);
    });
  }

  // Capture year-group pairs (h2.bibliography + following ol.bibliography) in their
  // original (descending) order, once, so ascending/descending can be replayed cheaply.
  const yearGroupsDescending = [];
  container.querySelectorAll("h2.bibliography").forEach((heading) => {
    const ol = heading.nextElementSibling;
    if (ol && ol.tagName === "OL") yearGroupsDescending.push([heading, ol]);
  });

  function applySort() {
    if (!sortSelect) return;
    const parent = yearGroupsDescending.length ? yearGroupsDescending[0][0].parentElement : null;
    if (!parent) return;
    const ordered = sortSelect.value === "year_asc" ? yearGroupsDescending.slice().reverse() : yearGroupsDescending;
    ordered.forEach(([heading, ol]) => {
      parent.appendChild(heading);
      parent.appendChild(ol);
    });
  }

  let debounceId;
  if (searchInput) {
    searchInput.addEventListener("input", function () {
      clearTimeout(debounceId);
      debounceId = setTimeout(applyFilters, 200);
    });
  }
  if (limitSelect) limitSelect.addEventListener("change", applyFilters);
  if (sortSelect) sortSelect.addEventListener("change", applySort);

  applyFilters();
});
