# 🚀 CareerForge

> **AI-powered career management, job matching, resume intelligence, and automated job-application assistance platform.**

CareerForge is a full-stack AI-powered career platform designed to help users manage their professional profiles, resumes, job opportunities, applications, emails, and career-related workflows from a single platform.

The system combines a modern React frontend, a FastAPI backend, an AI-powered agentic service, AWS infrastructure, asynchronous workers, vector search, and LLM-powered capabilities.

---

## 📌 Table of Contents

* [Overview](#-overview)
* [Key Features](#-key-features)
* [System Architecture](#-system-architecture)
* [Repository Structure](#-repository-structure)
* [Technology Stack](#-technology-stack)
* [Services](#-services)
* [Frontend](#-frontend)
* [Core Backend](#-core-backend)
* [Agentic Service](#-agentic-service)
* [Authentication](#-authentication)
* [Resume Processing](#-resume-processing)
* [AI & RAG Architecture](#-ai--rag-architecture)
* [Vector Store](#-vector-store)
* [Email & Gmail Integration](#-email--gmail-integration)
* [Background Workers](#-background-workers)
* [Database Architecture](#-database-architecture)
* [AWS Architecture](#-aws-architecture)
* [Environment Variables](#-environment-variables)
* [Local Development](#-local-development)
* [Running the Application](#-running-the-application)
* [API Structure](#-api-structure)
* [Data Flow](#-data-flow)
* [Resume Upload Flow](#-resume-upload-flow)
* [AI Assistant Flow](#-ai-assistant-flow)
* [Job Application Flow](#-job-application-flow)
* [Email Flow](#-email-flow)
* [Deployment](#-deployment)
* [Monitoring](#-monitoring)
* [Security](#-security)
* [Troubleshooting](#-troubleshooting)
* [Future Improvements](#-future-improvements)
* [Contributing](#-contributing)
* [License](#-license)

---

# 🎯 Overview

CareerForge is built around the idea of creating a centralized **AI career workspace**.

Instead of managing resumes, job descriptions, applications, professional information, recruiter communication, and career assistance across multiple disconnected tools, CareerForge brings these workflows together.

The platform allows a user to:

* Create and maintain a professional profile
* Manage education, skills, experience, projects, and certifications
* Upload and manage multiple resumes
* Analyze resumes against job descriptions
* Search and manage job opportunities
* Track applications
* Connect Gmail
* Draft professional emails using AI
* Automatically send application-related emails
* Chat with an AI career assistant
* Retrieve relevant information from uploaded documents
* Use semantic search over career-related information
* Generate context-aware responses using LLMs
* Process documents asynchronously
* Monitor application and system activity

---

# ✨ Key Features

## 👤 Professional Profile

Users can maintain their complete professional profile.

Supported information includes:

* Personal information
* Professional summary
* Skills
* Education
* Work experience
* Projects
* Certifications
* Contact information
* Professional email information

---

## 📄 Resume Management

CareerForge supports resume management through the platform.

Users can:

* Upload resumes
* Store multiple resume versions
* Maintain resume metadata
* Associate resumes with applications
* Process resumes for AI retrieval
* Use resume information in AI conversations
* Generate application-specific content

---

## 🤖 AI Career Assistant

CareerForge includes an AI-powered career assistant.

The assistant can work with:

* User profile
* Resume information
* Skills
* Experience
* Projects
* Certifications
* Job descriptions
* Application context

Example questions:

```text
How well does my profile match this job?

What skills am I missing for this position?

Write an email to the recruiter for this job.

Which projects from my profile are most relevant?

How should I improve my resume for this role?
```

---

## 🔎 RAG-Based Document Intelligence

CareerForge uses Retrieval-Augmented Generation (RAG) to provide context-aware AI responses.

The general pipeline is:

```text
Document
   ↓
Document Parser
   ↓
Text Extraction
   ↓
Chunking
   ↓
Embedding Generation
   ↓
Vector Store
   ↓
Semantic Retrieval
   ↓
Relevant Context
   ↓
LLM
   ↓
Final Response
```

This allows the AI system to retrieve relevant information instead of relying only on the model's general knowledge.

---

## 📧 Gmail Integration

CareerForge supports Gmail integration through OAuth.

Users can connect their Gmail account and use the platform for career-related email workflows.

Possible operations include:

* Connect Gmail
* Validate OAuth state
* Retrieve connected account information
* Draft emails
* Send application-related emails
* Attach resumes
* Track email metadata

CareerForge does not need to permanently store complete email bodies for the application workflow.

---

## 💼 Job Application Management

Users can manage job applications from a central dashboard.

Application information can include:

* Company
* Job title
* Job description
* Application status
* Application date
* Resume used
* Recruiter information
* Email activity
* Application events

Example application statuses:

```text
Saved
Applied
Under Review
Interview
Offer
Rejected
Withdrawn
```

---

# 🏗️ System Architecture

CareerForge follows a service-oriented architecture.

```text
                         ┌───────────────────────┐
                         │       User            │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │    React Frontend     │
                         │       Port 5173       │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │     Core Backend      │
                         │       FastAPI         │
                         │       Port 8000       │
                         └───────┬───────┬───────┘
                                 │       │
                  ┌──────────────┘       └──────────────┐
                  ▼                                     ▼
          ┌───────────────┐                     ┌───────────────┐
          │ PostgreSQL    │                     │     Redis     │
          │     RDS       │                     │   / Cache     │
          └───────────────┘                     └───────────────┘
                  │
                  │
                  ▼
          ┌──────────────────┐
          │ Agentic Service  │
          │     FastAPI      │
          │    Port 8001     │
          └───────┬──────────┘
                  │
        ┌─────────┼───────────────┐
        │         │               │
        ▼         ▼               ▼
     S3        S3 Vectors       LLM
   Storage     Vector Store    Provider
        │
        ▼
  Document Processing
        │
        ▼
   Embeddings
```

---

# 📁 Repository Structure

The repository contains three primary application components.

```text
CareerForge/
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── vite.config.js
│   └── ...
│
├── core-backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── workers/
│   │   └── main.py
│   │
│   ├── alembic/
│   ├── pyproject.toml
│   ├── uv.lock
│   └── ...
│
├── agentic-service/
│   ├── app/
│   │   ├── clients/
│   │   ├── core/
│   │   ├── ingestion/
│   │   ├── parsers/
│   │   ├── queue/
│   │   ├── repositories/
│   │   ├── retrieval/
│   │   ├── storage/
│   │   ├── vector_store/
│   │   ├── workers/
│   │   └── main.py
│   │
│   ├── scripts/
│   ├── tests/
│   ├── pyproject.toml
│   └── uv.lock
│
├── .gitignore
├── README.md
└── ...
```

---

# 🛠️ Technology Stack

## Frontend

* React
* Vite
* Tailwind CSS
* JavaScript
* Cognito integration
* REST APIs

---

## Backend

* Python
* FastAPI
* Uvicorn
* SQLAlchemy
* Alembic
* PostgreSQL
* asyncpg
* Pydantic

---

## AI / Agentic Layer

* LangChain
* LangGraph
* RAG
* Embeddings
* LLM providers
* Amazon Bedrock
* Google Gemini
* Hugging Face
* DeepEval
* LangSmith

---

## AWS

CareerForge uses multiple AWS services.

Potential infrastructure includes:

* Amazon EC2
* Amazon EKS
* Amazon RDS
* Amazon S3
* Amazon S3 Vectors
* Amazon Cognito
* Amazon SES
* Amazon ElastiCache
* Amazon SQS
* Application Load Balancer
* Route 53
* CloudWatch
* IAM
* VPC
* NAT Gateway
* Internet Gateway

---

# 🖥️ Services

CareerForge consists primarily of three application layers.

| Service         | Technology   | Port | Responsibility           |
| --------------- | ------------ | ---: | ------------------------ |
| Frontend        | React + Vite | 5173 | User interface           |
| Core Backend    | FastAPI      | 8000 | Main application APIs    |
| Agentic Service | FastAPI      | 8001 | AI, ingestion, retrieval |

---

# 🎨 Frontend

The frontend is responsible for all user-facing functionality.

Major pages include:

```text
Dashboard
Profile
Profile Edit
Resume Management
Applications
Career Assistant
Job Description
Settings
```

The frontend communicates primarily with the **Core Backend**.

```text
React
   ↓
Core Backend
   ↓
Database / Agentic Service
```

The frontend should not directly depend on internal Agentic Service APIs unless explicitly required by the architecture.

---

# ⚙️ Core Backend

The Core Backend is the primary application backend.

It handles:

* Authentication validation
* User management
* Profile management
* Resume metadata
* Education
* Experience
* Projects
* Skills
* Certifications
* Applications
* Notifications
* Gmail OAuth
* API orchestration
* Audit logs
* Application events

Technology:

```text
FastAPI
SQLAlchemy
PostgreSQL
Alembic
Pydantic
asyncpg
```

Default development port:

```text
8000
```

Start it with:

```bash
cd core-backend
uv run uvicorn app.main:app --reload --port 8000
```

---

# 🤖 Agentic Service

The Agentic Service contains AI-related functionality.

Responsibilities include:

* Document ingestion
* Document parsing
* Chunking
* Embedding generation
* Vector storage
* Semantic retrieval
* AI conversations
* Agent execution
* Job description analysis
* Profile-aware responses
* Email drafting
* AI evaluation

Default port:

```text
8001
```

Run:

```bash
cd agentic-service
uv run uvicorn app.main:app --reload --port 8001
```

---

# 🔐 Authentication

CareerForge uses Amazon Cognito for user authentication.

The general flow is:

```text
User
 ↓
Frontend
 ↓
Amazon Cognito
 ↓
JWT
 ↓
Core Backend
 ↓
JWT validation
 ↓
User identity
```

The backend associates the authenticated Cognito identity with a database user.

A typical user relationship is:

```text
Cognito User
      │
      │ cognito_sub
      ▼
PostgreSQL users table
```

The backend can bootstrap a database user record when a valid Cognito user exists but the corresponding application database row has not yet been created.

---

# 📄 Resume Processing

Resume processing is asynchronous.

A simplified flow:

```text
User Uploads Resume
        │
        ▼
Frontend
        │
        ▼
Core Backend
        │
        ├── Store Resume Metadata
        │
        └── Store File
                │
                ▼
               S3
                │
                ▼
         Event / Queue
                │
                ▼
        Agentic Worker
                │
                ▼
         Parse Document
                │
                ▼
          Extract Text
                │
                ▼
             Chunk
                │
                ▼
           Embeddings
                │
                ▼
          S3 Vectors
```

This separates the user-facing API request from potentially expensive document processing.

---

# 🧠 AI & RAG Architecture

CareerForge's RAG architecture is designed around user-specific career information.

## Step 1 — Document ingestion

A document is retrieved from storage.

```text
S3
 ↓
Document Loader
```

---

## Step 2 — Parsing

The document is converted into text.

Example:

```text
PDF
 ↓
PyPDFLoader
 ↓
Plain Text
```

---

## Step 3 — Chunking

Large documents are divided into smaller chunks.

Example strategy:

```text
RecursiveCharacterTextSplitter
```

---

## Step 4 — Embeddings

Each chunk is converted into a vector.

Possible embedding providers include:

```text
Amazon Titan
Google Gemini
Hugging Face
```

---

## Step 5 — Vector Storage

Vectors are stored in:

```text
Amazon S3 Vectors
```

The vector store allows semantic retrieval.

---

## Step 6 — Retrieval

When the user asks a question:

```text
User Query
    ↓
Query Embedding
    ↓
Vector Search
    ↓
Relevant Chunks
```

---

## Step 7 — Generation

Retrieved context is passed to the LLM.

```text
User Query
      +
Retrieved Context
      ↓
     LLM
      ↓
AI Response
```

---

# 🗄️ Vector Store

CareerForge uses an S3-based vector architecture.

The vector layer is responsible for operations such as:

```text
Get Index
Put Vectors
Query Vectors
Get Vectors
Delete Vectors
```

The implementation is located in the Agentic Service.

```text
agentic-service/
└── app/
    └── vector_store/
        └── s3_vectors.py
```

The vector dimensions must remain consistent between:

```text
Embedding Model
        ↓
Vector Configuration
        ↓
S3 Vector Index
```

For example, if an embedding provider produces:

```text
1024 dimensions
```

the vector index must be configured accordingly.

Changing embedding providers may require recreating or migrating the vector index if the dimensionality differs.

---

# 📧 Gmail Integration

Gmail integration uses Google's OAuth authorization flow.

General flow:

```text
User
 ↓
Connect Gmail
 ↓
Google OAuth
 ↓
Authorization
 ↓
Callback
 ↓
Token Exchange
 ↓
Validate Identity
 ↓
Store Email Connection
```

The system maintains an email connection associated with the user.

Example status:

```text
connected
not_connected
```

The Gmail connection is used for career-related email workflows.

---

# ✉️ AI Email Drafting

The AI email system can generate concise professional emails based on:

* User profile
* Resume
* Job description
* Target company
* Recruiter information

A generated email may contain:

```text
Subject
Body

Candidate Name
Email
Mobile
```

The user's resume can be attached when sending the email.

The objective is to generate short, relevant and context-aware professional communication rather than generic long-form text.

---

# ⚙️ Background Workers

CareerForge uses background workers so that expensive or asynchronous tasks do not block API requests.

There are two important worker types.

---

## Core Backend — Outbox Worker

The Core Backend uses an outbox-based workflow.

```text
API Request
    ↓
Database Transaction
    ↓
Outbox Event
    ↓
Outbox Worker
    ↓
Event Processing
```

The worker is responsible for processing pending events.

Development command:

```bash
cd core-backend
uv run python -m app.workers.outbox_worker
```

The intended architecture is to start this worker automatically with the Core Backend application.

---

## Agentic Service — Ingestion / SQS Worker

The Agentic Service processes asynchronous ingestion tasks.

```text
S3 / Application Event
       ↓
      SQS
       ↓
Ingestion Worker
       ↓
Document Processing
       ↓
Embeddings
       ↓
S3 Vectors
```

Development command:

```bash
cd agentic-service
uv run python -m app.workers.ingestion_worker
```

The intended deployment architecture starts the worker automatically with the Agentic Service.

---

# 🗃️ Database Architecture

CareerForge uses PostgreSQL.

The Core Backend contains application-oriented tables such as:

```text
users
profiles
skills
education
experience
projects
certifications
resumes
resume_versions
applications
application_events
notifications
audit_logs
email_connections
```

The Agentic Service can maintain its own AI/agent-related data within the database architecture.

Where schemas are separated, the architecture can use:

```text
public schema
agentic schema
```

This helps reduce coupling between services.

---

# 🧩 Database Relationships

A simplified relationship looks like:

```text
User
 │
 ├── Profile
 │
 ├── Skills
 │
 ├── Education
 │
 ├── Experience
 │
 ├── Projects
 │
 ├── Certifications
 │
 ├── Resumes
 │     └── Resume Versions
 │
 ├── Applications
 │     └── Application Events
 │
 ├── Email Connections
 │
 └── Notifications
```

---

# ☁️ AWS Architecture

A production deployment can be structured as follows:

```text
                         Route 53
                            │
                            ▼
                    Application Load
                        Balancer
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
        Frontend / Web              API Services
                                      │
                         ┌────────────┴────────────┐
                         │                         │
                         ▼                         ▼
                   Core Backend             Agentic Service
                         │                         │
              ┌──────────┼──────────┐              │
              │          │          │              │
              ▼          ▼          ▼              ▼
             RDS        S3       Redis/SQS        S3
              │                                      │
              │                                      ▼
              │                                 S3 Vectors
              │
              ▼
        Application Data
```

---

# 🌐 Networking

A production VPC can contain:

```text
VPC
│
├── Public Subnets
│   ├── Load Balancer
│   └── NAT / Internet-facing resources
│
└── Private Subnets
    ├── Application workloads
    ├── RDS
    ├── ElastiCache
    └── Internal services
```

Sensitive services such as databases should not be directly exposed to the public internet.

---

# 🔑 Environment Variables

Each service should maintain its own environment configuration.

Never commit secrets to Git.

Example Core Backend environment:

```env
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:5432/DB_NAME

AWS_REGION=ap-south-1

AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY
AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY

COGNITO_USER_POOL_ID=YOUR_USER_POOL_ID
COGNITO_CLIENT_ID=YOUR_CLIENT_ID

GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET=YOUR_GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI=YOUR_REDIRECT_URI

REDIS_URL=redis://localhost:6379
```

Example Agentic Service configuration:

```env
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:5432/DB_NAME

AWS_REGION=ap-south-1

S3_BUCKET_NAME=YOUR_BUCKET

S3_VECTOR_BUCKET=YOUR_VECTOR_BUCKET
S3_VECTOR_INDEX=YOUR_INDEX

AWS_ACCESS_KEY_ID=YOUR_ACCESS_KEY
AWS_SECRET_ACCESS_KEY=YOUR_SECRET_KEY

REDIS_URL=redis://localhost:6379

SQS_QUEUE_URL=YOUR_QUEUE_URL

EMBEDDING_PROVIDER=bedrock
EMBEDDING_MODEL_ID=amazon.titan-embed-text-v2:0

LLM_PROVIDER=google
GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY

HUGGINGFACE_API_KEY=YOUR_HUGGINGFACE_API_KEY
HUGGINGFACE_LLM_MODEL_ID=YOUR_MODEL_ID
```

Frontend example:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_COGNITO_USER_POOL_ID=YOUR_USER_POOL_ID
VITE_COGNITO_CLIENT_ID=YOUR_CLIENT_ID
```

---

# 🚫 Secrets

Never commit:

```text
.env
.env.local
.env.production
AWS credentials
Google OAuth secrets
API keys
JWT secrets
Database passwords
Private certificates
```

A `.gitignore` should include:

```gitignore
.env
.env.*
!.env.example

__pycache__/
*.pyc

node_modules/
dist/
build/

.venv/
venv/

.idea/
.vscode/

*.log

.DS_Store
```

---

# 💻 Local Development

## Requirements

Install:

* Git
* Python 3.11+
* Node.js
* npm
* uv
* PostgreSQL
* Redis

Optional:

* Docker
* Docker Compose
* AWS CLI

---

# 📥 Clone Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd CareerForge
```

---

# 🐍 Backend Installation

## Core Backend

```bash
cd core-backend
```

Create virtual environment using `uv`:

```bash
uv sync
```

Run migrations:

```bash
uv run alembic upgrade head
```

Start API:

```bash
uv run uvicorn app.main:app --reload --port 8000
```

API:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

---

# 🤖 Agentic Service Installation

```bash
cd agentic-service
uv sync
```

Run migrations if applicable:

```bash
uv run alembic upgrade head
```

Start service:

```bash
uv run uvicorn app.main:app --reload --port 8001
```

API:

```text
http://localhost:8001
```

Swagger:

```text
http://localhost:8001/docs
```

---

# 🎨 Frontend Installation

```bash
cd frontend
npm install
```

Start development server:

```bash
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

---

# ▶️ Running the Complete Application

During development, the system consists of:

### Terminal 1 — Frontend

```bash
cd frontend
npm run dev
```

### Terminal 2 — Core Backend

```bash
cd core-backend
uv run uvicorn app.main:app --reload --port 8000
```

### Terminal 3 — Agentic Service

```bash
cd agentic-service
uv run uvicorn app.main:app --reload --port 8001
```

The worker architecture is intended to allow the background workers to start automatically alongside their respective FastAPI services.

---

# 🔌 API Structure

The Core Backend API follows a versioned structure.

Example:

```text
/api/v1/
```

Examples:

```text
/api/v1/profile
/api/v1/resumes
/api/v1/applications
/api/v1/projects
/api/v1/skills
/api/v1/certifications
/api/v1/education
/api/v1/experience
/api/v1/email
```

---

# 📊 Example API Flow

## Get Profile

```http
GET /api/v1/profile
```

Authentication:

```text
Authorization: Bearer <JWT>
```

---

## Resume Upload

```http
POST /api/v1/resumes
```

Typical flow:

```text
Frontend
   ↓
POST /api/v1/resumes
   ↓
Core Backend
   ↓
Validate JWT
   ↓
Store Resume Metadata
   ↓
Store File
   ↓
Create Event
   ↓
Worker
   ↓
Agentic Service
```

---

# 🔄 Resume Upload Flow

Detailed architecture:

```text
                    User
                     │
                     ▼
               React Frontend
                     │
                     ▼
             Resume Upload API
                     │
                     ▼
              Core Backend
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
     PostgreSQL                 S3
   Resume Metadata           Resume File
          │                     │
          └──────────┬──────────┘
                     ▼
                Outbox Event
                     │
                     ▼
               Worker / Queue
                     │
                     ▼
              Agentic Service
                     │
                     ▼
                PDF Parser
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

---

# 💬 AI Assistant Flow

The AI assistant can use user-specific context.

```text
User Question
      │
      ▼
Career Assistant UI
      │
      ▼
Core Backend
      │
      ▼
Agentic Service
      │
      ▼
Query Understanding
      │
      ▼
Retrieve User Context
      │
      ▼
Vector Search
      │
      ▼
Relevant Documents
      │
      ▼
Prompt Construction
      │
      ▼
LLM
      │
      ▼
Response
      │
      ▼
Frontend
```

---

# 💼 Job Description Analysis

A job description can be processed as:

```text
Job Description
       │
       ▼
Text Extraction
       │
       ▼
Job Requirements
       │
       ├── Skills
       ├── Experience
       ├── Education
       └── Keywords
       │
       ▼
User Profile / Resume
       │
       ▼
Semantic Matching
       │
       ▼
LLM Analysis
       │
       ▼
Career Insights
```

Possible output:

```text
Matched Skills
Missing Skills
Relevant Projects
Relevant Experience
Resume Suggestions
Application Email
```

---

# 📧 Email Flow

```text
User
 ↓
Connect Gmail
 ↓
Google OAuth
 ↓
EmailConnection
 ↓
Career Assistant
 ↓
Generate Email
 ↓
User Review
 ↓
Send
 ↓
Gmail API
 ↓
Store Email Metadata
```

The system can keep email metadata such as:

```text
recipient
subject
timestamp
status
application_id
```

without requiring permanent storage of the complete email body.

---

# 🧪 Testing

Backend tests:

```bash
cd core-backend
uv run pytest
```

Agentic service:

```bash
cd agentic-service
uv run pytest
```

Specific ingestion tests can be executed using scripts such as:

```bash
uv run python scripts/test_langchain_ingestion.py
```

Embedding tests:

```bash
uv run python scripts/test_langchain_embeddings.py
```

---

# 📈 Evaluation

CareerForge can use evaluation datasets to measure AI quality.

The evaluation architecture can contain:

```text
Golden Dataset
      │
      ▼
Evaluation Runner
      │
      ├── Retriever Evaluation
      ├── Generator Evaluation
      └── End-to-End Evaluation
      │
      ▼
DeepEval
      │
      ▼
Evaluation Results
```

Useful metrics can include:

* Retrieval relevance
* Context relevance
* Answer relevance
* Faithfulness
* Hallucination rate
* Response quality

---

# 📊 Monitoring

The platform can be monitored using:

```text
Prometheus
Grafana
CloudWatch
LangSmith
```

Infrastructure monitoring:

```text
Application
   ↓
Metrics
   ↓
Prometheus
   ↓
Grafana
```

AWS infrastructure:

```text
AWS Services
   ↓
CloudWatch
   ↓
Logs / Metrics / Alarms
```

AI tracing:

```text
Agent
 ↓
LangChain / LangGraph
 ↓
LangSmith
```

---

# 🔒 Security

CareerForge should follow security best practices.

## Authentication

Use:

```text
Amazon Cognito
JWT
HTTPS
```

---

## Authorization

Every protected API should validate:

```text
User Identity
        +
Resource Ownership
```

A user should only access their own:

* Profile
* Resume
* Applications
* Documents
* Email connection
* AI session data

---

## AWS IAM

Use least-privilege IAM policies.

For S3 Vectors, permissions may include only the required operations:

```text
s3vectors:GetIndex
s3vectors:PutVectors
s3vectors:QueryVectors
s3vectors:GetVectors
s3vectors:DeleteVectors
```

Avoid using broad permissions such as:

```text
Action: "*"
Resource: "*"
```

in production.

---

# 🧠 Temporary AI Memory

CareerForge can maintain temporary conversation context for AI interactions.

A Redis-based approach can be used:

```text
User
 ↓
AI Conversation
 ↓
Redis
 ↓
Temporary Session Memory
```

The intended lifetime can be limited, for example:

```text
1 hour
```

This allows the agent to maintain conversational context without permanently storing every temporary interaction.

---

# 🔁 Event-Driven Architecture

CareerForge uses an event-driven approach for asynchronous tasks.

Example:

```text
Resume Uploaded
      │
      ▼
Database Transaction
      │
      ▼
Outbox Event
      │
      ▼
Worker
      │
      ▼
Queue
      │
      ▼
Agentic Service
      │
      ▼
Embedding Pipeline
```

This architecture reduces coupling between the synchronous API layer and expensive background processing.

---

# 🐳 Docker

Each backend service can be containerized.

Example:

```bash
docker build -t careerforge-core-backend ./core-backend
```

Run:

```bash
docker run -p 8000:8000 careerforge-core-backend
```

Agentic service:

```bash
docker build -t careerforge-agentic ./agentic-service
```

Run:

```bash
docker run -p 8001:8001 careerforge-agentic
```

Frontend:

```bash
docker build -t careerforge-frontend ./frontend
```

---

# ☸️ Kubernetes

CareerForge can be deployed to Kubernetes/EKS.

A simplified deployment:

```text
                     AWS EKS
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
   Frontend Pod   Core Backend    Agentic Service
                       │              │
                       │              │
                       └──────┬───────┘
                              │
              ┌───────────────┼──────────────┐
              ▼               ▼              ▼
             RDS          ElastiCache       S3
                                             │
                                             ▼
                                        S3 Vectors
```

Workers can run as:

```text
Deployment
```

or, depending on workload:

```text
Dedicated Worker Deployment
```

---

# ⚖️ Service Responsibilities

A clear separation of responsibility should be maintained.

## Frontend

Responsible for:

```text
UI
User Interaction
API Requests
Authentication State
Rendering
```

---

## Core Backend

Responsible for:

```text
Business Logic
User Data
Applications
Profiles
Resume Metadata
Authentication
Authorization
OAuth
API Orchestration
```

---

## Agentic Service

Responsible for:

```text
AI
RAG
Embeddings
Document Processing
Vector Search
Agents
LLM Calls
AI Evaluation
```

---

# 🔗 Service Communication

Recommended flow:

```text
Frontend
   │
   ▼
Core Backend
   │
   ├── PostgreSQL
   ├── S3
   ├── Redis
   └── Agentic Service
             │
             ├── LLM
             ├── Embeddings
             ├── S3 Vectors
             └── SQS
```

The frontend should primarily communicate with Core Backend.

This prevents exposing internal AI services directly to the browser.

---

# 🐛 Troubleshooting

## `401 Unauthorized`

Check:

```text
JWT
Cognito configuration
JWKS URL
User Pool ID
Client ID
Authorization header
```

Example:

```http
Authorization: Bearer <TOKEN>
```

---

## `405 Method Not Allowed`

Check:

```text
HTTP method
FastAPI route
CORS configuration
Frontend API call
```

---

## Database connection error

Check:

```text
DATABASE_URL
Security Group
VPC
Subnet
RDS endpoint
Port 5432
Credentials
```

---

## S3 access error

Check IAM permissions:

```text
s3:GetObject
s3:PutObject
s3:DeleteObject
```

and bucket policy.

---

## S3 Vector error

Verify:

```text
Vector bucket
Vector index
Region
IAM permissions
Embedding dimensions
```

Most importantly:

```text
Embedding dimensions == Vector index dimensions
```

---

## Embedding dimension mismatch

For example:

```text
Configured:
1024

Actual:
3072
```

This means the configured embedding model and vector index are inconsistent.

The embedding model and vector index must use the same dimension.

---

## Google OAuth error

Check:

```text
GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI
```

Also verify the redirect URI in Google Cloud matches the backend configuration exactly.

OAuth scopes must also be configured consistently.

---

## SQS worker not processing jobs

Check:

```text
SQS_QUEUE_URL
AWS_REGION
IAM permissions
Worker process
Message visibility timeout
Dead-letter queue
```

Then inspect worker logs.

---

# 🧭 Development Workflow

Recommended workflow:

```text
1. Create feature branch
        ↓
2. Implement feature
        ↓
3. Run backend tests
        ↓
4. Run frontend tests/build
        ↓
5. Test APIs
        ↓
6. Test worker
        ↓
7. Test AI flow
        ↓
8. Check logs
        ↓
9. Commit
        ↓
10. Push
        ↓
11. Create Pull Request
```

Example:

```bash
git checkout -b feature/resume-processing

git status

git add .

git commit -m "Add asynchronous resume processing"

git push origin feature/resume-processing
```

---

# 🌿 Git Branching

Suggested branches:

```text
main
develop
feature/*
bugfix/*
hotfix/*
```

Example:

```bash
git checkout -b feature/gmail-integration
```

---

# 🚀 Production Deployment

A production architecture can look like:

```text
                         Internet
                            │
                            ▼
                         Route 53
                            │
                            ▼
                           ALB
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
          Frontend                    API Layer
                                      │
                         ┌────────────┴────────────┐
                         │                         │
                         ▼                         ▼
                   Core Backend             Agentic Service
                         │                         │
                         │                 ┌───────┴───────┐
                         │                 │               │
                         ▼                 ▼               ▼
                        RDS              SQS          S3 Vectors
                         │
                         ▼
                    ElastiCache

                         +
                         │
                         ▼
                         S3
```

---

# 📦 Recommended Production Components

| Component          | AWS Service               |
| ------------------ | ------------------------- |
| DNS                | Route 53                  |
| Load Balancing     | Application Load Balancer |
| Compute            | EKS / EC2                 |
| Database           | RDS PostgreSQL            |
| Object Storage     | S3                        |
| Vector Storage     | S3 Vectors                |
| Cache              | ElastiCache               |
| Queue              | SQS                       |
| Authentication     | Cognito                   |
| Monitoring         | CloudWatch                |
| Metrics            | Prometheus                |
| Dashboards         | Grafana                   |
| AI Tracing         | LangSmith                 |
| SSL                | ACM                       |
| Container Registry | ECR                       |

---

# 🔐 Production Checklist

Before production deployment:

* [ ] HTTPS enabled
* [ ] Secrets stored securely
* [ ] IAM least privilege configured
* [ ] RDS private
* [ ] Redis private
* [ ] Internal services not publicly exposed
* [ ] Security groups reviewed
* [ ] S3 bucket policies reviewed
* [ ] Cognito configured
* [ ] Google OAuth production redirect URI configured
* [ ] SQS configured
* [ ] Dead-letter queue configured
* [ ] Worker health monitored
* [ ] Database backups enabled
* [ ] CloudWatch logging enabled
* [ ] Application monitoring configured
* [ ] Rate limiting configured
* [ ] CORS restricted
* [ ] Production environment variables configured

---

# 🗺️ Future Improvements

Potential future improvements include:

### AI

* Better job matching
* Resume optimization
* Multi-agent workflows
* Recruiter communication agent
* Interview preparation agent
* Automated skill-gap analysis
* Personalized career roadmap

### RAG

* Improved retrieval strategies
* Hybrid search
* Reranking
* Better document metadata
* Multi-document retrieval
* Evaluation-driven retrieval optimization

### Platform

* Job board integrations
* LinkedIn workflow integrations where permitted
* Application automation
* Interview tracking
* Calendar integration
* Recruiter CRM
* Career analytics

### Infrastructure

* Full Kubernetes deployment
* Horizontal autoscaling
* Event-driven worker scaling
* CI/CD
* Infrastructure as Code
* Terraform
* Centralized observability

---

# 📊 High-Level Data Flow

The complete CareerForge ecosystem can be summarized as:

```text
                           USER
                            │
                            ▼
                     React Frontend
                            │
                            ▼
                     Core Backend
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
            RDS             S3          Cognito
             │              │
             │              ▼
             │          Event / Queue
             │              │
             │              ▼
             │       Agentic Service
             │              │
             │       ┌──────┼───────┐
             │       │      │       │
             │       ▼      ▼       ▼
             │     Parser Embedding LLM
             │              │
             │              ▼
             │         S3 Vectors
             │              │
             └──────────────┴──────────────┐
                                            │
                                            ▼
                                     AI Response
                                            │
                                            ▼
                                       Frontend
```

---

# 🎯 Project Goals

CareerForge aims to provide a unified platform for:

```text
              ┌─────────────────────────┐
              │       CareerForge       │
              └────────────┬────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
     Profile             Resume             Jobs
        │                  │                  │
        ▼                  ▼                  ▼
    Experience          AI/RAG           Applications
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                           ▼
                    Career Assistant
                           │
                 ┌─────────┴─────────┐
                 │                   │
                 ▼                   ▼
             Email AI           Career Insights
```

---

# 📜 License

Add your chosen license here.

For example:

```text
MIT License
```

If this project is not open source, replace this section with:

```text
Copyright © 2026 CareerForge.

All rights reserved.
```

---

# 👨‍💻 Author

**Sahil Suman**

B.Tech — Electrical Engineering
NIT Agartala

CareerForge is developed as a full-stack AI/Cloud project combining:

```text
React
FastAPI
PostgreSQL
AWS
Docker
Kubernetes
LangChain
LangGraph
RAG
LLMs
Vector Search
Event-Driven Architecture
```

---

# ⭐ CareerForge

> **Build your profile. Understand your opportunities. Apply smarter.**

---
