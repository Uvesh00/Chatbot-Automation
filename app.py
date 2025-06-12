import streamlit as st
import pandas as pd
from test import run_test

st.title("Chatbot Automation Tester")

env_name = st.selectbox("Select Environment", ["Cog Search", "General"])
url = st.text_input("Chatbot Webpage URL")
username = st.text_input("Username")
password = st.text_input("Password", type="password")
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
live_preview = st.checkbox("Enable Live Preview (show browser)")

if st.button("Run Test") and uploaded_file and url and username and password:
    with st.spinner("Running tests..."):
        result_df = run_test(env_name, url, username, password, uploaded_file, live_preview)
        st.success("Testing complete!")
        st.dataframe(result_df)
        st.download_button("Download Results", result_df.to_csv(index=False), "results.csv")
