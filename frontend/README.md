# 🎨 CareerForge Frontend

The **CareerForge Frontend** is the user-facing web application for the CareerForge platform.

It provides the interface through which users manage their professional profiles, resumes, applications, career information, AI assistant conversations, and career-related workflows.

The frontend is built with **React + Vite + Tailwind CSS** and communicates primarily with the CareerForge Core Backend through REST APIs.

---

## 📌 Table of Contents

* [Overview](#-overview)
* [Features](#-features)
* [Technology Stack](#-technology-stack)
* [Architecture](#-architecture)
* [Project Structure](#-project-structure)
* [Application Flow](#-application-flow)
* [Authentication](#-authentication)
* [API Communication](#-api-communication)
* [Pages](#-pages)
* [Environment Variables](#-environment-variables)
* [Installation](#-installation)
* [Development](#-development)
* [Production Build](#-production-build)
* [Deployment](#-deployment)
* [Troubleshooting](#-troubleshooting)
* [Security](#-security)

---

# 🎯 Overview

The CareerForge frontend provides a centralized career-management interface.

Users can:

* Create and update their professional profile
* Manage skills
* Manage education
* Manage experience
* Manage projects
* Manage certifications
* Upload and manage resumes
* Track job applications
* View application events
* Connect Gmail
* Access professional email information
* Chat with the Career Assistant
* Analyze job descriptions
* Receive AI-powered career assistance

---

# ✨ Features

## 👤 Profile Management

Users can manage:

```text
Personal Information
Professional Summary
Skills
Education
Experience
Projects
Certifications
Contact Information
```

---

## 📄 Resume Management

The frontend provides interfaces for:

* Resume upload
* Resume listing
* Resume metadata
* Resume version management
* Resume selection for applications

The frontend does not perform heavy document processing.

Instead:

```text
Frontend
   ↓
Core Backend
   ↓
Storage / Processing
```

---

# 💼 Application Management

Users can manage their job applications.

Application information can include:

```text
Company
Job Title
Job Description
Application Status
Application Date
Resume
Recruiter
Email Activity
```

---

# 🤖 Career Assistant

The frontend provides the UI for the AI Career Assistant.

Example:

```text
User
 ↓
Career Assistant UI
 ↓
Core Backend
 ↓
Agentic Service
 ↓
AI / RAG
 ↓
Response
 ↓
Frontend
```

The frontend is responsible for:

* Chat interface
* User messages
* Assistant messages
* Loading states
* Error handling
* Conversation UI
* Relevant career information display

---

# 📧 Gmail Integration

The profile page provides Gmail connection functionality.

Typical flow:

```text
Profile
  ↓
Connect Gmail
  ↓
Core Backend
  ↓
Google OAuth
  ↓
Callback
  ↓
Connected
```

The frontend should not directly handle Google client secrets or Gmail API credentials.

---

# 🛠️ Technology Stack

| Technology     | Purpose                   |
| -------------- | ------------------------- |
| React          | UI framework              |
| Vite           | Development/build tooling |
| Tailwind CSS   | Styling                   |
| JavaScript     | Application logic         |
| Amazon Cognito | Authentication            |
| REST API       | Backend communication     |
| Fetch/Axios    | HTTP communication        |

---

# 🏗️ Architecture

```text
                 ┌──────────────────────┐
                 │        User          │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   React Frontend     │
                 │                      │
                 │ Dashboard            │
                 │ Profile              │
                 │ Resume               │
                 │ Applications         │
                 │ Career Assistant     │
                 └──────────┬───────────┘
                            │
                            │ REST API
                            ▼
                 ┌──────────────────────┐
                 │    Core Backend      │
                 │     FastAPI          │
                 │      :8000           │
                 └──────────┬───────────┘
                            │
               ┌────────────┴─────────────┐
               ▼                          ▼
          PostgreSQL                 Agentic Service
                                      :8001
```

The frontend should primarily communicate with **Core Backend**.

---

# 📁 Project Structure

A typical structure is:

```text
frontend/
│
├── public/
│
├── src/
│   ├── assets/
│   │
│   ├── components/
│   │
│   ├── pages/
│   │   ├── Dashboard.jsx
│   │   ├── Profile.jsx
│   │   ├── ProfileEdit.jsx
│   │   ├── CareerAssistant.jsx
│   │   ├── Applications.jsx
│   │   └── ...
│   │
│   ├── services/
│   │
│   ├── hooks/
│   │
│   ├── context/
│   │
│   ├── utils/
│   │
│   ├── App.jsx
│   └── main.jsx
│
├── .env
├── package.json
├── vite.config.js
└── README.md
```

---

# 🧭 Main Pages

## Dashboard

The dashboard provides an overview of the user's career activity.

Potential information:

```text
Profile Completion
Recent Applications
Resume Information
Professional Email
Career Assistant
Application Statistics
```

---

## Profile

Displays the user's professional information.

Sections include:

```text
Basic Information
Professional Summary
Skills
Education
Experience
Projects
Certifications
Gmail Connection
```

---

## Profile Edit

Used to update profile information.

The page communicates with:

```text
/api/v1/profile
/api/v1/skills
/api/v1/education
/api/v1/experience
/api/v1/projects
/api/v1/certifications
```

---

## Career Assistant

The AI assistant provides a conversational interface.

```text
CareerAssistant.jsx
```

Typical flow:

```text
User Message
     ↓
API Request
     ↓
Core Backend
     ↓
Agentic Service
     ↓
AI Agent
     ↓
Response
```

---

# 🔐 Authentication

CareerForge uses Amazon Cognito.

The frontend receives an authenticated session/token and sends the access token to the backend.

Example:

```http
Authorization: Bearer <ACCESS_TOKEN>
```

The frontend should never trust client-side authentication alone.

The backend validates the token independently.

---

# 🔌 API Communication

The frontend communicates with the backend using REST APIs.

Example:

```javascript
fetch(`${API_BASE_URL}/api/v1/profile`, {
  headers: {
    Authorization: `Bearer ${token}`,
  },
});
```

Recommended architecture:

```text
components/pages
       ↓
service/API layer
       ↓
Core Backend
```

Avoid duplicating API logic throughout UI components.

---

# 🌐 Environment Variables

Create:

```text
.env
```

Example:

```env
VITE_API_BASE_URL=http://localhost:8000

VITE_COGNITO_USER_POOL_ID=YOUR_USER_POOL_ID
VITE_COGNITO_CLIENT_ID=YOUR_CLIENT_ID
```

For production:

```env
VITE_API_BASE_URL=https://api.example.com
```

Do not place secrets such as:

```text
AWS_SECRET_ACCESS_KEY
GOOGLE_CLIENT_SECRET
DATABASE_PASSWORD
```

inside frontend environment variables.

Anything prefixed with `VITE_` can potentially be exposed to the browser.

---

# 📦 Installation

From the frontend directory:

```bash
npm install
```

---

# ▶️ Development

Start the development server:

```bash
npm run dev
```

Default:

```text
http://localhost:5173
```

---

# 🏗️ Production Build

Build:

```bash
npm run build
```

Preview:

```bash
npm run preview
```

The production output is generally generated in:

```text
dist/
```

---

# 🧪 Testing

Run the configured test suite:

```bash
npm test
```

If a test runner such as Vitest is configured:

```bash
npm run test
```

---

# 🔍 API Debugging

When an API request fails, check:

```text
Browser DevTools
     ↓
Network
     ↓
Request URL
Request Method
Status Code
Request Headers
Response
```

Common errors:

```text
401 → Authentication
403 → Authorization
404 → Incorrect endpoint
422 → Validation
500 → Backend error
```

---

# 🚀 Deployment

The frontend can be deployed using:

* S3 + CloudFront
* Nginx
* Docker
* Kubernetes
* Static hosting providers

Example:

```text
User
 ↓
Route 53
 ↓
CloudFront
 ↓
S3
 ↓
React Application
```

API traffic:

```text
React
 ↓
api.example.com
 ↓
ALB
 ↓
Core Backend
```

---

# 🔒 Frontend Security

Important rules:

* Never expose AWS secret keys
* Never expose database credentials
* Never expose Google client secrets
* Never trust client-side authorization
* Always validate authorization on the backend
* Use HTTPS in production
* Restrict CORS
* Validate uploaded files
* Avoid storing sensitive tokens unnecessarily

---

# 🐛 Troubleshooting

## API returns 401

Check:

```text
Cognito session
JWT
Authorization header
Token expiration
Backend JWKS configuration
```

---

## API returns 404

Check:

```text
VITE_API_BASE_URL
API version
Endpoint
Backend port
```

---

## CORS error

Check Core Backend CORS configuration.

Development:

```text
http://localhost:5173
```

Production:

```text
https://your-frontend-domain.com
```

---

## Blank page

Check:

```bash
npm run dev
```

and browser console.

Also verify:

```text
React errors
Import paths
Environment variables
API initialization
Routing
```

---

# 🔄 Development Flow

```text
Create UI
   ↓
Connect API
   ↓
Test API
   ↓
Add Loading State
   ↓
Add Error Handling
   ↓
Test Authentication
   ↓
Test Complete User Flow
```

---

# 📜 License

See the root CareerForge repository license.

---

# 👨‍💻 CareerForge

Frontend of the CareerForge AI-powered career platform.

Built with:

```text
React
Vite
Tailwind CSS
Amazon Cognito
REST APIs
```
