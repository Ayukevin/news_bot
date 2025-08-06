import streamlit as st
import pandas as pd
import yaml
from fuzzywuzzy import fuzz
import streamlit as st
from crawler import crawl_blocktempo_news
from nlp_processor import process_dataframe
from news_updater import update_news_data
from analyzer_lda_topic import load_news_data, load_keyword_rules, update_keyword_rules_with_lda, save_keyword_rules

# 讀取新聞資料
@st.cache_data
def load_news_data():
    df = pd.read_csv("news_raw.csv", parse_dates=["time"])
    return df

# 讀取關鍵字規則
@st.cache_data
def load_keyword_rules():
    with open("keyword_rules.yaml", encoding="utf-8") as f:
        rules = yaml.safe_load(f)
    return rules

# 模糊比對文字與所有主題 + 關鍵字
def detect_topic(user_input, keyword_rules, threshold=60):
    best_match_topic = None
    best_score = 0

    for topic, rule in keyword_rules.items():
        all_possible = [topic] + rule['keywords']
        for kw in all_possible:
            score = fuzz.partial_ratio(user_input.lower(), kw.lower())
            if score > best_score and score > threshold:
                best_score = score
                best_match_topic = topic

    return best_match_topic


def retrieve_news_by_topic(news_df, topic, keyword_rules, top_n=5):
    """
    根據傳入主題與 keyword_rules 對應找出新聞：
    1. labels 欄位直接 match 主題
    2. title_cut 欄位是否包含此主題的任一 keyword（字詞級）
    3. 擴展至相同 LDA topic 的新聞
    """
    if topic == "最新消息":
        matched_df = news_df.sort_values(by="time", ascending=False).head(top_n)
        return matched_df
    else:
        # 相關關鍵字
        keywords = keyword_rules.get(topic, {}).get("keywords", [])
        keywords = [topic] + keywords  # 把主題本身也加入查找關鍵列表

        # Step 1: 使用 labels 精準匹配
        label_matches = news_df[news_df['labels'].str.contains(topic, na=False, case=False)]
        # print(label_matches,"1")

        # Step 2: 使用 title_cut 分詞比對 
        def has_any_keyword(row, keywords):
            words = str(row['title_cut']).split()
            return any(kw in words for kw in keywords)

        title_cut_matches = news_df[news_df.apply(lambda row: has_any_keyword(row, keywords), axis=1)]
        # print(title_cut_matches,"2")

        # 進階搜尋:lda topic 擴大搜尋相關字詞
        matched_df = pd.concat([label_matches, title_cut_matches])
        if matched_df.empty:
            matched_lda_topics = matched_df['lda_topic'].dropna().unique()
            if len(matched_lda_topics) > 0:
                lda_expansion_df = news_df[news_df['lda_topic'].isin(matched_lda_topics)]
                matched_df = pd.concat([matched_df, lda_expansion_df])
            # print(matched_df,"3")
        
        
        # Step 3: 去重、排序、回傳
        matched_df = matched_df.drop_duplicates(subset=["title"])
        matched_df = matched_df.sort_values(by="time", ascending=False).head(top_n)
        return matched_df


#  == main ==
st.set_page_config(page_title="新聞對話機器人", page_icon="📰")
st.title("🤖 區塊鍊新聞對話機器人")
st.caption("輸入與新聞主題相關的問題，我會幫你找出最新相關新聞！")
st.caption("機器人所參考之新聞皆來自動驅動區塊鍊新聞網站 (BlockTempo)之區塊鍊商業應用金融市場")

# 載入資料
news_df = load_news_data()
keyword_rules = load_keyword_rules()

# 使用者輸入
user_input = st.text_input("請問你想了解什麼呢？（例如：升息新聞、比特幣價格、通膨怎麼了？）")

if st.button("查詢") or user_input:
    if not user_input.strip():
        st.warning("❗️請輸入一個問題...")
    else:
        # 試圖找出主題
        detected_topic = detect_topic(user_input, keyword_rules)
        
        if detected_topic:
            st.success(f"🎯 偵測到主題: **{detected_topic}**")
            related_news = filtered_news = retrieve_news_by_topic(news_df, detected_topic, keyword_rules)

            if not related_news.empty:
                st.markdown("📰 **以下是相關新聞：**")
                for _, row in related_news.iterrows():
                    title = row['title']
                    time_str = row['time'].strftime('%Y-%m-%d') if pd.notna(row['time']) else "未知"
                    url = row['url']
                    st.markdown(f"- [{title}]({url}) ({time_str})")
            else:
                st.text("😢 找不到相關新聞")
        else:
            st.warning("❗️無法判斷你的提問所對應的主題，請換個問法試試看。")

st.sidebar.title("🛠️ 管理工具")
if st.sidebar.button("📡 更新新聞資料"):
    with st.spinner("正在爬取最新新聞..."):
        raw_news = crawl_blocktempo_news()
        if not raw_news:
            st.warning("⛔ 沒有找到可用的新聞資料")
        else:
            st.success(f"共爬取 {len(raw_news)} 篇新聞，準備進行處理...")
            new_df = process_dataframe(pd.DataFrame(raw_news))
            updated_count = update_news_data(new_df)

            if updated_count == 0:
                st.info("✅ 沒有發現新新聞")
            else:
                st.success(f"✅ 成功新增 {updated_count} 則新聞資料！")

                # 重新更新分類 rules
                with st.spinner("正在更新主題對應的 LDA topic 分類..."):
                    news_df = load_news_data()
                    keyword_rules = load_keyword_rules()
                    updated_rules = update_keyword_rules_with_lda(news_df, keyword_rules)
                    save_keyword_rules(updated_rules)
                    st.success("🔄 keyword_rules.yaml 已自動更新 LDA topic!")

                # 可選：顯示簡要
                with st.expander("📋 內容預覽"):
                    st.dataframe(new_df.head())