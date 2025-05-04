# --- Converted Streamlit App (No Flask) ---
import streamlit as st



# === Scraper Functions ===
from flask import Blueprint, request, jsonify
import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

scraper_bp = Blueprint('scraper', __name__)

# ✅ Country Selection for Scraper
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

@scraper_bp.route('/search', methods=['POST'])
def search_ads():
    data = request.json
    country = data.get("country")
    query = data.get("query")

    if not country or not query:
        return jsonify({"error": "Missing required parameters"}), 400

    if country not in COUNTRIES:
        return jsonify({"error": "Invalid country code"}), 400

    results = scrape_ads(country, query)
    return jsonify({"data": results, "message": "Results found"})

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


# === Reddit Functions ===
from flask import Blueprint, request, jsonify
import requests
import logging

reddit_bp = Blueprint('reddit', __name__)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@reddit_bp.route('/search-reddit', methods=['POST'])
def search_reddit():
    data = request.json
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "Missing query parameter"}), 400

    logging.info(f"🔍 Searching Reddit for: {query}")

    base_url = "https://www.reddit.com/search.json"
    params = {"q": query, "sort": "relevance", "limit": 25}

    headers = {'User-Agent': "Mozilla/5.0"}

    try:
        response = requests.get(base_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []
        for post in data.get('data', {}).get('children', []):
            post_data = post['data']
            results.append({
                "query": query,
                "title": post_data.get('title', 'No Title'),
                "url": f"https://www.reddit.com{post_data.get('permalink', '')}"
            })

        logging.info(f"✅ Found {len(results)} results for {query}")
        return jsonify({"message": "Results found", "data": results})

    except requests.RequestException as e:
        logging.error(f"❌ Reddit search error: {e}")
        return jsonify({"error": "Failed to fetch Reddit data"}), 500


# === Malware Functions ===
from flask import Blueprint, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse, parse_qs, unquote
import time
import logging
import random
import re
from fake_useragent import UserAgent

# ✅ Setup Blueprint
malware_bp = Blueprint('malware', __name__)

# ✅ Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ List of domains to be whitelisted (ignored in results)
WHITELISTED_DOMAINS = ["corneredtomb.com", "dedigger.com"]

def extract_clean_url(url):
    """ Extracts only the clean URL path from Google redirect links. """
    parsed_url = urlparse(url)

    # ✅ If it's a Google redirect URL, extract the `q` parameter
    if "google.com/url" in parsed_url.netloc:
        query_params = parse_qs(parsed_url.query)
        if "q" in query_params:
            real_url = query_params["q"][0]  # ✅ Extract actual link
            real_url = unquote(real_url)  # ✅ Decode URL encoding

            # ✅ Use regex to extract the clean link (Google Drive or other)
            match = re.search(r"(https://drive\.google\.com/file/d/[^/]+)", real_url)
            if match:
                return match.group(1)  # ✅ Return only "https://drive.google.com/file/d/{file_id}"

            return real_url.split("?")[0]  # ✅ Remove query parameters if not Google Drive

    return url  # ✅ Return original URL if no redirection detected

def is_whitelisted(url):
    """ Checks if the URL's domain is in the whitelist. """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace("www.", "")  # ✅ Normalize domain

    return domain in WHITELISTED_DOMAINS  # ✅ True if domain is whitelisted

@malware_bp.route('/search-malware', methods=['POST'])
def search_malware():
    """ Handles the API request for malware document searches. """
    data = request.json
    query = data.get("query", "").strip()

    if not query:
        return jsonify({"error": "Missing query parameter"}), 400

    logging.info(f"🔍 Scraping De Digger for malware results: {query}")

    # ✅ Call the function that scrapes De Digger
    results = scrape_malware_documents(query)

    # ✅ Modify results: Extract only the real landing pages and filter whitelist domains
    updated_results = []
    for result in results:
        real_url = extract_clean_url(result["landing_page"])

        if not is_whitelisted(real_url):  # ✅ Ignore whitelisted domains
            updated_results.append({
                "keyword": result["keyword"],
                "landing_page": real_url  # ✅ Show only the cleaned landing page
            })

    return jsonify({"message": "Results found", "data": updated_results})

def scrape_malware_documents(keyword):
    """ Scrapes malware-related documents from De Digger """
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--headless")  # ✅ Run in headless mode for better performance

    # ✅ Random User-Agent to avoid detection
    ua = UserAgent()
    options.add_argument(f"user-agent={ua.random}")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    url = "https://www.dedigger.com/#gsc.tab=0&gsc.sort="
    driver.get(url)
    time.sleep(5)

    try:
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='text']"))
        )
        search_input.clear()

        # ✅ Simulate human-like typing
        for char in keyword:
            search_input.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3))  # ✅ Simulate slow typing

        time.sleep(2)
        search_input.send_keys(Keys.RETURN)
        
        logging.info("🔄 Waiting for search results...")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='gsc-webResult gsc-result']//a"))
        )
        
        results = []
        result_elements = driver.find_elements(By.XPATH, "//div[@class='gsc-webResult gsc-result']//a")
        
        for index, result_element in enumerate(result_elements):
            try:
                landing_page_url = result_element.get_attribute("href")

                if landing_page_url:  # ✅ Avoid empty results
                    results.append({
                        "keyword": keyword,
                        "landing_page": landing_page_url
                    })
                    logging.info(f"✅ Found {index + 1}: {landing_page_url}")

            except Exception as e:
                logging.warning(f"⚠️ Error retrieving result {index + 1}: {e}")

        driver.quit()

        if not results:
            logging.warning("⚠️ No results retrieved!")

        return results

    except Exception as e:
        logging.error(f"❌ Error during scraping: {e}")
        driver.quit()
        return []


