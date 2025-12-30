import streamlit as st
import requests
import json
import pandas as pd
from PIL import Image
import os

# Configuration de la page
st.set_page_config(
    page_title="LLM Firewall Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style personnalisé
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e293b;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #334155;
    }
    .status-box {
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .safe {
        background-color: #064e3b;
        border: 1px solid #059669;
        color: #34d399;
    }
    .danger {
        background-color: #450a0a;
        border: 1px solid #dc2626;
        color: #f87171;
    }
    </style>
    """, unsafe_allow_html=True)

# API Endpoint (FastAPI)
API_URL = "http://localhost:8000"

def check_api_health():
    try:
        response = requests.get(f"{API_URL}/health")
        return response.status_code == 200
    except:
        return False

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/isometric/512/shield.png", width=100)
    st.title("🛡️ Firewall Control")
    st.markdown("---")
    
    health = check_api_health()
    if health:
        st.success("API Status: Online")
    else:
        st.error("API Status: Offline")
        st.info("Please run `python api.py` first.")
    
    st.markdown("---")
    st.markdown("### Settings")
    use_ml = st.checkbox("Use ML Classifiers", value=True)
    st.markdown("---")
    st.markdown("### About")
    st.info("This dashboard provides a visual interface for the LLM Prompt Firewall system.")

# Main Page
st.title("🛡️ LLM Firewall - Security Dashboard")
st.markdown("Analyze prompts and monitor model behavior in real-time.")

tab1, tab2, tab3 = st.tabs(["🔍 Prompt Scanner", "📤 Response Filter", "📊 Statistics"])

with tab1:
    st.subheader("Analyze User Input")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        prompt_text = st.text_area("User Prompt", placeholder="Enter prompt here...", height=200)
        scan_button = st.button("🚀 Run Security Scan")
    
    with col2:
        st.markdown("#### Detection Settings")
        st.write("- Rule-based Check: ✅ Active")
        st.write("- ML Ensemble: ✅ Active")
        st.write("- Sensitive Data Scanner: ✅ Active")

    if scan_button and prompt_text:
        with st.spinner("Analyzing prompt safety..."):
            try:
                payload = {"prompt": prompt_text, "use_ml": use_ml}
                response = requests.post(f"{API_URL}/check-prompt", json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    is_malicious = result['is_malicious']
                    confidence = result['confidence']
                    
                    st.markdown("---")
                    
                    if is_malicious:
                        st.markdown(f'<div class="status-box danger"><h3>🚨 THREAT DETECTED</h3><p>This prompt has been flagged as malicious.</p></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="status-box safe"><h3>✅ SAFE</h3><p>No threats detected in this prompt.</p></div>', unsafe_allow_html=True)
                    
                    m1, m2 = st.columns(2)
                    m1.metric("Confidence Score", f"{confidence*100:.1f}%")
                    m2.metric("Verdict", "BLOCKED" if is_malicious else "ALLOWED")
                    
                    with st.expander("Technical details"):
                        st.json(result)
                else:
                    st.error(f"API Error: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

with tab2:
    st.subheader("Filter Model Response")
    resp_text = st.text_area("Model Output", placeholder="Paste LLM response here...", height=150)
    filter_btn = st.button("✨ Filter & Redact")
    
    if filter_btn and resp_text:
        try:
            payload = {"response": resp_text, "redact": True}
            response = requests.post(f"{API_URL}/filter-response", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                
                if not result['is_safe']:
                    st.warning("⚠️ Sensitive Information Detected!")
                    st.write("**Detected Types:** " + ", ".join(result['info_types']))
                    
                    st.markdown("#### Redacted Output")
                    st.code(result['redacted_text'])
                else:
                    st.success("✅ Output is safe. No PII or secrets found.")
                
                with st.expander("Raw analysis"):
                    st.json(result)
        except Exception as e:
            st.error(f"Connection Error: {e}")

with tab3:
    st.subheader("System Statistics")
    try:
        response = requests.get(f"{API_URL}/statistics")
        if response.status_code == 200:
            stats = response.json()
            
            c1, c2, c3 = st.columns(3)
            c1.metric("ML Models Loaded", stats['ml_models_loaded'])
            c2.metric("Ensemble Voting", "Enabled" if stats['use_ensemble'] else "Disabled")
            c3.metric("Confidence Threshold", stats['threshold_confidence'])
            
            st.markdown("#### Configuration")
            st.table(pd.DataFrame([stats]))
    except:
        st.warning("Could not fetch statistics. Is the API running?")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #64748b;'>Prompt Firewall v0.1.0 | Developed by Antigravity AI</div>", unsafe_allow_html=True)
