# Quotes Scraper Demo (Playwright)

## Українською

Демонстраційний Python-інструмент для автоматизації браузера, який показує роботу
з **динамічними JS-сторінками** (а не просто `requests` + `BeautifulSoup`).

Скрипт:
- запускає headless Chromium через **Playwright** (сучасна альтернатива Selenium,
  працює через Chrome DevTools Protocol);
- відкриває тестовий сайт [quotes.toscrape.com/js/](https://quotes.toscrape.com/js/)
  (офіційний сайт для тренування скрейперів, контент рендериться JavaScript'ом);
- коректно чекає, поки JS довантажить цитати в DOM (`wait_for_selector`);
- автоматично проходить усю пагінацію (натискає кнопку "Next", доки вона є);
- збирає текст цитати, автора і теги;
- зберігає результат у **CSV** (`output/quotes.csv`) та **Excel** (`output/quotes.xlsx`);
- веде детальний лог кожного кроку і всіх помилок у `scraper.log`.

### Встановлення

```powershell
# створити й активувати віртуальне середовище (рекомендовано)
python -m venv venv
venv\Scripts\activate

# встановити залежності
pip install -r requirements.txt

# завантажити браузер Chromium для Playwright (один раз)
playwright install chromium
```

### Запуск

```powershell
python scraper.py
```

Після завершення результати будуть у папці `output/`, а повний лог роботи — у
файлі `scraper.log`.

### Структура проєкту

```
scraper_demo/
├── scraper.py          # основний скрипт
├── requirements.txt    # залежності
├── README.md
├── scraper.log         # лог останнього запуску (генерується)
└── output/
    ├── quotes.csv
    └── quotes.xlsx
```

---

## English (simple)

A small demo Python tool for browser automation that shows how to handle
**dynamic, JavaScript-rendered pages** (not just `requests` + `BeautifulSoup`).

The script:
- launches a headless Chromium browser via **Playwright** (a modern alternative
  to Selenium, built on the Chrome DevTools Protocol);
- opens the test site [quotes.toscrape.com/js/](https://quotes.toscrape.com/js/)
  (an official scraping-practice site where content is rendered by JavaScript);
- waits properly for the JS to load quotes into the DOM (`wait_for_selector`);
- automatically follows pagination (clicks "Next" until it disappears);
- collects quote text, author and tags;
- saves the results to **CSV** (`output/quotes.csv`) and **Excel** (`output/quotes.xlsx`);
- logs every step and any errors to `scraper.log`.

### Install

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
```

### Run

```powershell
python scraper.py
```

Results are written to the `output/` folder; the full run log is in `scraper.log`.
