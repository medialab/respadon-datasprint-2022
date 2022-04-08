import pandas as pd
import json
import csv
import re
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

tokeniser = RegexpTokenizer(r"w+")


def rem_en(input_txt):
    input_txt = str(input_txt)
    input_txt = re.sub(r"[^\w\s]", "", input_txt)
    words = str(input_txt).lower().split()
    noise_free_words = [word for word in words if word not in stop]
    noise_free_text = " ".join(noise_free_words)
    return noise_free_text


with open("./ignored_data/solrwayback_2022-04-07-15-02-17_WITH_CONTENT.csv") as file:
    responses = csv.DictReader(file)

    df = pd.read_csv(file)
    df["content"] = df["content"].str.lower()

    stop = set(stopwords.words("french")) | set(stopwords.words("english"))

    df["clean_text"] = df["content"].apply(lambda s: rem_en(s))

    from sklearn.feature_extraction.text import TfidfVectorizer

    tfidf = TfidfVectorizer()
    X_tfidf = tfidf.fit_transform(df["clean_text"]).toarray()
    vocab = tfidf.vocabulary_
    reverse_vocab = {v: k for k, v in vocab.items()}

    feature_names = tfidf.get_feature_names()
    df_tfidf = pd.DataFrame(X_tfidf, columns=feature_names)

    idx = X_tfidf.argsort(axis=1)

    tfidf_max10 = idx[:, -10:]

    df_tfidf["top10"] = [
        [reverse_vocab.get(item) for item in row] for row in tfidf_max10
    ]

    print(df_tfidf["top10"])
    df["top10"] = df_tfidf["top10"]
    df.to_csv(
        "elections_top10.csv",
        columns=[
            "domain",
            "id",
            "url",
            "top10",
        ],
    )
