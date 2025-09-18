import boto3
import pandas as pd

from elasticsearch import Elasticsearch
from tqdm.auto import tqdm

es_client = Elasticsearch('http://localhost:9200') 

index_settings = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "service": {"type": "text"},
            "category": {"type": "text"},
            "title": {"type": "text"},
            "content": {"type": "text"},
            "tags": {"type": "keyword"}
        }
    }
}

index_name = "bedrock_knowledge_base"

es_client.indices.delete(index=index_name, body=index_settings)
es_client.indices.create(index=index_name, body=index_settings)

data_path = '../data/AWSBedrockRAG.json'
documents = pd.read_json(data_path)

for doc in tqdm(documents):
    es_client.index(index=index_name, document=doc)

def elastic_search(query):
    search_query = {
        "size": 5,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ["category^3", "title^2", "content", "tags^3"],
                        "type": "best_fields"
                    }
                },
                "filter": {
                    "match": {
                        "service": "Amazon Bedrock"
                    }
                }
            }
        }
    }

    response = es_client.search(index=index_name, body=search_query)
    
    result_docs = []
    
    for hit in response['hits']['hits']:
        result_docs.append(hit['_source'])
    
    return result_docs

prompt_template = """
You're a aws expert. Answer the QUESTION based on the CONTEXT from our aws core service database.
Use only the facts from the CONTEXT when answering the QUESTION.

QUESTION: {question}

CONTEXT:
{context}
""".strip()

entry_template = """
id: {id}
service: {service}
category: {category}
title: {title}
content: {content}
tags: {tags}
""".strip()

def build_prompt(query, search_results):
    context =""

    for doc in search_results:
        context = context + entry_template.format(**doc) + "\n\n"

    prompt = prompt_template.format(question=query, context=context).strip()
    return prompt

def llm(prompt, model):
    client = boto3.client("bedrock-runtime", region_name="us-east-1")

    messages = [{"role": "user", "content": [{"text": prompt}] }]

    inference_config = {"temperature": 0.1, "topP": 0.9}

    response = client.converse(modelId=model, messages=messages, inferenceConfig=inference_config)
    
    try:
        return response["output"]["message"]["content"][0]["text"]
    except (KeyError, IndexError, TypeError):
        return ""

def rag(query, model_id):
    search_results = elastic_search(query)
    prompt = build_prompt(query, search_results)
    #print(prompt)
    answer = llm(prompt, model_id)
    return answer


query = "Tell me use of agents and its type."
model_id = "amazon.nova-micro-v1:0"
answer = rag(query, model_id)
print(answer)