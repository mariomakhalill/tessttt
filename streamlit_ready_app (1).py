import streamlit as st
import requests
import socket

# ========== Tool 1: Facebook Ads Placeholder ==========
def scrape_ads_placeholder():
    return [{
        "ad_id": "N/A",
        "ad_url": "#",
        "ad_content": "Scraping ads requires a local environment with Chrome. This feature is unavailable on Streamlit Cloud."
    }]

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

# ========== Tool 2: Reddit Mentions ==========
def search_reddit_posts(query, size=10):
    url = f"https://api.pushshift.io/reddit/search/submission/?q={query}&size={size}&sort=desc"
    try:
        response = requests.get(url)
        data = response.json()
        return data.get("data", [])
    except Exception as e:
        st.error(f"Reddit API failed: {e}")
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
        st.warning("⚠️ This feature is not supported on Streamlit Cloud. Please run locally for full functionality.")
        results = scrape_ads_placeholder()
        for ad in results:
            st.markdown(f"**Ad ID:** {ad['ad_id']}")
            st.markdown(f"**Content:** {ad['ad_content']}")
            st.markdown("---")

with tab2:
    st.header("Reddit Mentions Finder")
    reddit_query = st.text_input("Enter keyword to search Reddit", key="reddit_query")
    if st.button("Search Reddit"):
        if not reddit_query.strip():
            st.warning("Please enter a keyword to search.")
        else:
            with st.spinner("Fetching posts..."):
                posts = search_reddit_posts(reddit_query)
                if posts:
                    for post in posts:
                        title = post.get("title", "No title")
                        url = post.get("url", "#")
                        st.markdown(f"- [{title}]({url})")
                else:
                    st.warning("No posts found or request failed.")

with tab3:
    st.header("Malware Simulation Tool")
    malware_filename = st.text_input("Enter filename to simulate scan")
    if st.button("Check File"):
        if not malware_filename.strip():
            st.warning("Please enter a filename.")
        else:
            result = analyze_malware(malware_filename)
            st.info(f"Status: {result['status']}")
            st.markdown(result['description'])

with tab4:
    st.header("WHOIS Lookup")
    domain = st.text_input("Enter domain to check WHOIS info")
    if st.button("Lookup Domain"):
        if not domain.strip():
            st.warning("Please enter a domain.")
        else:
            result = whois_lookup(domain)
            if "error" in result:
                st.error(result["error"])
            else:
                st.success(f"Domain: {result['domain']} ➜ IP: {result['ip']}")
