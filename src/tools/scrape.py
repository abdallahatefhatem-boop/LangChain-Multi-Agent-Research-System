import os
import re
import sys
import requests
import trafilatura
from bs4 import BeautifulSoup
from readability import Document
from ensure import ensure_annotations
from langchain.tools import tool
from src.logger import logging
from src.exception import multi_agent


@tool
@ensure_annotations
def scrape_url(url: str) -> str:
    """
    Scrape and extract clean readable content from a URL using multiple fallback strategies.
    """
    try:
        logging.info(f"Starting URL scraping for: {url}")

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
        }

        # ── Fetch page ─────────────────────────────────────
        try:
            logging.info("Sending GET request to target URL...")
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            html = response.text
        except requests.exceptions.Timeout:
            logging.warning(f"Timeout occurred while scraping: {url}")
            return "Request timed out while scraping the URL."
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP error occurred while scraping {url}: {str(e)}")
            return f"HTTP error occurred: {str(e)}"
        except Exception as e:
            logging.error(f"Failed to fetch content from {url}: {str(e)}")
            return f"Could not scrape URL: {str(e)}"

        # ──────────────────────────────────────────────────
        # Strategy 1 → trafilatura (BEST for articles/blogs)
        # ──────────────────────────────────────────────────
        logging.info("Attempting Strategy 1: Trafilatura extraction...")
        extracted = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=False
        )

        if extracted and len(extracted.strip()) > 200:
            logging.info("Successfully extracted content using Trafilatura.")
            cleaned = re.sub(r'\s+', ' ', extracted)
            return cleaned[:5000]

        # ──────────────────────────────────────────────────
        # Strategy 2 → readability
        # ──────────────────────────────────────────────────
        logging.info("Strategy 1 insufficient. Attempting Strategy 2: Readability...")
        doc = Document(html)
        clean_html = doc.summary()
        soup = BeautifulSoup(clean_html, "html.parser")

        for tag in soup([
            "script", "style", "nav", "footer", "header", "aside", "form"
        ]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        if text and len(text.strip()) > 200:
            logging.info("Successfully extracted content using Readability.")
            cleaned = re.sub(r'\s+', ' ', text)
            return cleaned[:5000]

        # ──────────────────────────────────────────────────
        # Strategy 3 → fallback full page extraction
        # ──────────────────────────────────────────────────
        logging.info("Strategy 2 insufficient. Attempting Strategy 3: BeautifulSoup Fallback...")
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup([
            "script", "style", "nav", "footer", "header", "aside", "form"
        ]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        cleaned = re.sub(r'\s+', ' ', text)

        if cleaned:
            logging.info("Successfully extracted content using BeautifulSoup Fallback.")
            return cleaned[:5000]

        logging.warning("Failed to extract meaningful content using all strategies.")
        return "Could not extract meaningful content from the page."

    except Exception as e:
        logging.debug("Error occurred inside scrape_url tool execution.")
        raise multi_agent(e, sys)

scrape_url(" https://www.mtu.edu/data-science/undergraduate/ai/what-is")