import re
import jieba
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

def preprocess(text):
    text = re.sub(r"[^\u4e00-\u9fa5a-zA-Z0-9]", "", str(text))
    tokens = list(jieba.cut(text))
    return " ".join(tokens)

def process_dataframe(df, n_topics=5):
    df["title_cut"] = df["title"].fillna("").map(preprocess)
    vectorizer = CountVectorizer(max_df=0.9, min_df=2)
    X = vectorizer.fit_transform(df["title_cut"])
    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
    lda.fit(X)
    topic_probs = lda.transform(X)
    df["lda_topic"] = topic_probs.argmax(axis=1)
    return df