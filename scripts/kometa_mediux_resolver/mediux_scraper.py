"""
mediux_scraper.py

Minimal, self-contained MediUX scraper helper.

This module implements a compact MediuxScraper class used as an optional fallback
when public API endpoints do not expose set asset lists. It performs a headless
Chromium login (when credentials provided) and extracts the YAML from a set page
by finding the "YAML" button and reading the modal/textarea contents.

Design notes:
- Imports selenium only when scrape is actually used to avoid hard dependency for
  asset-only runs.
- Credentials may be provided via env vars MEDIUX_USERNAME/MEDIUX_PASSWORD/MEDIUX_NICKNAME
  or passed explicitly.
- This scraper attempts minimal robust behavior: navigate, wait for YAML button,
  click it, and read the YAML text. It returns an empty string on failure.
"""
from __future__ import annotations

import logging
import os
import re
import time
from typing import Optional, List, Dict, Set

logger = logging.getLogger(__name__)

YAML_BUTTON_XPATH = "//button[span[contains(text(), 'YAML')]]"
SIGN_IN_XPATH = "//button[contains(text(), 'Sign In')]"
USER_BUTTON_XPATH_TEMPLATE = "//button[contains(text(), '{nickname}')]"

ASSET_URL_RE = re.compile(r"https?://[\w\.\-]*/assets/([0-9a-fA-F\-]{20,})")
ASSET_REALTIVE_RE = re.compile(r"/assets/([0-9a-fA-F\-]{20,})")


class MediuxScraper:
    """Compact MediUX scraper using Selenium.

    Usage: create instance and call `scrape_set_yaml(set_url, ...)` to get YAML string.
    """

    def __init__(self):
        # lazy init logger
        self.logger = logger

    def _import_selenium(self):
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
        except Exception as e:
            raise RuntimeError("selenium is required for scraping. Install via pip: selenium") from e
        return webdriver, Options, By, WebDriverWait, EC

    def _init_driver(self, headless: bool = True, profile_path: Optional[str] = None, chromedriver_path: Optional[str] = None):
        webdriver, Options, By, WebDriverWait, EC = self._import_selenium()
        opts = Options()
        if headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        if profile_path:
            opts.add_argument(f"--user-data-dir={profile_path}")
        # minimal stability options
        opts.add_argument("--disable-gpu")
        driver = webdriver.Chrome(executable_path=chromedriver_path, options=opts) if chromedriver_path else webdriver.Chrome(options=opts)
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(3)
        return driver

    def login_if_needed(self, driver, username: Optional[str], password: Optional[str], nickname: Optional[str]):
        """Attempt to login if sign-in button is present and username/password given.

        This is intentionally conservative: if credentials are not provided or the
        sign-in button is not present, we quietly continue.
        """
        webdriver, Options, By, WebDriverWait, EC = self._import_selenium()
        # quick check for user button
        try:
            if nickname:
                user_xpath = USER_BUTTON_XPATH_TEMPLATE.format(nickname=nickname)
                elems = driver.find_elements(By.XPATH, user_xpath)
                if elems:
                    self.logger.debug("Already logged in as %s", nickname)
                    return True
        except Exception:
            pass

        if not username or not password:
            self.logger.debug("No credentials provided; skipping login attempt")
            return False

        try:
            sign_buttons = driver.find_elements(By.XPATH, SIGN_IN_XPATH)
            if not sign_buttons:
                self.logger.debug("Sign-in button not found; may already be logged in or UI changed")
                return False

            sign_buttons[0].click()
            time.sleep(1)
            # naive attempt to fill typical inputs
            email_inputs = driver.find_elements(By.XPATH, "//input[@type='email' or @name='username' or contains(@placeholder,'Email')]")
            pass_inputs = driver.find_elements(By.XPATH, "//input[@type='password' or @name='password' or contains(@placeholder,'Password')]")
            if email_inputs:
                email_inputs[0].clear()
                email_inputs[0].send_keys(username)
            if pass_inputs:
                pass_inputs[0].clear()
                pass_inputs[0].send_keys(password)

            # try to find and click submit
            submits = driver.find_elements(By.XPATH, "//button[@type='submit' or contains(text(),'Sign in') or contains(text(),'Log in')]")
            if submits:
                submits[0].click()
                time.sleep(2)

            # optionally click nickname if provided
            if nickname:
                try:
                    user_btn = driver.find_element(By.XPATH, USER_BUTTON_XPATH_TEMPLATE.format(nickname=nickname))
                    if user_btn:
                        self.logger.debug('Found user button for nickname after login')
                        return True
                except Exception:
                    pass

            self.logger.debug('Login attempt completed; caller should verify login success')
            return True
        except Exception as e:
            self.logger.warning('Login attempt failed: %s', e)
            return False

    def scrape_set_yaml(
        self,
        set_url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        nickname: Optional[str] = None,
        headless: bool = True,
        profile_path: Optional[str] = None,
        chromedriver_path: Optional[str] = None,
        timeout: int = 20,
    ) -> str:
        """Return YAML string for a given MediUX set URL or an empty string on failure.

        The function is defensive: it imports selenium only when called and cleans up
        the driver on exit. If selenium or chromedriver aren't available, it raises
        a RuntimeError with guidance.
        """
        webdriver, Options, By, WebDriverWait, EC = self._import_selenium()
        driver = None
        try:
            driver = self._init_driver(headless=headless, profile_path=profile_path, chromedriver_path=chromedriver_path)
            self.logger.debug('Navigating to %s', set_url)
            driver.get(set_url)
            time.sleep(1)

            # attempt login if required
            self.login_if_needed(driver, username, password, nickname)

            # look for YAML button
            try:
                btn = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, YAML_BUTTON_XPATH)))
            except Exception:
                self.logger.debug('YAML button not found on page %s', set_url)
                return ""

            # click button to open modal/copy panel
            try:
                btn.click()
                time.sleep(0.6)
            except Exception:
                self.logger.debug('Failed to click YAML button; continuing to search for YAML content')

            # look for textarea/pre elements that likely contain YAML
            yaml_text = ""
            try:
                # try textarea inside modal
                ta = driver.find_element(By.XPATH, "//textarea")
                yaml_text = ta.get_attribute('value') or ta.text
            except Exception:
                # try pre/code blocks
                try:
                    pre = driver.find_element(By.XPATH, "//pre")
                    yaml_text = pre.text
                except Exception:
                    # last resort: find any element with a lot of text and 'yaml' nearby
                    candidates = driver.find_elements(By.XPATH, "//*[string-length(normalize-space(text())) > 100]")
                    for el in candidates:
                        txt = el.get_attribute('innerText') or el.text
                        if 'metadata:' in (txt or ''):
                            yaml_text = txt
                            break

            if not yaml_text:
                # No explicit YAML modal found. As a fallback, collect large text
                # nodes from the page (Next.js initial-state JSON fragments often
                # appear inside large text nodes) and return that combined text so
                # the extractor can parse JSON-like asset lists.
                self.logger.debug('No textarea/pre with YAML found; collecting large text nodes as fallback for %s', set_url)
                parts = []
                candidates = driver.find_elements(By.XPATH, "//*[string-length(normalize-space(text())) > 100]")
                for el in candidates:
                    try:
                        txt = el.get_attribute('innerText') or el.text
                        if txt:
                            parts.append(txt)
                    except Exception:
                        continue
                combined = "\n".join(parts)
                if combined:
                    self.logger.debug('Collected %d chars from large text nodes as fallback', len(combined))
                    return combined
                self.logger.debug('Could not locate YAML content for %s', set_url)
                return ""

            self.logger.info('Scraped YAML (%d chars) from %s', len(yaml_text), set_url)
            return yaml_text
        finally:
            try:
                if driver:
                    driver.quit()
            except Exception:
                pass


