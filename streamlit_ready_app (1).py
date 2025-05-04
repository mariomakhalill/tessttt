import streamlit as st
import logging


import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

COUNTRIES = {
    "US": "🇺🇸 United States",
    "UK": "🇬🇧 United Kingdom",
    "CA": "🇨🇦 Canada",
    "FR": "🇫🇷 France",
    "DE": "🇩🇪 Germany",
    "AE": "🇦🇪 United Arab Emirates",
    "SA": "🇸🇦 Saudi Arabia",
    "EG": "🇪🇬 Egypt",
    "IN": "🇮🇳 India",
    "JP": "🇯🇵 Japan",
    "CN": "🇨🇳 China",
    "BR": "🇧🇷 Brazil",
    "AU": "🇦🇺 Australia",
}

def scrape_ads(country_code, query):
    url = f"https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country={country_code}&q={query}&search_type=keyword_unordered"
    logging.info(f"🔍 Searching Facebook Ads Library: {url}")

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-popup-blocking")

    driver = None
    ads_data = []

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)

        logging.info("🕒 Waiting for Facebook ads to load...")
        time.sleep(7)

        WebDriverWait(driver, 12).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Library ID')]"))
        )

        ad_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Library ID')]")
        logging.info(f"✅ Found {len(ad_elements)} ads!")

        for ad in ad_elements:
            ad_id_match = ad.text.strip().split()[-1]
            ad_url = f"https://www.facebook.com/ads/library/?id={ad_id_match}"

            ad_content = "N/A"
            try:
                ad_container = ad.find_element(By.XPATH, "./ancestor::div[contains(@class, 'xh8yej3')]")
                ad_content_element = ad_container.find_element(By.XPATH, ".//div[@style='white-space: pre-wrap;']/span")
                ad_content = ad_content_element.text.strip()
            except:
                logging.warning(f"⚠️ Could not extract content for Ad ID: {ad_id_match}")

            ads_data.append({
                "query": query,
                "country": country_code,
                "ad_id": ad_id_match,
                "ad_url": ad_url,
                "ad_content": ad_content
            })

    except Exception as e:
        logging.error(f"❌ Facebook Ad scraping error: {e}")

    finally:
        if driver:
            driver.quit()

    return ads_data


# === Streamlit UI ===

st.title("Facebook Ads Scraper Tool")

country = st.selectbox("Select a country", list(COUNTRIES.keys()))
query = st.text_input("Enter keyword to search ads for")

if st.button("Search Facebook Ads"):
    with st.spinner("Scraping ads..."):
        results = scrape_ads(country, query)
        if results:
            st.success(f"Found {len(results)} ads.")
            for ad in results:
                st.markdown(f"**Ad ID:** [{ad['ad_id']}]({ad['ad_url']})")
                st.markdown(f"**Content:** {ad['ad_content']}")
                st.markdown("---")
        else:
            st.warning("No ads found or failed to scrape.")
