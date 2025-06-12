import time
import pandas as pd
import tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import streamlit as st

ENV_CONFIG = {
    "Solutions Dev": {
        "username_selector": {"by": "id", "value": "userID"},
        "password_selector": {"by": "id", "value": "password"},
        "submit_selector": {"by": "class_name", "value": "btn-dark"}
    },
    "Products": {
        "username_selector": {"by": "id", "value": "userID"},
        "password_selector": {"by": "id", "value": "password"},
        "submit_selector": {"by": "class_name", "value": "btn-dark"}
    },
    "UAT": {
        "username_selector": {"by": "id", "value": "userID"},
        "password_selector": {"by": "id", "value": "password"},
        "submit_selector": {"by": "class_name", "value": "btn-dark"}
    },
    "Production": {
        "username_selector": {"by": "id", "value": "userID"},
        "password_selector": {"by": "id", "value": "password"},
        "submit_selector": {"by": "class_name", "value": "btn-dark"}
    },
    "Newpresales": {
        "username_selector": {"by": "id", "value": "userID"},
        "password_selector": {"by": "id", "value": "password"},
        "submit_selector": {"by": "class_name", "value": "btn-dark"}
    },
    "DESIT": {
        "username_selector": {"by": "name", "value": "un"},
        "password_selector": {"by": "name", "value": "pw"},
        "submit_selector": {"by": "class_name", "value": "btn-primary"}
    },
    "DEQA": {
        "username_selector": {"by": "name", "value": "un"},
        "password_selector": {"by": "name", "value": "pw"},
        "submit_selector": {"by": "class_name", "value": "btn-primary"}
    },
    "DEUAT": {
        "username_selector": {"by": "name", "value": "un"},
        "password_selector": {"by": "name", "value": "pw"},
        "submit_selector": {"by": "class_name", "value": "btn-primary"}
    },
    "Rybot Production": {
        "username_selector": {"by": "name", "value": "un"},
        "password_selector": {"by": "name", "value": "pw"},
        "submit_selector": {"by": "class_name", "value": "btn-primary"}
    }
}

BY_MAP = {
    "id": By.ID,
    "name": By.NAME,
    "class_name": By.CLASS_NAME,
    "css_selector": By.CSS_SELECTOR,
    "xpath": By.XPATH,
}

def run_test(env_name, url, username, password, file, live_preview=False):
    df = pd.read_excel(file)
    env = ENV_CONFIG[env_name]

    options = webdriver.ChromeOptions()
    if not live_preview:
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=options)
    results = []

    try:
        driver.get(url)
        time.sleep(2)

        uname_by = BY_MAP[env["username_selector"]["by"]]
        uname_val = env["username_selector"]["value"]
        driver.find_element(uname_by, uname_val).send_keys(username)

        pwd_by = BY_MAP[env["password_selector"]["by"]]
        pwd_val = env["password_selector"]["value"]
        driver.find_element(pwd_by, pwd_val).send_keys(password)

        submit_by = BY_MAP[env["submit_selector"]["by"]]
        submit_val = env["submit_selector"]["value"]
        driver.find_element(submit_by, submit_val).click()

        time.sleep(5)
        driver.get(url)
        time.sleep(30)
        driver.find_element(By.CLASS_NAME, "chatButtonBG").click()
        time.sleep(10)

        wait = WebDriverWait(driver, 60)

        for index, row in df.iterrows():
            question = row["Question"]
            expected_answer = row["ExpectedAnswer"]
            expected_link = str(row["ExpectedLink"]).strip()

            try:
                previous_response = driver.find_elements(By.CSS_SELECTOR, ".leftmsg")[-1].text.strip()
            except IndexError:
                previous_response = ""

            chat_input = driver.find_element(By.CSS_SELECTOR, ".enterKeyDetect")
            chat_input.send_keys(question + Keys.RETURN)

            try:
                wait.until(lambda d: d.find_elements(By.CSS_SELECTOR, ".leftmsg") and
                           d.find_elements(By.CSS_SELECTOR, ".leftmsg")[-1].text.strip() != previous_response)

                responses = driver.find_elements(By.CSS_SELECTOR, ".leftmsg")
                last_response = responses[-1].text.strip()
                parent_element = responses[-1]

                try:
                    link_element = parent_element.find_element(By.TAG_NAME, "a")
                    extracted_link = link_element.get_attribute("href").strip()
                except:
                    extracted_link = "[No link found]"

            except Exception:
                last_response = "[No response received within timeout]"
                extracted_link = "[No link found]"

            pass_answer = expected_answer in last_response
            pass_link = expected_link in extracted_link
            result = "✅ PASS" if pass_answer and pass_link else "❌ FAIL"

            results.append({
                "Question": question,
                "ExpectedAnswer": expected_answer,
                "ExpectedLink": expected_link,
                "BotResponse": last_response,
                "ExtractedLink": extracted_link,
                "Result": result
            })

    finally:
        if not live_preview:
            driver.quit()

    return pd.DataFrame(results)

st.title("Chatbot Automation Tester")

env_name = st.selectbox("Select Environment", list(ENV_CONFIG.keys()))
url = st.text_input("Chatbot Webpage URL")
username = st.text_input("Username")
password = st.text_input("Password", type="password")
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
live_preview = st.checkbox("Enable Live Preview (show browser)")

if st.button("Run Test") and uploaded_file and url and username and password:
    with st.spinner("Running tests... this may take a minute"):
        result_df = run_test(env_name, url, username, password, uploaded_file, live_preview)
        st.success("Testing complete!")
        st.dataframe(result_df)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            result_df.to_excel(tmp.name, index=False)
            st.download_button("Download Results as Excel", data=open(tmp.name, "rb").read(), file_name="test_data_updated.xlsx")
