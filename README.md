# crypto_newsbot

這是一個基於 Python + Streamlit 的互動式新聞查詢系統，整合了新聞爬蟲、自動更新、中文斷詞 (Jieba)、LDA 主題分析、模糊匹配查詢等模組，能夠根據使用者輸入主題，自動推薦最相關的區塊鏈相關新聞。

---

## 架構設計與功能模組

| 模組名稱                                     | 功能說明                                         |
| -------------------------------------------- | ------------------------------------------------ |
| `crawler.py`（Crawler）                    | 自動爬取動區新聞網站（Blocktempo），收集最新資料 |
| `news_updater.py`（News Updater）          | 比較資料表並新增新新聞項目                       |
| `nlp_processor.py`（NLP Processor）        | 使用 jieba 斷詞、TF-IDF 特徵抽取與 LDA 主題分類  |
| `analyzer_lda_topic.py`（LDA-YAML 同步器） | 自動更新主題與 LDA topic 對應關係至 YAML         |
| `app.py`（Streamlit UI）                   | 對話式使用者互動介面，查詢新聞與觸發更新流程     |

---

## 使用者互動流程

1. 使用者輸入一段查詢語句（例：「升息怎麼了」、「比特幣漲了嗎」）
2. 系統使用關鍵字規則與模糊比對，判斷意圖主題
3. 從新聞資料表中，先比對 `label`，再以 `title_cut` 模糊查找，最後擴展至對應的 `lda_topic`
4. 系統依據時間排序，展示最新相關新聞（包含標題、連結、日期）
5. 使用者也可按下「📡 更新新聞資料」按鈕，自動爬取並新增未收錄的新新聞，並重新分析斷詞與 LDA 主題

---

## 技術使用

- **多層級主題擷取邏輯**：labels ➜ title_cut ➜ LDA topic
- **模糊輸入容錯能力**（如：「市場情緒」、「通膨趨勢」 ➜ 成功對應主題）
- **新聞自動更新按鈕（非同步爬蟲 ➜ NLP ➜ 存檔）**
- **自動維護 YAML 知識庫分類**（主題 ➜ 關鍵字 ➜ LDA topics）
- **模組化設計，易於擴充新網站、新主題、新模型**
- **部署於 Streamlit 可雲端分享**

---

## 專案安裝與執行方式

```bash
pip install -r requirements.txt
streamlit run app.py
```

※本程式所擷取之新聞資料來源為[Blocktempo 動區新聞](https://www.blocktempo.com/category/business/finance-market/)，新聞內容僅用於 AI 自然語言應用展示，不做為商業用途或再次分發使用。若新聞來源網站對資料使用有異議，請聯繫開發者，我們將立即配合下架。
