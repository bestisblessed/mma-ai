from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

service = Service(executable_path='/usr/lib/chromium-browser/chromedriver')
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get("https://www.pinnacle.com/en/mixed-martial-arts/matchups/")
driver.implicitly_wait(5)

# Append current date to file name
file_name = f"./data/raw.html"

with open(file_name, "w", encoding="utf-8") as file:
    file.write(driver.page_source)

driver.quit()



