# AWS-RAG-Assistant

An intelligent conversational assistant built with Retrieval-Augmented Generation (RAG) that provides expert-level answers about AWS Bedrock services. This system combines the power of semantic search with large language models to deliver accurate, contextual responses about AWS Bedrock foundation models, implementation patterns, and best practices.

##  Features

- **Multi-Provider LLM Support**: Choose between AWS Bedrock (Nova Micro) or OpenAI (GPT-4.1 Nano)
- **Intelligent Document Retrieval**: Advanced search through 450+ AWS Bedrock knowledge records
- **Docker-Ready Deployment**: One-command containerized setup
- **RESTful API**: Clean Flask-based API for easy integration
- **Secure Credential Management**: Environment-based configuration
- **Real-time Health Monitoring**: Built-in health checks and error handling

##  Problem It Solves

AWS Bedrock offers numerous foundation models and implementation approaches, making it challenging to find the right information quickly. This assistant eliminates the need to navigate through complex documentation by providing instant, accurate answers through natural conversation.

##  Prerequisites

Before getting started, ensure you have:

- Docker and Docker Compose installed on your system
- An active API key from either:
  - **AWS Bedrock**: Access through AWS Console with Nova model permissions
  - **OpenAI**: API key from [OpenAI Platform](https://platform.openai.com/api-keys)

##  Installation & Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/nikhilj9/AWS-RAG-Assistant.git
cd AWS-RAG-Assistant
```

### Step 2: Configure Environment Variables

Create a `.env` file in the project root directory:

```bash
# Copy the template
cp env_template .env
```

Edit the `.env` file with your credentials:

```env
# For AWS Bedrock
AWS_BEARER_TOKEN_BEDROCK=your_actual_bedrock_bearer_token

# For OpenAI
OPENAI_API_KEY=your_actual_openai_api_key
```

### Step 3: Launch the Application

Choose your preferred LLM provider:

**Option A: AWS Bedrock (Port 5000)**
```bash
docker-compose --profile bedrock up --build
```

**Option B: OpenAI (Port 5001)**
```bash
docker-compose --profile openai up --build
```

### Step 4: Verify Installation

Test the health endpoint:

```bash
# For Bedrock
curl http://localhost:5000/health

# For OpenAI  
curl http://localhost:5001/health
```

Expected response:
```json
{
  "status": "healthy",
  "provider": "bedrock"
}
```

##  Using the API

### Ask a Question

Send questions about AWS Bedrock:

```bash
curl -X POST http://localhost:5000/question \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the key features of Amazon Nova models in Bedrock?"
  }'
```

Response format:
```json
{
  "conversation_id": "uuid-string",
  "question": "What are the key features of Amazon Nova models in Bedrock?",
  "answer": "Amazon Nova models in AWS Bedrock offer multimodal capabilities..."
}
```

### Submit Feedback

Provide feedback on responses:

```bash
curl -X POST http://localhost:5000/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "your-conversation-id",
    "feedback": 1
  }'
```

Feedback values: `1` (helpful) or `-1` (not helpful)

##  Project Structure

```
AWS-RAG-Assistant/
├──  README.md                 # Project documentation
├──  Dockerfile                # Container configuration
├──  docker-compose.yml        # Multi-service orchestration
├──  requirements.txt          # Python dependencies
├──  env_template              # Environment variables template
├──  data/
│   └── AWSBedrockRAG.json     # Knowledge base (450+ records)
└──  rag_scripts/
    ├── app.py                 # Flask API server
    ├── rag.py                 # RAG pipeline implementation
    └── ingest.py              # Document indexing
```

##  Configuration Options

### Model Selection

| Provider | Model | Port |
|----------|-------|------|
| AWS Bedrock | amazon.nova-micro-v1:0 | 5000 |
| OpenAI | gpt-4.1-nano-2025-04-14 | 5001 |

### Environment Variables

| Variable | Description | Required For |
|----------|-------------|--------------|
| `AWS_BEARER_TOKEN_BEDROCK` | AWS Bedrock authentication | Bedrock provider |
| `OPENAI_API_KEY` | OpenAI API access key | OpenAI provider |

##  Example Queries

Try these sample questions:

- `"How do I implement RAG with AWS Bedrock?"`
- `"What's the difference between Claude and Nova models?"`
- `"How do Bedrock Agents work?"`
- `"What are the pricing models for foundation models?"`
- `"How to fine-tune models in Bedrock?"`

##  Troubleshooting

### Common Issues & Solutions

####  Authentication Errors

**Error**: `ValueError: AWS_BEARER_TOKEN_BEDROCK environment variable is required`

**Solution**:
1. Verify your `.env` file exists in the project root
2. Check that credentials are properly set (no quotes needed)
3. Restart the container after updating credentials

```bash
# Check your .env file
cat .env

