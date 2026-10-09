// Każdy projekt ma własną tablicę images. Strzałki nigdy nie zmieniają projektu.
// src: null to oznaczone miejsce na przyszłe zdjęcie.
// cover: opcjonalna miniatura; domyślnie pierwsze zdjęcie projektu.
// fullSrc: opcjonalny większy plik zdjęcia do lightboxa.
window.siteContent = {
  email: "",
  phone: "", // np. +48 123 456 789; pusty wpis pokazuje placeholder
  facebook: "", // pełny adres https://www.facebook.com/...
  galleries: {
    technologiczne: {
      label: "Projekty technologiczne",
      projects: [
        { title: "Projekt 01", images: [{ src: null, alt: "" }, { src: null, alt: "" }, { src: null, alt: "" }] },
        { title: "Projekt 02", images: [{ src: null, alt: "" }, { src: null, alt: "" }] },
        { title: "Projekt 03", images: [{ src: null, alt: "" }] }
      ]
    },
    mieszkania: {
      label: "Projekty mieszkań",
      projects: [
        { title: "Projekt 01", images: [{ src: null, alt: "" }, { src: null, alt: "" }, { src: null, alt: "" }] },
        { title: "Projekt 02", images: [{ src: null, alt: "" }, { src: null, alt: "" }] },
        { title: "Projekt 03", images: [{ src: null, alt: "" }] }
      ]
    }
  }
};
