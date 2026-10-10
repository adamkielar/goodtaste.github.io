# Good Taste

Polskie portfolio w HTML, CSS i JavaScript. Bez instalacji zależności i bez kompilacji.

## Podgląd lokalny

Uruchom `python3 -m http.server 8080` w katalogu repozytorium i otwórz http://localhost:8080.

## Treść i zdjęcia

Edytuj `assets/content.js`. Dodano 40 zdjęć w 7 projektach: 2 technologicznych i 5 mieszkalnych. Każda z dwóch kategorii ma tablicę `projects`. Każdy projekt ma własną tablicę `images`: kliknięcie jego miniatury otwiera tylko te zdjęcia. Strzałki przewijają zdjęcia w obrębie projektu i wracają do początku po ostatnim zdjęciu. Dla pojedynczego zdjęcia są ukryte.

Pliki pochodzą z siedmiu nazwanych folderów w `../good taste`. Zachowano kolejność liczbową nazw źródłowych; pierwsze zdjęcie jest okładką. W repozytorium mają proste ścieżki bez spacji i polskich znaków. Oryginały pozostają niezmienione poza repozytorium. Wszystkie obrazy strony zajmują teraz około 6,75 MB zamiast 232,77 MB — szczegóły w `IMAGE_AUDIT.md`.

Galerie używają WebP do 2000 px na dłuższym boku. Siatka pobiera osobne miniatury do 800 px, wskazane w polu `cover`. Zdjęcia w lightboxie pobierane są dopiero po otwarciu. Mniejsze oryginały nie są powiększane. Aby ponownie wygenerować grafiki z folderów źródłowych, uruchom `python3 scripts/optimize_images.py` w środowisku z Pillow i obsługą WebP. Liczba zdjęć w konfiguracji musi odpowiadać liczbie plików w folderze danego projektu.

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
4. Logo w nagłówku i stopce to `assets/images/logo.png`. Ikona karty to `assets/images/GT_znak.png`. Oba pliki pochodzą z dostarczonych grafik.

Obraz otwierający stronę to lokalnie zoptymalizowany `assets/images/showcase.webp`, o wymiarach 2400 × 960. Logo ma 600 × 256 px, a favicon 48 × 48 px. Zachowano proporcje, kolory, przezroczystość logo i osadzone znaki na zdjęciach. WebP używa kompresji stratnej; pliki źródłowe pozostają niezmienione.

Interfejs jest czarno-biały. Zdjęcie główne zachowuje oryginalne kolory. Sekcja Kontakt używa tymczasowo tego samego zdjęcia jako tła, w skali szarości z ciemną nakładką CSS. Własne zdjęcie kontaktowe można podstawić w regule `.contact::before` w `assets/styles.css`. Przesłane zrzuty Hazel są referencją układu, nie grafiką z wtopionym tekstem na stronie.

Na komputerze przyciski na obrazie pojawiają się po najechaniu lub ustawieniu fokusu klawiaturą. Na urządzeniach dotykowych są widoczne stale, a na małym ekranie znajdują się bezpośrednio pod odpowiednimi połowami obrazu, żeby nie zasłaniać wnętrz.

## GitHub Pages

Po dodaniu plików do gałęzi `main` w GitHub wybierz **Settings → Pages → Deploy from a branch → main → /(root)**. Pusty plik `.nojekyll` wyłącza przetwarzanie przez Jekyll. Nie potrzeba własnego workflow ani pakietów npm.

Linki do zasobów są względne, więc działają również pod adresem projektu z prefiksem repozytorium. Ostateczny adres strony wyświetli GitHub w ustawieniach Pages.

Publikuj tylko zawartość tego repozytorium. Archiwum motywu WordPress Hazel pozostaje poza nim.

Przed publikacją: uzupełnij e-mail, telefon i Facebook oraz sprawdź teksty. Nie skonfigurowano analityki, formularzy ani zewnętrznych fontów.
