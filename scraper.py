"""
Quotes Scraper Demo - автоматизація браузера з Playwright.

Відкриває https://quotes.toscrape.com/js/ (офіційний навчальний сайт з
JS-рендерингом), чекає довантаження динамічного DOM, проходить усю
пагінацію та зберігає зібрані цитати у CSV і Excel.
"""

import csv
import logging
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from openpyxl import Workbook

BASE_URL = "https://quotes.toscrape.com/js/"
OUTPUT_DIR = Path(__file__).parent / "output"
CSV_PATH = OUTPUT_DIR / "quotes.csv"
XLSX_PATH = OUTPUT_DIR / "quotes.xlsx"
LOG_PATH = Path(__file__).parent / "scraper.log"

QUOTE_SELECTOR = "div.quote"
NEXT_BUTTON_SELECTOR = "li.next > a"
NAV_TIMEOUT_MS = 15_000


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("quotes_scraper")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stdout = sys.stdout
    if hasattr(stdout, "reconfigure"):
        try:
            stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    console_handler = logging.StreamHandler(stdout)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger


@dataclass
class Quote:
    text: str
    author: str
    tags: str
    page: int


def scrape_quotes(logger: logging.Logger) -> list[Quote]:
    quotes: list[Quote] = []

    with sync_playwright() as pw:
        logger.info("Запуск headless Chromium через Playwright (CDP)...")
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_default_timeout(NAV_TIMEOUT_MS)

        try:
            page_number = 1
            logger.info("Відкриваю стартову сторінку: %s", BASE_URL)
            page.goto(BASE_URL, wait_until="domcontentloaded")

            while True:
                logger.info("Сторінка %d: чекаю рендеринг JS-контенту (div.quote)...", page_number)
                try:
                    page.wait_for_selector(QUOTE_SELECTOR, state="visible")
                except PlaywrightTimeoutError:
                    logger.error("Сторінка %d: контент не завантажився за %d мс, зупиняюсь.",
                                 page_number, NAV_TIMEOUT_MS)
                    break

                quote_elements = page.query_selector_all(QUOTE_SELECTOR)
                logger.info("Сторінка %d: знайдено %d цитат(и).", page_number, len(quote_elements))

                for element in quote_elements:
                    try:
                        text_el = element.query_selector("span.text")
                        author_el = element.query_selector("small.author")
                        tag_elements = element.query_selector_all("div.tags a.tag")

                        text = text_el.inner_text().strip() if text_el else ""
                        author = author_el.inner_text().strip() if author_el else ""
                        tags = ", ".join(t.inner_text().strip() for t in tag_elements)

                        if not text or not author:
                            logger.warning("Сторінка %d: пропущено неповний запис (text=%r, author=%r)",
                                            page_number, text, author)
                            continue

                        quotes.append(Quote(text=text, author=author, tags=tags, page=page_number))
                    except Exception as exc:
                        logger.error("Сторінка %d: помилка при розборі цитати: %s", page_number, exc)

                next_button = page.query_selector(NEXT_BUTTON_SELECTOR)
                if not next_button:
                    logger.info("Кнопку 'Next' не знайдено — це остання сторінка (%d).", page_number)
                    break

                logger.info("Сторінка %d: переходжу на наступну сторінку...", page_number)
                try:
                    next_button.click()
                    page.wait_for_load_state("networkidle")
                except PlaywrightTimeoutError:
                    logger.error("Таймаут під час переходу на сторінку %d, зупиняюсь.", page_number + 1)
                    break
                except Exception as exc:
                    logger.error("Не вдалося перейти на наступну сторінку: %s", exc)
                    break

                page_number += 1

        except Exception as exc:
            logger.exception("Неочікувана помилка під час скрейпінгу: %s", exc)
        finally:
            browser.close()
            logger.info("Браузер закрито.")

    return quotes


def save_results(quotes: list[Quote], logger: logging.Logger) -> None:
    if not quotes:
        logger.warning("Немає даних для збереження — список цитат порожній.")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["text", "author", "tags", "page"])
            writer.writeheader()
            for q in quotes:
                writer.writerow(asdict(q))
        logger.info("Збережено CSV: %s (%d рядків)", CSV_PATH, len(quotes))
    except OSError as exc:
        logger.error("Не вдалося записати CSV-файл: %s", exc)

    try:
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Quotes"
        sheet.append(["text", "author", "tags", "page"])
        for q in quotes:
            sheet.append([q.text, q.author, q.tags, q.page])
        workbook.save(XLSX_PATH)
        logger.info("Збережено Excel: %s (%d рядків)", XLSX_PATH, len(quotes))
    except Exception as exc:
        logger.error("Не вдалося записати Excel-файл: %s", exc)


def main() -> int:
    logger = setup_logging()
    logger.info("=== Старт скрейпінгу quotes.toscrape.com/js/ ===")

    quotes = scrape_quotes(logger)
    logger.info("Зібрано всього %d цитат(и) з усіх сторінок.", len(quotes))

    save_results(quotes, logger)

    logger.info("=== Завершено ===")
    return 0 if quotes else 1


if __name__ == "__main__":
    sys.exit(main())
