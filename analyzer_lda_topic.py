import yaml
import pandas as pd

def load_news_data(filepath="news_raw.csv"):
    return pd.read_csv(filepath)

def load_keyword_rules(filepath="keyword_rules.yaml"):
    with open(filepath, encoding="utf-8") as f:
        return yaml.safe_load(f)

def save_keyword_rules(rules, filepath="keyword_rules.yaml"):
    with open(filepath, "w", encoding="utf-8") as f:
        yaml.dump(rules, f, allow_unicode=True)

def analyze_lda_topic_distribution(news_df, keyword_rules, max_lda_per_topic=3):
    """
    自動根據 title_cut + 關鍵字 找出關聯的 lda topic
    回傳一個 dict：{ 主題: [lda topic編號,...] }
    """
    topic_lda_map = {}

    for topic, rule in keyword_rules.items():
        all_keywords = [topic] + rule.get('keywords', [])
        matched_lda_series = pd.Series(dtype="int")

        # 每個關鍵字針對 title_cut 做搜尋
        for kw in all_keywords:
            matched_df = news_df[news_df['title_cut'].str.contains(kw, na=False, case=False)]
            matched_lda_series = pd.concat([matched_lda_series, matched_df['lda_topic']])

        # 統計出現次數最多的 LDA topics
        lda_counts = matched_lda_series.value_counts()
        top_lda = lda_counts.head(max_lda_per_topic).index.tolist()
        topic_lda_map[topic] = top_lda

    return topic_lda_map

def update_keyword_rules_with_lda(news_df, keyword_rules):
    topic_lda_map = analyze_lda_topic_distribution(news_df, keyword_rules)

    # 更新到原規則中
    for topic, lda_list in topic_lda_map.items():
        keyword_rules[topic]["lda_topics"] = lda_list

    return keyword_rules  # 回傳更新後規則（可寫入）
