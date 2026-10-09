# Good Taste

Polskie portfolio w HTML, CSS i JavaScript. Bez instalacji zależności i bez kompilacji.

## Podgląd lokalny

Uruchom `python3 -m http.server 8080` w katalogu repozytorium i otwórz http://localhost:8080.

## Treść i zdjęcia

Edytuj `assets/content.js`. Każda z dwóch kategorii ma tablicę `projects`. Każdy projekt ma własną tablicę `images`: kliknięcie jego miniatury otwiera tylko te zdjęcia. Strzałki przewijają zdjęcia w obrębie projektu i wracają do początku po ostatnim zdjęciu. Dla pojedynczego zdjęcia są ukryte. Można dodać 20–30 lub więcej zdjęć, rozdzielając je między projekty.

1. Umieść zdjęcia w `assets/images/portfolio/`.
2. Uzupełnij projekty i zastąp wpisy z `src: null` własnymi zdjęciami:

```js
{
  title: "Mieszkanie — Warszawa",
  // Opcjonalnie cover: "assets/images/portfolio/miniatura.jpg",
  // Bez cover miniaturą jest pierwsze zdjęcie.
  images: [
    {
      src: "assets/images/portfolio/kuchnia.jpg",
      fullSrc: "assets/images/portfolio/kuchnia-duza.jpg", // opcjonalne
      title: "Kuchnia", // opcjonalny podpis zdjęcia
      alt: "Jasna kuchnia z drewnianą zabudową i kamienną wyspą"
    },
    { src: "assets/images/portfolio/salon.jpg", alt: "Salon z dużymi oknami" }
  ]
}
```

3. W tym samym pliku uzupełnij `email`, `phone` i `facebook` (pełny adres HTTPS). Te dane aktualizują nagłówek, sekcję Kontakt i stopkę. Numer telefonu staje się linkiem `tel:`, a e-mail linkiem `mailto:`. Puste dane wyświetlają placeholder, bez fikcyjnych linków. Facebook to jedyny serwis społecznościowy.
4. Tymczasowy znak tekstowy znajduje się w nagłówku i stopce `index.html`. Zastąp go swoim logo. Ikona karty jest również tymczasowa.

Obraz otwierający stronę jest oryginalnym plikiem dostarczonym przez właściciela (około 5,4 MB). Przed publikacją warto przygotować jego lżejszą wersję WebP/AVIF. Nie zmieniono obrazu ani nie usunięto osadzonego logo.

Interfejs jest czarno-biały. Zdjęcie główne zachowuje oryginalne kolory. Sekcja Kontakt używa tymczasowo tego samego zdjęcia jako tła, w skali szarości z ciemną nakładką CSS. Własne zdjęcie kontaktowe można podstawić w regule `.contact::before` w `assets/styles.css`. Przesłane zrzuty Hazel są referencją układu, nie grafiką z wtopionym tekstem na stronie.

Na komputerze przyciski na obrazie pojawiają się po najechaniu lub ustawieniu fokusu klawiaturą. Na urządzeniach dotykowych są widoczne stale, a na małym ekranie znajdują się bezpośrednio pod odpowiednimi połowami obrazu, żeby nie zasłaniać wnętrz.

## GitHub Pages

Po dodaniu plików do gałęzi `main` w GitHub wybierz **Settings → Pages → Deploy from a branch → main → /(root)**. Pusty plik `.nojekyll` wyłącza przetwarzanie przez Jekyll. Nie potrzeba własnego workflow ani pakietów npm.

Linki do zasobów są względne, więc działają również pod adresem projektu z prefiksem repozytorium. Ostateczny adres strony wyświetli GitHub w ustawieniach Pages.

Publikuj tylko zawartość tego repozytorium. Archiwum motywu WordPress Hazel pozostaje poza nim.

Przed publikacją: dodaj właściwe zdjęcia, logo, e-mail i profile społecznościowe oraz sprawdź teksty. Nie skonfigurowano analityki, formularzy ani zewnętrznych fontów.
