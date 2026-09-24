# OrgLens - Codebase Intelligence

[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)](https://www.djangoproject.com/)
[![Llama](https://img.shields.io/badge/Meta_Llama-0467DF?style=for-the-badge&logo=meta&logoColor=white)](https://llama.meta.com/)


https://github.com/user-attachments/assets/7496afda-b3e3-4e1d-b03f-ddc43982b7a1

*OrgLens: Understanding your codebase and connecting with experts, powered by Llama.*

## 🌟 Why OrgLens?

### The Problem

Finding the right expert or understanding code history in large organizations is time-consuming and inefficient. Key knowledge often stays siloed or buried in commit logs.

## Our Solution: OrgLens

OrgLens connects to your GitHub organization, analyzes repositories, commits, and contributors, and uses **Llama** to generate insightful summaries. It helps you:

*   Instantly find contributors with specific expertise.
*   Understand individual contributions through AI-generated profiles.
*   Query your codebase's history and activity using natural language.
*   Interact with contributor "digital twins" (AI based on their work) for context before direct contact**.

## Core Features

✨ **AI-Powered Contributor Summaries & Profiles**.
🔍 **Natural Language Codebase Querying**.
🌐 **Repository & Contributor Exploration**.
🤖 **"Digital Twin" Interaction via Chat**.

---

## 🤖 Digital Twin Architecture

OrgLens introduces **Digital Twins**—autonomous AI personas synthesized for every software engineer in your organization based on their real commit history, pull requests, issue resolutions, and repository activity.

### ⚙️ Backend API & Prompt Pipeline Specification

The Digital Twin feature is powered by Django REST endpoints that dynamically build persona system prompts and stream responses using chunked transfer encoding (`StreamingHttpResponse`).

#### 1. Endpoint Details
* **Route**: `POST /api/twin_stream/`
* **Content-Type**: `application/json`
* **Request Payload**:
  ```json
  {
    "contributor_id": 1,
    "prompt": "What was your approach to optimizing the React rendering pipeline?"
  }
  ```
* **Response Header**: `Content-Type: text/plain; charset=utf-8` (chunked HTTP stream)

#### 2. Dynamic System Persona Construction
When a user initiates a chat session, the backend gathers relevant contextual telemetry:
1. **Contributor Profile & Overview**: Pulls overall contribution summaries from `DataSerializer`.
2. **Repository Mapping**: Links contributor activity with specific repositories and summaries.
3. **Commit & Issue History**: Ingests recent commit messages, solved GitHub issues, and PR context.
4. **Persona Framing**: Enforces first-person persona execution ("I built...", "In my recent commit...").

#### 3. Frontend Chat Component (`ContributorTwinChat.jsx`)
* **Floating Widget Integration**: Embedded inside [ContributorDetail.jsx](file:///Users/apple/Desktop/llama/frontend/src/pages/ContributorDetail.jsx) with fixed bottom-right positioning.
* **Readable Streams Handler**: Uses standard Fetch API `response.body.getReader()` with `TextDecoder` to stream markdown text tokens in real time.
* **Interactive Prompt Chips**: Quick action buttons allow users to send predefined queries instantly.
* **Responsive Dark/Light Layout**: Full Tailwind CSS adaptation matching global theme state.



## 🛠 Tech Stack

| Component | Technology |
|---|---|
| **Backend** | Python, Django, Llama API |
| **Frontend** | ReactJS, Vite, Tailwind CSS |
| **Data APIs** | GitHub API |
| **Real-time Voice/Chat** | PlayAI API powered by Groq |


## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

### Installation
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/rajneeshverma1/Hack-e-awadh
    cd Hack-e-awadh
    ```
2.  **Set up the Backend (Django Server):**
    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate  # Use `.\venv\Scripts\activate` on Windows
    pip install -r requirements.txt
    # Create a .env file in this 'backend' directory
    # Add your API keys and Django secret key:
    # LLAMA_API_KEY=your_llama_api_key
    # Add any other necessary backend env vars (like DB config if not SQLite)
    # Note: Copy .env.example if available or follow the required keys.
    python manage.py migrate # Run migrations if needed
    python manage.py runserver
    ```
    *The backend should now be running, typically on `http://127.0.0.1:8000/`.*

3.  **Set up the Frontend (Vite/React):**
    *(In a separate terminal)*
    ```bash
    cd frontend
    npm install
    npm run dev
    ```
    *The frontend development server should now be running, typically on `http://localhost:5173/` (check terminal output).*

4.  **Access the App:** Open your browser to the frontend URL (e.g., `http://localhost:5173`).

## 🌍 Deployment

- **Frontend**: Designed for Vercel/Netlify.
- **Backend**: Ready for Render/Railway.

## 🤝 Contributors

*   Rajneesh Verma - [GitHub](https://github.com/rajneeshverma1)

## Acknowledgements

*   Powered by **Meta Llama**.
## Support

For any questions or issues, please open a GitHub issue.

## License

This project is licensed under CC BY-NC 4.0. No commercial use allowed without explicit permission.

- **Theme Mode**: Full Light and Dark Mode toggle support.
