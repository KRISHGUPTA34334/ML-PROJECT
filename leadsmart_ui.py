import streamlit as st
import pandas as pd
import requests

# ⛔ Replace with your actual API keys
CLEARBIT_API_KEY = "your_clearbit_api_key"
HUNTER_API_KEY = "your_hunter_api_key"

st.set_page_config(page_title="LeadSmart: Enrich & Score Leads", layout="wide")
st.title("🚀 LeadSmart – Lead Enrichment & Scoring Tool")

uploaded_file = st.file_uploader("Upload a CSV file with 'Company' and 'Website' columns", type=['csv'])

# ------------------------ ENRICHMENT FUNCTIONS ------------------------

def clearbit_enrich(domain):
    try:
        url = f"https://company.clearbit.com/v2/companies/find?domain={domain}"
        headers = {'Authorization': f'Bearer {CLEARBIT_API_KEY}'}
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json()
            return {
                'Industry': data.get('category', {}).get('industry', ''),
                'Tech Stack': ', '.join(data.get('tech', [])) if data.get('tech') else '',
                'Employees': data.get('metrics', {}).get('employees', 0),
                'Description': data.get('description', '')
            }
    except:
        pass
    return {'Industry': '', 'Tech Stack': '', 'Employees': 0, 'Description': ''}

def hunter_email(domain):
    try:
        url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={HUNTER_API_KEY}"
        r = requests.get(url)
        if r.status_code == 200:
            emails = r.json().get('data', {}).get('emails', [])
            return emails[0]['value'] if emails else ''
    except:
        pass
    return ''

def score_lead(lead):
    score = 0
    desc = lead.get('Description', '').lower()
    if any(kw in desc for kw in ['ai', 'data', 'payments', 'leads', 'docs']):
        score += 30
    if lead.get('Email'):
        score += 20
    size = lead.get('Employees', 0)
    score += 30 if size > 1000 else 20 if size > 50 else 10
    return score

# ------------------------ PROCESSING LOGIC ------------------------

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("📊 Uploaded Data:", df)

    if st.button("🔍 Enrich & Score Leads"):
        enriched_data = []
        with st.spinner("Fetching data from APIs..."):
            for _, row in df.iterrows():
                domain = row['Website']
                enriched = clearbit_enrich(domain)
                email = hunter_email(domain)
                lead = {
                    'Company': row['Company'],
                    'Website': domain,
                    **enriched,
                    'Email': email
                }
                lead['Score'] = score_lead(lead)
                enriched_data.append(lead)

        enriched_df = pd.DataFrame(enriched_data).sort_values(by='Score', ascending=False).reset_index(drop=True)
        st.success("✅ Enrichment complete!")

        st.dataframe(enriched_df, use_container_width=True)
        csv = enriched_df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download Enriched CSV", csv, "enriched_leads.csv", "text/csv")

