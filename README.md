# AWS-RAG-Assistant

This project is an LLM-based application using RAG (Retrieval-Augmented Generation) with a knowledge base on AWS Bedrock services. It enables users to query and get accurate, contextual answers through natural language prompts. The system supports multiple LLM providers including AWS Bedrock and OpenAI with secure credential management.

## Problem Description

Organizations and developers working with AWS Bedrock face critical challenges when seeking service information. AWS Bedrock documentation encompasses multiple foundation models, implementation approaches, and integration patterns, making it difficult to understand optimal model selection and configuration for specific use cases. 

The AWS-RAG-Assistant addresses these challenges by providing a unified conversational interface that instantly retrieves and synthesizes relevant AWS Bedrock information, eliminating complex documentation navigation and accelerating development workflows.

## Features

- **Multi-Provider Support**: Works with both AWS Bedrock and OpenAI
- **Secure Credentials**: Environment variables or secure runtime prompts
- **RAG Pipeline**: Retrieval-augmented generation for accurate responses
- **REST API**: Flask-based API for easy integration
- **AWS Bedrock Focus**: Specialized knowledge base for AWS Bedrock services

## Dataset

The dataset contains comprehensive information about AWS Bedrock services including model names, capabilities, use cases, technical specifications, pricing models, integration points, implementation examples, best practices, and security features. 

You can find the data in `data/AWSBedrockRAG.json` with 450+ comprehensive records covering AWS Bedrock foundation models and associated services.

## Technologies

- **Python 3.12**: Primary programming language
- **Minsearch**: Full-text search with custom boosting
- **AWS Bedrock**: Claude 3.5 Sonnet model for language processing
- **OpenAI**: GPT-3.5-turbo as alternative provider
- **Flask**: REST API interface
- **boto3**: AWS SDK for Python

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd aws-rag-assistant
```

2. **Install dependencies**
```bash
pip install boto3 flask pandas minsearch openai
```

3. **Prepare your credentials** (choose one method):

**Option A: Environment Variables**
```bash
export AWS_BEARER_TOKEN_BEDROCK="your_bedrock_bearer_token"
export OPENAI_API_KEY="your_openai_api_key"
```

**Option B: Runtime Input** (credentials will be prompted securely when you run the app)

## Running the Application

### Start the Server

**With AWS Bedrock:**
```bash
python app.py --provider bedrock
```

**With OpenAI:**
```bash
python app.py --provider openai
```

The Flask API will be available at `http://localhost:5000`

### Using the API

**Send a question via curl:**
```bash
curl -X POST \
    -H "Content-Type: application/json" \
    -d '{"question": "How to use agents in bedrock?"}' \
    http://localhost:5000/question
```

**Example Response:**
```json
{
    "conversation_id": "uuid-here",
    "question": "How to use agents in bedrock?",
    "answer": "AWS Bedrock Agents allow you to..."
}
```

**Send feedback:**
```bash
curl -X POST \
    -H "Content-Type: application/json" \
    -d '{"conversation_id": "your-conversation-id", "feedback": 1}' \
    http://localhost:5000/feedback
```

## Code Structure

```
aws-rag-assistant/
├── app.py          # Flask API server with CLI argument parsing
├── rag.py          # RAG pipeline with multi-provider support
├── ingest.py       # Document ingestion and indexing
├── data/           # AWS Bedrock knowledge base
│   └── AWSBedrockRAG.json
└── README.md
```

### Key Components

- **`app.py`**: Flask web server with provider selection via CLI arguments
- **`rag.py`**: RAGPipeline class handling both Bedrock and OpenAI providers
- **`ingest.py`**: Loads and indexes the AWS Bedrock knowledge base

## Configuration Options

### Provider Selection
- `--provider bedrock`: Use AWS Bedrock Claude 3.5 Sonnet
- `--provider openai`: Use OpenAI GPT-3.5-turbo

### Credential Management
1. **Environment Variables** (recommended for production)
2. **Runtime Prompts** (secure masked input for development)

### Search Configuration
The system uses optimized search parameters for AWS Bedrock queries with custom field boosting for better retrieval accuracy.

## Security Features

- **No Hardcoded Credentials**: All secrets managed via environment or secure input
- **Masked Input**: Credentials are hidden when entered at runtime
- **Environment Priority**: Checks environment variables before prompting
- **Secure Token Handling**: AWS Bearer Token properly managed

## Example Queries

Try these sample questions:
- "What are the available foundation models in AWS Bedrock?"
- "How do I implement RAG with Bedrock?"
- "What's the pricing for Claude models?"
- "How to fine-tune models in Bedrock?"
- "What are Bedrock Agents and how do they work?"

## Troubleshooting

### Common Issues

**"No credentials found"**
- Ensure environment variables are set or be ready to enter them when prompted

**"Provider not supported"**
- Use `--provider bedrock` or `--provider openai`

**"Connection errors"**
- Verify your credentials are valid and have proper permissions

### Debug Mode
The Flask app runs in debug mode by default for development. For production, modify the `app.run()` call in `app.py`.

## Future Development

Future iterations will expand the knowledge base to include comprehensive coverage of additional AWS services including compute, storage, database, networking, and security services, transforming the system into a comprehensive AWS service assistant.

## Acknowledgements

Thanks to the LLM Zoomcamp course and its sponsors for making this educational opportunity available. This project demonstrates practical RAG applications in technical documentation scenarios with multi-provider LLM support and secure credential management.