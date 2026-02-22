import pandas as pd
import requests
import streamlit as st

API_BASE = st.sidebar.text_input("API Base URL", "http://127.0.0.1:8000/api")

st.title("Autopilot Dataset Discovery + Label QA")

st.header("Search")
q = st.text_input("Query")
weather = st.selectbox("Weather", ["", "clear", "rain", "fog", "night"])
scenario = st.selectbox("Scenario", ["", "intersection", "merge", "occlusion", "pedestrian_crossing"])
if st.button("Run Search"):
    try:
        params = {"q": q or None, "weather": weather or None, "scenario": scenario or None, "limit": 50}
        res = requests.get(f"{API_BASE}/assets/search", params=params, timeout=10)
        res.raise_for_status()
        data = res.json()
        if data:
            st.dataframe(pd.DataFrame(data))
        else:
            st.info("Search returned no assets. Try removing filters or re-running ingestion.")
    except requests.RequestException as exc:
        st.error(f"Search request failed: {exc}")

st.header("Label QA")
if st.button("Refresh QA Summary"):
    try:
        qa = requests.get(f"{API_BASE}/qa/summary", timeout=10)
        qa.raise_for_status()
        payload = qa.json()

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Assets", payload["total_assets"])
        c2.metric("Total Annotations", payload["total_annotations"])
        c3.metric("Missing Labels", payload["missing_label_assets"])

        st.write("Annotator disagreement rate", payload["annotator_disagreement_rate"])
        st.subheader("Class Distribution")
        if payload["label_distribution"]:
            dist_df = pd.DataFrame(list(payload["label_distribution"].items()), columns=["class", "count"])
            st.bar_chart(dist_df.set_index("class"))

        st.subheader("Hard Examples")
        st.write(payload["hard_examples"])
    except requests.RequestException as exc:
        st.error(f"QA request failed: {exc}")
