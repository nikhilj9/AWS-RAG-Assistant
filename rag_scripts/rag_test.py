# ## Retrieval Evaluation
import pandas as pd
import ingest 

index = ingest.load_index()

df_question = pd.read_csv('data/ground-truth-retrieval.csv')


df_question.head()

ground_truth = df_question.to_dict(orient='records')

ground_truth[0]

def hit_rate(relevance_total):
    cnt = 0

    for line in relevance_total:
        if True in line:
            cnt = cnt + 1

    return cnt / len(relevance_total)

def mrr(relevance_total):
    total_score = 0.0

    for line in relevance_total:
        for rank in range(len(line)):
            if line[rank] == True:
                total_score = total_score + 1 / (rank + 1)

    return total_score / len(relevance_total)

def minsearch_search(query):
    boost = {
        "category": 2.0,
        "tags": 1.5,
        "title": 1.0 
    }

    results = index.search(
        query=query,
        filter_dict={},
        boost_dict=boost,
        num_results=10
    )

    return results

relevance_total = []

def evaluate(ground_truth, search_function):

    for q in tqdm(ground_truth):
        doc_id = q['id']
        results = search_function(q)
        relevance = [d['id'] == doc_id for d in results]
        relevance_total.append(relevance)

    return {
        'hit_rate': hit_rate(relevance_total),
        'mrr': mrr(relevance_total),
    }

from tqdm.auto import tqdm

evaluate(ground_truth, lambda q: minsearch_search(q['question']))

evaluate(ground_truth, lambda q: elastic_search(q['question']))

df_validation = df_question[:100]
df_test = df_question[100:]

gt_val = df_validation.to_dict(orient='records')

def minsearch_search(query, boost=None):
    if boost is None:
        boost = {}

    results = index.search(
        query=query,
        filter_dict={},
        boost_dict=boost,
        num_results=10
    )

    return results

import optuna

SEED = 42  # use only this seed as requested

param_ranges = {
    'category': (0.0, 2.0),
    'tags': (0.0, 1.5),
    'title': (0.0, 1.0),
}

def optuna_objective(trial):

    boost = {}
    for name, (low, high) in param_ranges.items():
        boost[name] = trial.suggest_uniform(name, low, high)

    def search_function(q):
        return minsearch_search(q['question'], boost)

    results = evaluate(gt_val, search_function)

    return results['mrr']

def run_optuna_search(n_trials=20):
    sampler = optuna.samplers.TPESampler(seed=SEED)
    study = optuna.create_study(direction='maximize', sampler=sampler)
    study.optimize(optuna_objective, n_trials=n_trials)

    best_params = study.best_params
    best_value = study.best_value

    best_boost = {k: float(v) for k, v in best_params.items()}

    print("Optuna best MRR:", best_value)
    print("Optuna best boost:", best_boost)

    return best_boost, best_value, study

best_boost, best_value, study = run_optuna_search(n_trials=20)

def minsearch_search(query):
    boost = {
        "category": 0.20,
        "tags": 0.11,
        "title": 0.92
    }

    results = index.search(
        query=query,
        filter_dict={},
        boost_dict=boost,
        num_results=10
    )

    return results

evaluate(ground_truth, lambda q: minsearch_search(q['question']))

df_validation = df_question[:100]
df_test = df_question[100:]

gt_val = df_validation.to_dict(orient='records')

from elasticsearch import Elasticsearch
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

es_client.indices.create(index=index_name, body=index_settings)

def elastic_search(query, boost=None, es_client=None, index_name=None):
    if boost is None:
        boost = {'category': 3.0, 'title': 2.0, 'content': 1.0, 'tags': 3.0}

    fields = []
    for field, weight in boost.items():
        if weight > 0:
            fields.append(f"{field}^{weight}")
        else:
            fields.append(field)
    
    search_query = {
        "size": 5,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": fields,
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


import optuna

SEED = 42  # use only this seed as requested

param_ranges = {
    'category': (0.0, 4.0),   
    'title': (0.0, 4.0),        
    'content': (0.0, 4.0),     
    'tags': (0.0, 4.0),
}

def optuna_objective(trial):

    boost = {}
    for name, (low, high) in param_ranges.items():
        boost[name] = trial.suggest_uniform(name, low, high)

    def search_function(q):
        return elastic_search(q['question'], boost, es_client)

    results = evaluate(gt_val, search_function)

    return results['mrr']

def run_optuna_search(n_trials=20):
    sampler = optuna.samplers.TPESampler(seed=SEED)
    study = optuna.create_study(direction='maximize', sampler=sampler)
    study.optimize(optuna_objective, n_trials=n_trials)

    best_params = study.best_params
    best_value = study.best_value

    best_boost = {k: float(v) for k, v in best_params.items()}

    print("Optuna best MRR:", best_value)
    print("Optuna best boost:", best_boost)

    return best_boost, best_value, study


best_boost, best_value, study = run_optuna_search(n_trials=20)

def elastic_search(query):
    search_query = {
        "size": 5,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ["category^2.6", "title^2.8", "content^1.8", "tags^2.6"],
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

evaluate(ground_truth, lambda q: elastic_search(q['question']))