# Restart with fresh build
docker-compose --profile bedrock down
docker-compose --profile bedrock up --build
```

####  Docker Issues

**Error**: `Container exits immediately`

**Solution**:
```bash
# View container logs for details
docker logs rag-bedrock_compose

# Common fixes:
docker system prune -f        # Clean Docker cache
docker-compose down --volumes # Remove volumes
docker-compose --profile bedrock up --build
```

**Error**: `Port already in use`

**Solution**:
```bash
# Find and stop conflicting processes
lsof -i :5000
kill -9 <PID>

# Or use different ports in docker-compose.yml
```

####  API Connection Issues

**Error**: `Connection refused`

**Solutions**:
1. **Wait for startup**: Containers need 30-60 seconds to fully initialize
2. **Check logs**: `docker logs rag-bedrock_compose`
3. **Verify port**: Bedrock uses 5000, OpenAI uses 5001

**Error**: `"No question provided"`

**Solution**: Ensure proper JSON format:
```bash
#  Correct format
curl -X POST http://localhost:5000/question \
  -H "Content-Type: application/json" \
  -d '{"question": "your question here"}'

#  Common mistake - missing Content-Type header
```

####  Model Access Issues

**AWS Bedrock Error**: `AccessDeniedException`

**Solution**:
1. Go to AWS Console → Bedrock → Model Access
2. Enable access for `amazon.nova-micro-v1:0`
3. Wait 5-10 minutes for permission propagation

**OpenAI Error**: `Invalid API key`

**Solution**:
1. Verify key format: `sk-...` (starts with sk-)
2. Check key permissions at OpenAI platform
3. Regenerate key if necessary

##  Manual Installation (Alternative)

If you prefer running without Docker:

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export AWS_BEARER_TOKEN_BEDROCK="your_token"
export OPENAI_API_KEY="your_key"

# Navigate to application directory
cd rag_scripts

# Run with your preferred provider
python app.py --provider bedrock  # or openai
```

##  Monitoring & Logs

### View Application Logs

```bash
# Real-time logs
docker logs -f rag-bedrock_compose

# Last 50 lines
docker logs --tail 50 rag-bedrock_compose
```

### Health Monitoring

The `/health` endpoint provides system status:
- Service availability
- Provider configuration  
- Model connectivity

##  Stopping the Application

```bash
# Stop Bedrock service
docker-compose --profile bedrock down

# Stop OpenAI service
docker-compose --profile openai down

# Stop and remove volumes
docker-compose down --volumes
```

##  Technology Stack

- **Backend**: Python 3.11, Flask
- **Search**: Minsearch with TF-IDF ranking
- **LLMs**: AWS Bedrock Nova Micro, OpenAI GPT-4.1 Nano
- **Containerization**: Docker, Docker Compose
- **Data Processing**: Pandas, JSON

##  Dataset Information

The knowledge base contains comprehensive AWS Bedrock information:
- **Records**: 450+ detailed entries
- **Coverage**: Foundation models, pricing, implementation guides
- **Format**: Structured JSON with semantic fields
- **Updates**: Regularly maintained for accuracy

## Contributing

We welcome contributions! Areas for improvement:
- Additional AWS services coverage
- Enhanced search algorithms  
- UI/frontend development
- Performance optimizations

## Future Development

Future iterations will expand the knowledge base to include comprehensive coverage of additional AWS services including compute, storage, database, networking, and security services, transforming the system into a comprehensive AWS service assistant.

## Acknowledgements

Thanks to the LLM Zoomcamp course and its sponsors for making this educational opportunity available. This project demonstrates practical RAG applications in technical documentation scenarios with multi-provider LLM support and secure credential management.

## License

This project is open source and available under the MIT License.

**Built with ❤️ for the AWS community**