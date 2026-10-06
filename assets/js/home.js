document.addEventListener("DOMContentLoaded", function () {
  const root = document.querySelector(".home-v2");
  if (!root) return;

  // ---- Mooney demo: click toggles; hover also reveals on devices that have it ----
  const demo = root.querySelector(".home-demo");
  if (demo) {
    const frame = demo.querySelector(".home-demo-frame");
    const caption = demo.querySelector(".home-demo-caption");
    const canHover = window.matchMedia("(hover: hover)").matches;
    let pinned = false;
    let hovering = false;
    let suppressHover = false; // set when the user clicks the photo away while hovering
    let seen = false;

    function render() {
      const shown = pinned || (hovering && !suppressHover);
      frame.classList.toggle("is-photo", shown);
      frame.setAttribute("aria-pressed", String(pinned));
      frame.setAttribute("aria-label", shown ? "Back to the two-tone image" : "Reveal the photograph");
      if (shown) seen = true;
      const state = shown ? "revealed" : seen ? "after" : "before";
      demo.dataset.state = state;
      caption.textContent = caption.dataset[state];
    }

    frame.addEventListener("click", function () {
      if (pinned) {
        pinned = false;
        suppressHover = true;
      } else {
        pinned = true;
        suppressHover = false;
      }
      render();
    });

    if (canHover) {
      frame.addEventListener("mouseenter", function () {
        hovering = true;
        render();
      });
      frame.addEventListener("mouseleave", function () {
        hovering = false;
        suppressHover = false;
        render();
      });
    }
  }

  // ---- paper/resource cards: Abstract, Cite and Copy (same behaviour as /papers/) ----
  root.addEventListener("click", function (e) {
    const abstractBtn = e.target.closest(".abstract-toggle");
    const bibtexBtn = e.target.closest(".bibtex-toggle");
    const copyBtn = e.target.closest(".copy-bibtex-btn");

    if (abstractBtn) {
      const el = abstractBtn.closest(".paper-card").querySelector(".paper-abstract");
      if (el) el.classList.toggle("open");
    } else if (bibtexBtn) {
      const el = bibtexBtn.closest(".paper-card").querySelector(".paper-bibtex");
      if (el) el.classList.toggle("open");
    } else if (copyBtn) {
      const pre = copyBtn.parentElement.querySelector(".bibtex-pre");
      navigator.clipboard.writeText(pre ? pre.innerText : "").then(() => {
        const label = copyBtn.querySelector(".copy-label");
        const original = label.textContent;
        label.textContent = "Copied!";
        setTimeout(() => (label.textContent = original), 1500);
      });
    } else if (e.target.closest("[data-topic-filter]")) {
      // topic pills filter on /papers/ and /resources/; here they are just labels
      e.preventDefault();
    }
  });
});
