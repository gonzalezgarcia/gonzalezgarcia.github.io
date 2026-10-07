// Landing page: on narrow screens the portrait is hidden until the visitor asks for it.
document.addEventListener("DOMContentLoaded", function () {
  const toggle = document.querySelector(".about-photo-toggle");
  if (!toggle) return;
  const side = toggle.closest(".about-side");
  const label = toggle.querySelector(".action-label");

  toggle.addEventListener("click", function () {
    const open = side.classList.toggle("photo-open");
    toggle.setAttribute("aria-expanded", String(open));
    label.textContent = open ? "Hide photo" : "Show photo";
  });
});
