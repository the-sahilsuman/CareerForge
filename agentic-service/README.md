# 🤖 CareerForge Agentic Service

The **CareerForge Agentic Service** is the AI and document-intelligence service of the CareerForge platform.

It is responsible for document ingestion, parsing, chunking, embeddings, vector storage, semantic retrieval, AI agents, LLM interaction, job-description analysis, career assistance, and AI evaluation.

Built with **FastAPI, LangChain, LangGraph, AWS services, vector search, and configurable LLM/embedding providers**.

---

## 📌 Table of Contents

* [Overview](#-overview)
* [Responsibilities](#-responsibilities)
* [Architecture](#-architecture)
* [Technology Stack](#-technology-stack)
* [Project Structure](#-project-structure)
* [AI Architecture](#-ai-architecture)
* [RAG Pipeline](#-rag-pipeline)
* [Document Ingestion](#-document-ingestion)
* [Embeddings](#-embeddings)
* [Vector Store](#-vector-store)
* [Retrieval](#-retrieval)
* [Agent Architecture](#-agent-architecture)
* [Career Assistant](#-career-assistant)
* [Job Description Analysis](#-job-description-analysis)
* [Email Generation](#-email-generation)
* [SQS Worker](#-sqs-worker)
* [Redis Memory](#-redis-memory)
* [LLM Providers](#-llm-providers)
* [Environment Variables](#-environment-variables)
* [Installation](#-installation)
* [Running](#-running)
* [Testing](#-testing)
* [Evaluation](#-evaluation)
* [Monitoring](#-monitoring)
* [Troubleshooting](#-troubleshooting)
* [Security](#-security)

---

# 🎯 Overview

The Agentic Service provides the AI capabilities of CareerForge.

The Core Backend manages business data and application APIs.

The Agentic Service manages:

```text
AI
RAG
Embeddings
Document Processing
Vector Search
Agents
LLMs
AI Evaluation
```

---

# ✨ Responsibilities

## Document Processing

* PDF loading
* Text extraction
* Chunking
* Metadata generation

## Embeddings

* Generate document embeddings
* Generate query embeddings
* Support configurable embedding providers

## Vector Search

* Store vectors
* Query vectors
* Retrieve relevant chunks
* Delete vectors

## AI

* Career assistant
* Job description analysis
* Profile matching
* Resume analysis
* Email generation

## Background Processing

* SQS consumption
* Document ingestion
* Embedding generation
* Vector indexing

---

# 🏗️ Architecture

```text
                       Core Backend
                            │
                            ▼
                    Agentic Service
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
     Ingestion           Retrieval          Agent
          │                 │                 │
          ▼                 ▼                 ▼
       Parser         S3 Vectors            LLM
          │                 │                 │
          ▼                 └────────┬────────┘
      Chunking                       │
          │                          ▼
          ▼                     AI Response
      Embeddings
          │
          ▼
     S3 Vectors
```

---

# 🛠️ Technology Stack

| Technology     | Purpose                |
| -------------- | ---------------------- |
| Python         | Application language   |
| FastAPI        | API service            |
| LangChain      | LLM/RAG framework      |
| LangGraph      | Agent orchestration    |
| PostgreSQL     | Persistent metadata    |
| Redis          | Temporary memory/cache |
| S3             | Document storage       |
| S3 Vectors     | Vector storage         |
| SQS            | Async ingestion        |
| Amazon Bedrock | LLM/embeddings         |
| Google Gemini  | LLM/embeddings         |
| Hugging Face   | LLM/embeddings         |
| DeepEval       | Evaluation             |
| LangSmith      | AI tracing             |

---

# 📁 Project Structure

```text
agentic-service/
│
├── app/
│   │
│   ├── clients/
│   │   └── bedrock.py
│   │
│   ├── core/
│   │   └── config.py
│   │
│   ├── ingestion/
│   │
│   ├── parsers/
│   │
│   ├── queue/
│   │
│   ├── repositories/
│   │
│   ├── retrieval/
│   │
│   ├── storage/
│   │
│   ├── vector_store/
│   │   └── s3_vectors.py
│   │
│   ├── workers/
│   │   └── ingestion_worker.py
│   │
│   └── main.py
│
├── scripts/
│   ├── test_langchain_ingestion.py
│   └── test_langchain_embeddings.py
│
├── tests/
│
├── pyproject.toml
├── uv.lock
└── README.md
```

---

# 🧠 AI Architecture

The Agentic Service follows a layered architecture:

```text
                    API Layer
                       │
                       ▼
                 Agent Layer
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
        Retrieval              Tools
             │                   │
             ▼                   ▼
        Vector Store           Services
             │
             ▼
        Context Builder
             │
             ▼
             LLM
```

---

# 📚 RAG Pipeline

CareerForge uses Retrieval-Augmented Generation.

```text
                  DOCUMENT
                     │
                     ▼
                 S3 Storage
                     │
                     ▼
               Document Loader
                     │
                     ▼
                  Parser
                     │
                     ▼
                 Text
                     │
                     ▼
                 Chunking
                     │
                     ▼
                Embeddings
                     │
                     ▼
                S3 Vectors
```

At query time:

```text
User Question
      │
      ▼
Query Embedding
      │
      ▼
S3 Vector Search
      │
      ▼
Relevant Chunks
      │
      ▼
Context Builder
      │
      ▼
LLM
      │
      ▼
Response
```

---

# 📄 Document Ingestion

The ingestion pipeline is asynchronous.

```text
Resume Upload
      │
      ▼
S3
      │
      ▼
Event
      │
      ▼
SQS
      │
      ▼
Ingestion Worker
      │
      ▼
Download Document
      │
      ▼
Parse
      │
      ▼
Chunk
      │
      ▼
Embed
      │
      ▼
S3 Vectors
```

This prevents the user-facing upload API from waiting for the entire embedding process.

---

# 🧩 Document Parsing

PDF documents can be processed using LangChain loaders.

Example:

```text
PDF
 ↓
PyPDFLoader
 ↓
Pages
 ↓
Text
```

Text is then passed to the chunking layer.

---

# ✂️ Chunking

Large documents are divided into smaller chunks.

A recursive text splitter can be used:

```text
RecursiveCharacterTextSplitter
```

The goal is to create chunks that are:

* Small enough for retrieval
* Large enough to preserve context
* Consistent across documents

---

# 🔢 Embeddings

Embeddings transform text into numerical vectors.

```text
Text
 ↓
Embedding Model
 ↓
[0.12, -0.43, 0.91, ...]
```

CareerForge supports configurable providers.

Possible providers:

```text
Amazon Bedrock
Google Gemini
Hugging Face
```

---

# ⚠️ Embedding Dimensions

The vector dimension must match the vector index.

Example:

```text
Embedding Model
      │
      ▼
1024 dimensions
      │
      ▼
S3 Vector Index
      │
      ▼
1024 dimensions
```

If the embedding provider changes:

```text
1024 → 3072
```

the existing vector index may no longer be compatible.

Always verify:

```text
Configured Dimension
=
Actual Embedding Dimension
=
Vector Index Dimension
```

---

# 🗃️ S3 Vector Store

CareerForge uses Amazon S3 Vectors for semantic search.

Implementation:

```text
app/vector_store/s3_vectors.py
```

The vector store layer should abstract AWS-specific operations from the rest of the application.

Core operations include:

```text
Get Index
Put Vectors
Query Vectors
Get Vectors
Delete Vectors
```

---

# 🔎 Retrieval

The retrieval pipeline:

```text
Query
 ↓
Query Embedding
 ↓
S3 Vector Search
 ↓
Top-K Results
 ↓
Metadata Filtering
 ↓
Relevant Context
```

Retrieved information is then passed to the generation layer.

---

# 🤖 Agent Architecture

LangGraph can be used to orchestrate agent workflows.

A simplified graph:

```text
                   START
                     │
                     ▼
               Understand Query
                     │
                     ▼
                Route Query
                /     |      \
               /      |       \
              ▼       ▼        ▼
          Retrieval  Profile  Email
              │        │        │
              └────────┼────────┘
                       ▼
                  Build Context
                       │
                       ▼
                      LLM
                       │
                       ▼
                    Response
                       │
                       ▼
                      END
```

---

# 💬 Career Assistant

The Career Assistant can answer questions using the user's career context.

Example:

```text
User:
"What projects should I mention for this backend role?"
```

The system can retrieve:

```text
Projects
Experience
Skills
Resume
Job Description
```

and provide contextual assistance.

---

# 💼 Job Description Analysis

A job description can be processed into structured information:

```text
Job Description
      │
      ▼
Text Processing
      │
      ├── Required Skills
      ├── Preferred Skills
      ├── Experience
      ├── Education
      └── Keywords
      │
      ▼
Compare with User Profile
      │
      ▼
AI Analysis
```

Potential output:

```text
Matching Skills
Skill Gaps
Relevant Projects
Relevant Experience
Resume Suggestions
```

---

# 📧 Email Generation

The Agentic Service can generate application-related emails.

Inputs can include:

```text
User Profile
Resume
Job Description
Company
Recruiter
```

Example:

```text
Profile
   +
Job Description
   +
Relevant Experience
        ↓
       LLM
        ↓
Professional Email
```

The generated email should remain concise and relevant to the application context.

---

# 📨 SQS Worker

Worker:

```text
app/workers/ingestion_worker.py
```

Development:

```bash
uv run python -m app.workers.ingestion_worker
```

The worker:

1. Connects to SQS
2. Receives messages
3. Validates messages
4. Retrieves document
5. Parses document
6. Creates chunks
7. Generates embeddings
8. Writes vectors
9. Deletes/acknowledges the message
10. Retries failures when appropriate

---

# 🔄 Worker Flow

```text
                     SQS
                      │
                      ▼
                Receive Message
                      │
                      ▼
                Validate Event
                      │
                      ▼
                Download File
                      │
                      ▼
                    Parse
                      │
                      ▼
                   Chunk
                      │
                      ▼
                 Embedding
                      │
                      ▼
                S3 Vectors
                      │
                      ▼
                 Success
```

---

# 🧠 Redis Temporary Memory

Redis can be used for temporary AI conversation memory.

Example:

```text
User
 ↓
Chat Session
 ↓
Redis
 ↓
Temporary Context
```

A short TTL can be used to avoid keeping temporary conversational data indefinitely.

Example:

```text
TTL = 1 hour
```

The exact TTL should be configurable.

---

# 🧩 LLM Providers

CareerForge can be configured to support multiple providers.

## Amazon Bedrock

```env
LLM_PROVIDER=bedrock
```

---

## Google Gemini

```env
LLM_PROVIDER=google
```

---

## Hugging Face

```env
LLM_PROVIDER=huggingface
```

This allows provider changes without modifying application logic.

---

# 🔢 Embedding Provider Configuration

Example:

```env
EMBEDDING_PROVIDER=bedrock
EMBEDDING_MODEL_ID=amazon.titan-embed-text-v2:0
```

Alternative:

```env
EMBEDDING_PROVIDER=google
```

or:

```env
EMBEDDING_PROVIDER=huggingface
```

The application should determine the correct embedding implementation from configuration.

---

# 🌎 Environment Variables

Example:

```env
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:5432/DB

AWS_REGION=ap-south-1

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=

S3_BUCKET_NAME=
S3_VECTOR_BUCKET=
S3_VECTOR_INDEX=

SQS_QUEUE_URL=

REDIS_URL=

LLM_PROVIDER=google
EMBEDDING_PROVIDER=bedrock

GOOGLE_API_KEY=

HUGGINGFACE_API_KEY=
HUGGINGFACE_LLM_MODEL_ID=

BEDROCK_LLM_MODEL_ID=
BEDROCK_EMBEDDING_MODEL_ID=
```

Never commit `.env`.

---

# 📦 Installation

Install dependencies:

```bash
uv sync
```

---

# ▶️ Run API

```bash
uv run uvicorn app.main:app --reload --port 8001
```

Swagger:

```text
http://localhost:8001/docs
```

---

# ⚙️ Run Worker

```bash
uv run python -m app.workers.ingestion_worker
```

The intended architecture is to start the worker automatically alongside the Agentic Service in deployment.

---

# 🧪 Testing

Run all tests:

```bash
uv run pytest
```

---

## Ingestion Test

```bash
uv run python scripts/test_langchain_ingestion.py
```

---

## Embedding Test

```bash
uv run python scripts/test_langchain_embeddings.py
```

---

# 🧪 RAG Testing

A basic RAG test should verify:

```text
Document
 ↓
Parser
 ↓
Chunker
 ↓
Embedding
 ↓
Vector Store
 ↓
Retriever
 ↓
LLM
 ↓
Answer
```

Each layer should be testable independently.

---

# 📊 AI Evaluation

CareerForge can use DeepEval for evaluating the AI pipeline.

Potential evaluation datasets:

```text
Golden Questions
Expected Context
Expected Answer
```

Evaluation pipeline:

```text
Golden Dataset
      │
      ▼
Run Agent
      │
      ▼
Retrieve Context
      │
      ▼
Generate Answer
      │
      ▼
DeepEval
      │
      ▼
Metrics
```

---

# 📈 Monitoring

AI tracing can be implemented using LangSmith.

```text
User Request
      │
      ▼
Agent
      │
      ├── Retrieval
      ├── Tool Calls
      └── LLM
      │
      ▼
LangSmith
```

Infrastructure monitoring can use:

```text
CloudWatch
Prometheus
Grafana
```

---

# 🐳 Docker

Build:

```bash
docker build -t careerforge-agentic .
```

Run:

```bash
docker run \
  -p 8001:8001 \
  --env-file .env \
  careerforge-agentic
```

---

# ☸️ Kubernetes

A production deployment can separate the API and worker.

```text
EKS
│
├── Agentic API Deployment
│
└── Ingestion Worker Deployment
        │
        ▼
       SQS
```

This allows the worker to scale independently.

---

# 🔒 Security

The Agentic Service should:

* Validate authenticated requests
* Restrict internal access
* Use IAM least privilege
* Keep secrets outside source control
* Restrict S3 access
* Restrict S3 Vector access
* Protect SQS
* Avoid logging secrets
* Avoid logging complete sensitive documents
* Use encrypted storage
* Use HTTPS in production

---

# 🐛 Troubleshooting

## S3 Vector permission error

Check IAM permissions:

```text
s3vectors:GetIndex
s3vectors:PutVectors
s3vectors:QueryVectors
s3vectors:GetVectors
s3vectors:DeleteVectors
```

Also verify:

```text
AWS Region
Vector Bucket
Vector Index
IAM Role
```

---

## Embedding dimension mismatch

Check:

```text
Embedding Model
Configured Dimension
Actual Vector Dimension
S3 Vector Index Dimension
```

All must match.

---

## SQS messages not processing

Check:

```text
SQS_QUEUE_URL
AWS_REGION
IAM permissions
Worker process
Message visibility timeout
Dead-letter queue
```

---

## LLM 429

A `429` usually indicates rate limiting or quota limitations.

Check:

```text
Provider quota
API limits
Model availability
Request frequency
Billing/account status
```

---

## Model unavailable

If a provider reports that a model is unavailable, verify the current provider model identifier and whether the model is available to the configured account/tier.

Avoid hardcoding provider-specific model assumptions.

---

## LangGraph routing errors

If an agent router expects JSON, ensure the model produces valid JSON.

Expected:

```json
{
  "route": "retrieval"
}
```

Invalid output such as:

```text
{'route': 'retrieval'}
```

may fail strict JSON parsing.

Use structured output where supported.

---

# 🔄 Complete AI Data Flow

```text
                         USER
                          │
                          ▼
                    React Frontend
                          │
                          ▼
                    Core Backend
                          │
                          ▼
                   Agentic Service
                          │
                 ┌────────┴────────┐
                 │                 │
                 ▼                 ▼
              Query            User Context
                 │                 │
                 └────────┬────────┘
                          ▼
                    Query Embedding
                          │
                          ▼
                     S3 Vectors
                          │
                          ▼
                   Relevant Chunks
                          │
                          ▼
                   Context Builder
                          │
                          ▼
                    LangGraph Agent
                          │
                          ▼
                         LLM
                          │
                          ▼
                     AI Response
                          │
                          ▼
                    Core Backend
                          │
                          ▼
                    React Frontend
```

---

# 📄 Complete Resume Ingestion Flow

```text
                    Resume Upload
                          │
                          ▼
                    Core Backend
                          │
                          ▼
                         S3
                          │
                          ▼
                    Event / SQS
                          │
                          ▼
                 Ingestion Worker
                          │
                          ▼
                    PDF Parser
                          │
                          ▼
                     Text Data
                          │
                          ▼
                     Chunking
                          │
                          ▼
                    Embeddings
                          │
                          ▼
                     S3 Vectors
                          │
                          ▼
                  Retrieval Ready
```

---

# 🎯 Design Principles

The Agentic Service follows these principles:

### Separation of Concerns

```text
Parsing
Embedding
Retrieval
Generation
Storage
Queue
```

should remain separate modules.

### Provider Independence

LLM and embedding providers should be configurable.

### Async Processing

Expensive operations should run asynchronously.

### Observability

AI operations should be traceable.

### User Isolation

User-specific data must remain isolated.

### Failure Recovery

Queue-based tasks should support retries and failure handling.

---

# 📜 License

See the root CareerForge repository.

---

# 👨‍💻 CareerForge Agentic Service

AI infrastructure powering CareerForge.

Built with:

```text
FastAPI
LangChain
LangGraph
RAG
Amazon Bedrock
Google Gemini
Hugging Face
S3
S3 Vectors
SQS
Redis
DeepEval
LangSmith
```
