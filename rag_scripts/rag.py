import boto3
import openai
import ingest
import os
import getpass

class RAGPipeline:
    def __init__(self, provider='bedrock'):
        """Initialize RAG pipeline with specified provider"""
        self.provider = provider
        self.index = ingest.load_index()
        
        if provider == 'bedrock':
            self._setup_bedrock()
        elif provider == 'openai':
            self._setup_openai()
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _setup_bedrock(self):
        """Setup AWS Bedrock with bearer token"""
        # Check for environment variable first
        bearer_token = os.getenv('AWS_BEARER_TOKEN_BEDROCK')
        
        # If not set, prompt user
        if not bearer_token:
            bearer_token = getpass.getpass("Enter AWS Bedrock Bearer Token: ")
        
        # Set environment variable for boto3 to use
        os.environ['AWS_BEARER_TOKEN_BEDROCK'] = bearer_token
        
        # Initialize Bedrock client (uses bearer token from environment)
        self.client = boto3.client("bedrock-runtime", region_name="us-east-1")
        self.model = 'us.anthropic.claude-3-5-sonnet-20241022-v2:0'
        print("Initialized Bedrock client with bearer token")
    
    def _setup_openai(self):
        """Setup OpenAI credentials and client"""
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            api_key = getpass.getpass("Enter OpenAI API Key: ")
        
        self.client = openai.OpenAI(api_key=api_key)
        self.model = 'gpt-3.5-turbo'
        print("Initialized OpenAI client")

    def search(self, query):
        """Search for relevant documents"""
        try:
            boost = {}
            results = self.index.search(
                query=query,
                filter_dict={},
                boost_dict=boost,
                num_results=3
            )
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def build_prompt(self, query, search_results):
        """Build prompt from query and search results"""
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

        context = ""
        for doc in search_results:
            context = context + entry_template.format(**doc) + "\n\n"

        prompt = prompt_template.format(question=query, context=context).strip()
        return prompt

    def llm(self, prompt):
        """Call LLM based on configured provider"""
        if self.provider == 'bedrock':
            return self._call_bedrock(prompt)
        elif self.provider == 'openai':
            return self._call_openai(prompt)
    
    def _call_bedrock(self, prompt):
        """Call AWS Bedrock LLM"""
        messages = [{"role": "user", "content": [{"text": prompt}]}]
        inference_config = {"temperature": 0.1, "topP": 0.9}

        try:
            response = self.client.converse(
                modelId=self.model, 
                messages=messages, 
                inferenceConfig=inference_config
            )
            return response["output"]["message"]["content"][0]["text"]
        except (KeyError, IndexError, TypeError, Exception) as e:
            print(f"Error calling Bedrock: {e}")
            return ""
    
    def _call_openai(self, prompt):
        """Call OpenAI LLM"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling OpenAI: {e}")
            return ""

    def rag(self, query):
        """Main RAG pipeline function"""
        try:
            search_results = self.search(query)
            prompt = self.build_prompt(query, search_results)
            answer = self.llm(prompt)
            return answer
        except Exception as e:
            print(f"RAG pipeline error: {e}")
            return f"Error processing query: {str(e)}"
    
    def debug_search(self, query):
        """Debug search results"""
        results = self.search(query)
        print(f"Query: {query}")
        print(f"Number of results: {len(results)}")
        for i, doc in enumerate(results):
            print(f"Result {i+1}: {doc}")
        return results