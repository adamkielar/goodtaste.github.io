"use strict";
document.documentElement.classList.add("js");
const content = window.siteContent;
const assetRoot = document.body.dataset.root || "./";
const menu = document.querySelector(".navigation");
const toggle = document.querySelector(".menu-toggle");
const dialog = document.querySelector(".lightbox");
let activeGallery, activeProject, returnFocus;
let activeIndex = 0;
function closeMenu() {
  toggle.setAttribute("aria-expanded", "false");
  menu.classList.remove("is-open");
}
toggle.addEventListener("click", () => {
  const open = toggle.getAttribute("aria-expanded") !== "true";
  toggle.setAttribute("aria-expanded", String(open));
  menu.classList.toggle("is-open", open);
});
menu.addEventListener("click", event => { if (event.target.closest("a")) closeMenu(); });
document.addEventListener("keydown", event => {
  if (event.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") { closeMenu(); toggle.focus(); }
});
document.addEventListener("click", event => { if (!event.target.closest(".header")) closeMenu(); });
window.matchMedia("(max-width: 680px)").addEventListener("change", closeMenu);

function placeholder(index, label = "Miejsce na zdjęcie") {
  const wrapper = document.createElement("span");
  wrapper.className = "placeholder";
  const number = document.createElement("span");
  number.className = "placeholder-number";
  number.textContent = String(index + 1).padStart(2, "0");
  const text = document.createElement("span");
  text.className = "placeholder-label";
  text.textContent = label;
  wrapper.append(number, text);
  return wrapper;
}
function projectImage(item, index, large = false) {
  if (!item.src) return placeholder(index);
  const img = document.createElement("img");
  img.src = new URL(assetRoot + (large ? (item.fullSrc || item.src) : item.src), document.baseURI).href;
  img.alt = item.alt || item.title || `Zdjęcie ${index + 1}`;
  img.loading = large ? "eager" : "lazy";
  img.decoding = "async";
  if (item.width && item.height) { img.width = item.width; img.height = item.height; }
  img.addEventListener("error", () => img.replaceWith(placeholder(index, "Zdjęcie niedostępne")), { once: true });
  return img;
}
function projectPhotos(project) {
  return project.images?.length ? project.images : [{ src: null, alt: "" }];
}
// HTML contains the complete gallery. JavaScript only adds the lightbox.
for (const link of document.querySelectorAll("[data-gallery-key]")) {
  const key = link.dataset.galleryKey;
  const project = content.galleries[key]?.projects[Number(link.dataset.projectIndex)];
  if (!project || !dialog?.showModal) continue;
  link.setAttribute("aria-haspopup", "dialog");
  link.addEventListener("click", event => {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;
    event.preventDefault();
    activeGallery = key;
    activeProject = project;
    activeIndex = Number(link.dataset.photoIndex || 0);
    returnFocus = link;
    updateLightbox();
    dialog.showModal();
    document.body.classList.add("modal-open");
    document.querySelector(".lightbox-close").focus();
  });
}
function updateLightbox() {
  const gallery = content.galleries[activeGallery];
  const photos = projectPhotos(activeProject);
  const item = photos[activeIndex];
  document.querySelector(".lightbox-media").replaceChildren(projectImage(item, activeIndex, true));
  document.querySelector("#lightbox-title").textContent = activeProject.title + (item.title ? ` — ${item.title}` : "") + (item.src ? "" : " — zdjęcie wkrótce");
  document.querySelector("#lightbox-category").textContent = gallery.label;
  document.querySelector(".lightbox-counter").textContent = `${activeIndex + 1} / ${photos.length}`;
  document.querySelectorAll(".lightbox-arrow").forEach(button => { button.disabled = photos.length < 2; });
}
function moveImage(direction) {
  const count = projectPhotos(activeProject).length;
  activeIndex = (activeIndex + direction + count) % count;
  updateLightbox();
}
document.querySelector(".lightbox-close").addEventListener("click", () => dialog.close());
document.querySelector(".lightbox-prev").addEventListener("click", () => moveImage(-1));
document.querySelector(".lightbox-next").addEventListener("click", () => moveImage(1));
dialog.addEventListener("keydown", event => {
  if (event.key === "ArrowRight" || event.key === "ArrowLeft") {
    event.preventDefault();
    moveImage(event.key === "ArrowRight" ? 1 : -1);
  }
});
dialog.addEventListener("close", () => {
  document.body.classList.remove("modal-open");
  document.querySelector(".lightbox-media").replaceChildren();
  returnFocus?.focus({ preventScroll: true });
});
dialog.addEventListener("click", event => {
  if (event.target === dialog || event.target.classList.contains("lightbox-stage")) dialog.close();
});
// One value updates every occurrence in the header, contact panel, and footer.
function contactLinks(selector, href, label, external = false) {
  document.querySelectorAll(selector).forEach(placeholder => {
    const link = document.createElement("a");
    link.className = placeholder.className;
    link.href = href;
    const icon = placeholder.classList.contains("facebook-button");
    link.textContent = icon ? "f" : label;
    if (external) {
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.setAttribute("aria-label", `${label} — otwiera się w nowej karcie`);
    }
    placeholder.replaceWith(link);
  });
}
if (content.email) contactLinks("[data-email]", `mailto:${content.email}`, content.email);
if (content.phone) contactLinks("[data-phone]", `tel:${content.phone.replace(/[^+\d]/g, "")}`, content.phone);
if (/^https:\/\//i.test(content.facebook)) contactLinks("[data-facebook]", content.facebook, "Facebook", true);
document.querySelector("#year").textContent = new Date().getFullYear();
// Match actual page URLs; navigation now includes service pages, not only anchors.
for (const link of menu.querySelectorAll("a")) {
  const target = new URL(link.href);
  const current = target.pathname === location.pathname && !target.hash;
  link.classList.toggle("is-active", current);
  if (current) link.setAttribute("aria-current", "page");
  else link.removeAttribute("aria-current");
}
// Keep anchor destinations below the actual header after logo loading and resizing.
new ResizeObserver(() => {
  if (toggle.getAttribute("aria-expanded") !== "true") {
    document.documentElement.style.setProperty("--header-height", `${document.querySelector(".header").offsetHeight}px`);
  }
}).observe(document.querySelector(".header"));
