import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import chromedriver_autoinstaller

def run_test(env_name, url, username, password, file, live_preview=False):
    df = pd.read_excel(file)

    chromedriver_autoinstaller.install()
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
        driver.find_element(By.ID, "userID").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.CLASS_NAME, "btn-dark").click()
        time.sleep(5)
        driver.get(url)
        time.sleep(20)
        driver.find_element(By.CLASS_NAME, "chatButtonBG").click()
        time.sleep(10)

        for _, row in df.iterrows():
            question = row["Question"]
            expected_answer = row["ExpectedAnswer"]
            expected_link = str(row["ExpectedLink"]).strip()

            prev_resp = driver.find_elements(By.CSS_SELECTOR, ".leftmsg")
            prev_text = prev_resp[-1].text if prev_resp else ""

            chat_input = driver.find_element(By.CSS_SELECTOR, ".enterKeyDetect")
            chat_input.send_keys(question + Keys.RETURN)

            for _ in range(30):
                time.sleep(1)
                new_resp = driver.find_elements(By.CSS_SELECTOR, ".leftmsg")
                if new_resp and new_resp[-1].text != prev_text:
                    break

            last_text = new_resp[-1].text.strip() if new_resp else "[No response]"
            try:
                link = new_resp[-1].find_element(By.TAG_NAME, "a").get_attribute("href").strip()
            except:
                link = "[No link found]"

            pass_answer = expected_answer in last_text
            pass_link = expected_link in link if env_name == "Cog Search" else True
            result = "✅ PASS" if pass_answer and pass_link else "❌ FAIL"

            results.append({
                "Question": question,
                "ExpectedAnswer": expected_answer,
                "ExpectedLink": expected_link,
                "BotResponse": last_text,
                "ExtractedLink": link,
                "Result": result
            })

    finally:
        driver.quit()

    return pd.DataFrame(results)
