import pandas as pd

def update_news_data(new_data, file_path="news_raw.csv"):
    try:
        old_df = pd.read_csv(file_path)
    except FileNotFoundError:
        old_df = pd.DataFrame(columns=["title", "url", "labels", "time", "title_cut", "lda_topic"])

    old_titles = set(old_df["title"].tolist())
    new_df = pd.DataFrame(new_data)

    # 過濾重複新聞
    filtered_df = new_df[~new_df["title"].isin(old_titles)]

    if filtered_df.empty:
        return 0  # 無新增資料

    # 回傳新增筆數 + 合併儲存
    combined_df = pd.concat([old_df, filtered_df], ignore_index=True)
    combined_df.to_csv(file_path, index=False, encoding="utf-8")

    return len(filtered_df)