# === Whois Functions ===


# === Streamlit Interface ===
import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the page
st.set_page_config(
    page_title="Cyber Tools Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# Constants
BACKEND_URL = "http://localhost:5000"  # Update this with your backend URL
API_ENDPOINTS = {
    "reddit": f"{BACKEND_URL}/api/reddit",
    "meta": f"{BACKEND_URL}/api/meta",
    "malware": f"{BACKEND_URL}/api/malware"
}

# Session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        try:
            response = requests.post(
                f"{BACKEND_URL}/api/login",
                json={"username": username, "password": password}
            )
            if response.status_code == 200:
                st.session_state.authenticated = True
                st.success("Login successful!")
                st.experimental_rerun()
            else:
                st.error("Invalid credentials")
        except Exception as e:
            st.error(f"Error connecting to backend: {str(e)}")

def reddit_tool():
    st.title("Reddit Mentions Finder")
    keyword = st.text_input("Enter keyword to search")
    limit = st.number_input("Number of results", min_value=1, max_value=100, value=10)
    
    if st.button("Search"):
        try:
            response = requests.post(
                API_ENDPOINTS["reddit"],
                json={"keyword": keyword, "limit": limit}
            )
            if response.status_code == 200:
                results = response.json()
                st.write("Results:")
                for result in results:
                    st.write(f"- {result['title']} ({result['url']})")
            else:
                st.error("Error fetching results")
        except Exception as e:
            st.error(f"Error: {str(e)}")

def meta_tool():
    st.title("Meta Ads Finder")
    keyword = st.text_input("Enter keyword to search")
    country = st.text_input("Country code (e.g., US)", value="US")
    
    if st.button("Search"):
        try:
            response = requests.post(
                API_ENDPOINTS["meta"],
                json={"keyword": keyword, "country": country}
            )
            if response.status_code == 200:
                results = response.json()
                st.write("Results:")
                for result in results:
                    st.write(f"- {result['title']} ({result['url']})")
            else:
                st.error("Error fetching results")
        except Exception as e:
            st.error(f"Error: {str(e)}")

def malware_tool():
    st.title("Malware Document Finder")
    keyword = st.text_input("Enter keyword to search")
    
    if st.button("Search"):
        try:
            response = requests.post(
                API_ENDPOINTS["malware"],
                json={"keyword": keyword}
            )
            if response.status_code == 200:
                results = response.json()
                st.write("Results:")
                for result in results:
                    st.write(f"- {result['title']} ({result['url']})")
            else:
                st.error("Error fetching results")
        except Exception as e:
            st.error(f"Error: {str(e)}")

def main():
    if not st.session_state.authenticated:
        login()
    else:
        st.sidebar.title("Navigation")
        tool = st.sidebar.radio(
            "Select Tool",
            ["Reddit Mentions Finder", "Meta Ads Finder", "Malware Document Finder"]
        )
        
        if tool == "Reddit Mentions Finder":
            reddit_tool()
        elif tool == "Meta Ads Finder":
            meta_tool()
        elif tool == "Malware Document Finder":
            malware_tool()
        
        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.experimental_rerun()

if __name__ == "__main__":
    main() 