import pandas as pd

import minsearch

def load_index():
    data_path='../data/AWSBedrockRAG.json'
    df = pd.read_json(data_path)

    documents = df.to_dict(orient="records")

    index = minsearch.Index(
        text_fields = ['service', 'category', 'title', 'content'],
        keyword_fields = ['tags']
    )

    index.fit(documents)
    return index