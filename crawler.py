import requests
from bs4 import BeautifulSoup

def crawl_blocktempo_news(page_count=3):
    base_url = "https://www.blocktempo.com/category/business/finance-market/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    results = []

    for page in range(1, page_count + 1):
        if page == 1:
            url = base_url
        else:
            url = f"{base_url}page/{page}/"

        print(f"📄 正在抓取：{url}")
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"⚠️ 無法取得第 {page} 頁 (status code: {response.status_code})，略過。")
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        # 每篇文章封裝在 article.blockArticle 裡
        articles = soup.select("article.jeg_post")

        for article in articles:
            try:
                title_tag = article.select_one("h3.jeg_post_title > a")
                title = title_tag.text.strip()
                link = title_tag["href"]

                date_tag = article.select_one(".jeg_meta_date")
                time = date_tag.text.strip() if date_tag else ""

                label_tag = article.select_one(".jeg_post_category")
                labels = label_tag.text.strip() if label_tag else ""

                results.append({
                    "title": title,
                    "url": link,
                    "labels": labels,
                    "time": time
                })
            except Exception as e:
                print("⚠️ 擷取失敗：", e)
                continue

    return results