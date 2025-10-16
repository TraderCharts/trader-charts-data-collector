import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import SELENIUM_TIMEOUT, CHROME_WINDOW_SIZE, SELENIUM_HEADLESS

class SeleniumClient:
    def __init__(self, download_dir: str):
        self.download_dir = os.path.abspath(download_dir)
        os.makedirs(self.download_dir, exist_ok=True)

        options = Options()
        options.add_argument("--headless" if SELENIUM_HEADLESS else "")
        options.add_argument("--disable-gpu")
        options.add_argument(f"--window-size={CHROME_WINDOW_SIZE}")

        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)

        self.driver = webdriver.Chrome(service=Service(), options=options)
        self.wait = WebDriverWait(self.driver, SELENIUM_TIMEOUT)

    def quit(self):
        if self.driver:
            self.driver.quit()

    def get_page(self, url: str):
        self.driver.get(url)

    def click_download_button(self):
        element = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#Coti-hist-c .download button"))
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)
        self.driver.execute_script("arguments[0].click();", element)

    def wait_for_new_file(self, previous_files: set):
        timeout = 30
        while timeout > 0:
            csv_files = [f for f in os.listdir(self.download_dir) if f.endswith(".csv")]
            new_files = [f for f in csv_files if f not in previous_files]
            if new_files:
                new_files.sort(
                    key=lambda f: os.path.getctime(os.path.join(self.download_dir, f)),
                    reverse=True
                )
                candidate = os.path.join(self.download_dir, new_files[0])
                if not candidate.endswith(".crdownload"):
                    return candidate
            time.sleep(1)
            timeout -= 1
        raise FileNotFoundError("No new CSV downloaded.")