def extract_asset_ids_from_yaml(yaml_text: str) -> List[Dict[str, str]]:
    """Extract assets from YAML or JSON-like text.

    Returns a list of dicts: {"id": <uuid>, "fileType": <type_or_unknown>}.
    Heuristics:
      - Find compact JSON-like objects containing both "id" and "fileType".
      - Fallback to any explicit "id":"<uuid>" occurrences.
      - Final fallback to any uuid-like tokens.
    """
    assets: List[Dict[str, str]] = []
    seen: Set[str] = set()

    # Try to find objects that include both id and fileType (common in page JSON)
    obj_re = re.compile(r'\{[^}]{0,400}?"id"\s*:\s*"([0-9a-fA-F-]{36})"[^}]{0,200}?"fileType"\s*:\s*"([a-zA-Z0-9_-]+)"', re.DOTALL)
    for m in obj_re.finditer(yaml_text):
        uid = m.group(1)
        ftype = m.group(2)
        if uid not in seen:
            assets.append({"id": uid, "fileType": ftype})
            seen.add(uid)

    # If none found, try looser pattern: "id":"<uuid>" anywhere
    if not assets:
        for m in re.finditer(r'"id"\s*:\s*"([0-9a-fA-F-]{36})"', yaml_text):
            uid = m.group(1)
            if uid not in seen:
                assets.append({"id": uid, "fileType": "unknown"})
                seen.add(uid)

    # Final fallback: any uuid-like tokens
    if not assets:
        for m in re.finditer(r'([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})', yaml_text):
            uid = m.group(1)
            if uid not in seen:
                assets.append({"id": uid, "fileType": "unknown"})
                seen.add(uid)

    return assets
