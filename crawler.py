from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def crawl_blocktempo_news(pages=5):
    url = "https://www.blocktempo.com/category/business/finance-market/"
    service = ChromeService(ChromeDriverManager().install())

    chrome_option = Options()
    chrome_option.add_argument("--headless")  # 無頭執行，不開瀏覽器
    chrome_option.add_argument("--disable-gpu")
    prefs = {"profile.default_content_setting_values.notifications": 2}
    chrome_option.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(service=service, options=chrome_option)
    results = []

    try:
        for page in range(1, pages + 1):
            driver.get(url + f"page/{page}/")
            driver.implicitly_wait(10)
            articles = driver.find_elements(By.XPATH, "//article")
            for article in articles:
                try:
                    a_tag = article.find_element(By.XPATH, ".//h3[@class='jeg_post_title']/a")
                    title = a_tag.text.strip()
                    link = a_tag.get_attribute("href")
                    time = article.find_element(By.XPATH, ".//div[contains(@class, 'jeg_meta_date')]").text
                    labels = article.find_element(By.XPATH, ".//div[contains(@class, 'jeg_post_category')]").text
                    results.append({'title': title, 'url': link, 'labels': labels, 'time': time})
                except Exception:
                    continue
    finally:
        driver.quit()

    return results