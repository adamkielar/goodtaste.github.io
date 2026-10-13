# Good Taste

Polskie portfolio Good Taste: projektowanie wnętrz i projekty technologiczne gastronomii, z naciskiem na Wrocław i Dolny Śląsk. Statyczny HTML, CSS i JavaScript, bez zależności npm. GitHub Pages publikuje gotowe pliki z repozytorium.

## Podgląd lokalny

```sh
python3 -m http.server 8080
```

Otwórz `http://localhost:8080/`. Wszystkie podstrony, galerie i linki działają również pod prefiksem repozytorium.

## Edycja i generowanie

Źródła treści:

- `assets/content.js`: dane kontaktowe, dziesięć projektów, opisy i 53 obrazy. Format po `window.siteContent =` musi pozostać poprawnym JSON-em.
- `site.json`: docelowy publiczny adres HTTPS wskazany przez właściciela: `https://goodtaste.net.pl/`.
- `templates/home.html`: strona główna, sekcje O Nas i Oferta (układ O Nas na podstawie Hazel Demo 1 / About Version 1).
- `templates/interiors.html` i `templates/gastronomy.html`: strony oferty, bez galerii.
- `templates/portfolio.html`: osobne galerie dla projektów wnętrz i projektów technologicznych. Nawigacja Oferta / Portfolio prowadzi do różnych podstron.
- `templates/base.html`: wspólna nawigacja, kontakt, stopka i lightbox.
- `assets/styles.css` i `assets/main.js`: wygląd oraz interakcje.

Po zmianie treści lub adresu uruchom:

```sh
python3 scripts/build_site.py
python3 scripts/check_site.py
```

Generator korzysta wyłącznie ze standardowej biblioteki Pythona 3.10+. Wygenerowane pliki `index.html`, katalogi stron usług i projektów, `sitemap.xml` oraz `robots.txt` należy zapisać w repozytorium razem ze źródłami. Nie edytuj wygenerowanego HTML ręcznie: kolejne uruchomienie zastąpi zmiany.

Kontrola bez zapisywania plików:

```sh
python3 scripts/build_site.py --check
python3 scripts/check_site.py
node --check assets/main.js
```

Python jest potrzebny tylko przy aktualizacji treści; hosting nie uruchamia generatora. `.nojekyll` wyłącza przetwarzanie przez Jekyll.

## Projekty i obrazy

Każdy projekt ma `title`, unikalny `slug`, `subtitle`, `description`, `cover` oraz niepustą tablicę `images`. Każdy obraz ma lokalny `src`, opisowy `alt`, `width` i `height`. Pole `source` wskazuje wybrany plik w folderze źródłowym, jeśli folder zawiera alternatywne eksporty tego samego ujęcia. Zachowaj istniejące slugi, aby nie zmieniać opublikowanych adresów.

Kliknięcie miniatury, tytułu projektu lub linku „Zobacz galerię” prowadzi do stałej podstrony ze wszystkimi obrazami. Dopiero kliknięcie pojedynczego obrazu otwiera lightbox. Galerie nie zawierają widocznych podpisów zdjęć ani dodatkowych opisów SEO; zachowują opisy alternatywne obrazów. Bez JavaScript karty również prowadzą do podstron, a kliknięcie obrazu otwiera plik WebP. Każda strona ma własny tytuł, opis metadanych, adres kanoniczny i dane JSON-LD.

Obrazy pochodzą z dostarczonych materiałów. Wizualizacje nie są opisywane jako fotografie ukończonych realizacji. Galeria korzysta z WebP do 2000 px, miniatur do 800 px i ładowania odroczonego. Oryginały pozostają poza repozytorium. Nowe galerie zawierają 13 różnych ujęć (Dom w centrum: 7, Dom w Krzyżanowie: 4, Biuro: 2); ich obrazy i miniatury zajmują 2,16 MB zamiast 68,45 MB źródeł. Alternatywne eksporty pominięto, oryginały zachowano. Wybrane galerie można przetworzyć z `--project dom-w-centrum --project dom-w-krzyzanowie --project biuro`. Opcjonalne ponowne przetworzenie zdjęć: `python3 scripts/optimize_images.py` w środowisku z Pillow i obsługą WebP; potem uruchom generator stron.

## Kontakt i publikacja

Dane kontaktowe (`email`, `phone` i `facebook`) edytuj w `assets/content.js`, następnie wygeneruj strony. Dane będą dostępne w HTML także bez JavaScript. Puste wartości pozostawiają dotychczasowe komunikaty „wkrótce”; nie dodano fikcyjnych danych firmy.

W GitHub Pages: **Settings → Pages → Deploy from a branch → main → /(root)**. Publikuj tylko zawartość tego repozytorium. Nie dołączaj folderów materiałów źródłowych ani archiwum motywu WordPress.

Strona jest przygotowana do przeniesienia na `https://goodtaste.net.pl/`. Adresy kanoniczne, metadane społecznościowe, JSON-LD i mapa witryny wskazują już tę domenę. Samo ustawienie URL nie zmienia DNS, hostingu ani przekierowań. Konfigurację domeny w hostingu wykonaj podczas przenoszenia strony; jeżeli pozostanie na GitHub Pages, ustaw tam domenę niestandardową.

Po przeniesieniu opublikuj zawartość repozytorium w katalogu głównym domeny. Sprawdź `https://goodtaste.net.pl/robots.txt` i zgłoś `https://goodtaste.net.pl/sitemap.xml` w Search Console. Skonfiguruj przekierowania ze starych adresów na odpowiadające im podstrony nowej domeny. Względne linki do stron i zasobów nadal pozwalają korzystać z lokalnego podglądu.

Badania, mapa fraz, ograniczenia i plan lokalnego SEO: [SEO_RESEARCH.md](SEO_RESEARCH.md).

## Zasady treści

Tekst O Nas i oferty odtwarza brzmienie `../Good taste/opis.docx`; nie parafrazuj ani nie dopisuj treści. Zmieniać można układ i formatowanie. Strona Start nie zawiera widocznej sekcji SEO. Na pozostałych stronach dodatkowe treści SEO umieszczaj wyłącznie w dolnym polu `seo` generatora, po kontakcie i przed stopką. Wstępy SEO usług znajdują się w `templates/*-seo.html`.
