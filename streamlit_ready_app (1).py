import streamlit as st
import logging
import time
import requests
import socket
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ========== Tool 1: Facebook Ads Scraper ==========
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

        time.sleep(7)
        WebDriverWait(driver, 12).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Library ID')]"))
        )

        ad_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Library ID')]")

        for ad in ad_elements:
            ad_id_match = ad.text.strip().split()[-1]
            ad_url = f"https://www.facebook.com/ads/library/?id={ad_id_match}"

            ad_content = "N/A"
            try:
                ad_container = ad.find_element(By.XPATH, "./ancestor::div[contains(@class, 'xh8yej3')]")
                ad_content_element = ad_container.find_element(By.XPATH, ".//div[@style='white-space: pre-wrap;']/span")
                ad_content = ad_content_element.text.strip()
            except:
                pass

            ads_data.append({
                "query": query,
                "country": country_code,
                "ad_id": ad_id_match,
                "ad_url": ad_url,
                "ad_content": ad_content
            })

    except Exception as e:
        logging.error(f"❌ Scraper error: {e}")

    finally:
        if driver:
            driver.quit()

    return ads_data


# ========== Tool 2: Reddit Mentions ==========
def search_reddit_posts(query, size=10):
    url = f"https://api.pushshift.io/reddit/search/submission/?q={query}&size={size}&sort=desc"
    try:
        response = requests.get(url)
        data = response.json()
        return data.get("data", [])
    except Exception as e:
        return [{"title": f"Error: {e}", "url": ""}]


# ========== Tool 3: Malware Simulation ==========
def analyze_malware(file_name):
    if "malware" in file_name.lower():
        return {"status": "Malicious", "description": "This file is flagged as malware."}
    return {"status": "Clean", "description": "No malicious indicators found."}


# ========== Tool 4: WHOIS ==========
def whois_lookup(domain):
    try:
        ip = socket.gethostbyname(domain)
        return {"domain": domain, "ip": ip}
    except Exception as e:
        return {"error": str(e)}


# ========== Streamlit UI ==========
st.set_page_config(page_title="Cyber Tools", layout="wide")
st.title("🛡️ Cyber Tools Suite")

tab1, tab2, tab3, tab4 = st.tabs(["🔍 Facebook Ads", "📢 Reddit Search", "🧪 Malware Check", "🌐 WHOIS Lookup"])

with tab1:
    st.header("Facebook Ads Scraper")
    country = st.selectbox("Select a country", list(COUNTRIES.keys()))
    query = st.text_input("Enter keyword to search ads for", key="ads_query")
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
                st.warning("No ads found.")

with tab2:
    st.header("Reddit Mentions Finder")
    reddit_query = st.text_input("Enter keyword to search Reddit", key="reddit_query")
    if st.button("Search Reddit"):
        with st.spinner("Fetching posts..."):
            posts = search_reddit_posts(reddit_query)
            for post in posts:
                title = post.get("title", "No title")
                url = post.get("url", "#")
                st.markdown(f"- [{title}]({url})")

with tab3:
    st.header("Malware Simulation Tool")
    malware_filename = st.text_input("Enter filename to simulate scan")
    if st.button("Check File"):
        result = analyze_malware(malware_filename)
        st.info(f"Status: {result['status']}")
        st.markdown(result['description'])

with tab4:
    st.header("WHOIS Lookup")
    domain = st.text_input("Enter domain to check WHOIS info")
    if st.button("Lookup Domain"):
        result = whois_lookup(domain)
        if "error" in result:
            st.error(result["error"])
        else:
            st.success(f"Domain: {result['domain']} ➜ IP: {result['ip']}")
