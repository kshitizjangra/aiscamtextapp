import streamlit as st
import requests
import re
import time
import random

# Hugging Face API details
API_URL = "https://router.huggingface.co/hf-inference/models/phishbot/ScamLLM"
HF_API_KEY = "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"  # Replace with your actual API key

headers = {"Authorization": f"Bearer {HF_API_KEY}"}

# Model Label Mapping
LABEL_MAPPING = {
    "LABEL_0": "Scam",
    "LABEL_1": "Not a Scam"
}

# Function to analyze text using the same model (for both text & email)
def analyze_text(input_text):
    if not input_text.strip():
        return "Please enter text", 0.0

    payload = {"inputs": input_text}
    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()

        # Safely handle nested lists
        if isinstance(result, list) and len(result) > 0:
            if isinstance(result[0], list):
                result = result[0]

            # Ensure the result is a list of dicts with "score" & "label"
            if isinstance(result[0], dict) and "score" in result[0]:
                best_match = max(result, key=lambda x: x.get("score", 0))
                label = best_match.get("label", "Unknown")
                confidence = best_match.get("score", 0.0)

                # Map label to human-readable text
                readable_label = LABEL_MAPPING.get(label, "Unknown")
                return readable_label, confidence

    return "API Error", 0.0

# Function to detect URLs and Emails
def detect_links_emails(text):
    url_pattern = re.compile(r"https?://[^\s]+|www\.[^\s]+")
    email_pattern = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    
    urls = url_pattern.findall(text)
    emails = email_pattern.findall(text)
    return {"urls": urls, "emails": emails}

# Function to check suspicious URLs
def is_suspicious_url(url):
    suspicious_patterns = ["free", "win", "claim", "click", "verify", "login", "secure", "bank", "update"]
    return any(word in url.lower() for word in suspicious_patterns)

# Streamlit UI
st.set_page_config(page_title="Scam Detection App", page_icon="🔍", layout="centered")

st.title("🔍 Scam Detection App")
st.write("Enter a text below to check if it's a scam or not.")

# User input box
user_input = st.text_area("Enter text to analyze:", value="", height=150)

# Auto-analyze option
auto_check = st.checkbox("Auto-analyze while typing")

if auto_check or st.button("Analyze"):
    prediction, confidence = analyze_text(user_input)

    # Confidence bar
    st.progress(confidence)

    # Display result
    if prediction == "Scam":
        st.error(f"🚨 **Prediction: {prediction}** (Confidence: {confidence:.2%})")
    elif prediction == "Not a Scam":
        st.success(f"✅ **Prediction: {prediction}** (Confidence: {confidence:.2%})")
    else:
        st.warning(f"⚠️ {prediction} (Confidence: {confidence:.2%})")

    # Check for URLs & Emails
    detected = detect_links_emails(user_input)
    url_warning = any(is_suspicious_url(url) for url in detected["urls"])

    if detected["urls"]:
        st.warning(f"🔗 **Detected URLs:** {', '.join(detected['urls'])}")
        if url_warning:
            st.error("🚨 **Suspicious URL detected! Be careful before clicking.**")

    if detected["emails"]:
        st.warning(f"📧 **Detected Emails:** {', '.join(detected['emails'])}")

# --- AI Scam Insights Section ---
st.markdown("---")
st.subheader("💡 AI Scam Insights")

scam_insights = [
    "Always verify email senders before clicking any link.",
    "Do not share OTPs or passwords with anyone.",
    "Investment schemes promising high returns are usually scams.",
    "Check website URLs before entering payment details.",
    "Scammers often create urgency to make you act fast.",
    # New insights added:
    "Beware of Digital Arrest scams: Scammers impersonate law enforcement and claim you're digitally under arrest—demanding money. Stay calm, verify the caller's identity, and never let fear override your judgment.",
    "WhatsApp OTP Scam Alert: A hacker may take over a relative's WhatsApp account and send you an OTP request. Remember, OTPs are your private keys—never share them, even if the message seems to come from someone you know."
]

if st.button("Get AI Scam Insights"):
    with st.spinner("Fetching AI insights..."):
        time.sleep(1.5)
        insight = random.choice(scam_insights)
        st.subheader("⚠️ Scam Tip:")
        st.write(insight)

st.markdown("---")
