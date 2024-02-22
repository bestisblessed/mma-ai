from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

driver = webdriver.Chrome(options=chrome_options)

driver.get("https://data.vsin.com/vegas-odds-linetracker/?sportid=ufc&linetype=moneyline")

driver.implicitly_wait(5)

with open("./data/odds_VSiN.html", "w", encoding="utf-8") as file:
    file.write(driver.page_source)

driver.quit()
