import time
import json
import logging
from urllib.parse import urljoin

from inscriptis import get_text
from lxml import html as LH
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright
from rq import get_current_job


def get_html(url: str) -> str:
    html_content = None
    logging.getLogger(__name__).error("########################START")
    with sync_playwright() as p:
        browser = None
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            page.goto(url, wait_until="networkidle", timeout=8000)
        except PlaywrightTimeoutError:
            page.goto(url, wait_until="domcontentloaded", timeout=8000)
        except Exception:
            # log Exception
            raise

        page.wait_for_timeout(2000)
        html_content = page.content()

        if browser:
            browser.close()

    return html_content


def clean_html(html: str, base_url: str | None = None):
    doc = LH.fromstring(html, base_url=base_url)
    base = doc.base_url

    for img in doc.xpath("//img"):
        src = img.get("src") or ""
        if src == "":
            continue
        if base:
            src = urljoin(base, src)
        alt = (img.get("alt") or "").strip().replace('"', '\\"')
        marker = f'[IMAGE alt="{alt}" src="{src}"]'
        # Replace the <img> with a simple inline text node
        parent = img.getparent()
        i = parent.index(img)
        parent.remove(img)
        parent.insert(i, LH.fromstring(f"<span>{marker}</span>"))

    return get_text(LH.tostring(doc, encoding="unicode"))


def get_cleaned_html(url: str, events_id: str | None = None):
    time.sleep(2)
    return "CLEANED HTML"
