# OrgLens Deployment & User Guide

This guide will walk you through deploying your **React (Vite)** frontend to Vercel and your **Django** backend to Render or Railway. It also includes a guide on how to use the application once it's live!

---

## Part 1: How to Use the Application (User Guide)

Welcome to OrgLens! This application provides deep codebase intelligence across all your repositories. Here is how to navigate and use the platform:

### 1. The Dashboard (Home Page)
When you first open the application, you will land on the Dashboard. 
- **Organization Overview**: You'll see high-level statistics about your organization, including total repositories and active contributors.
- **Interactive Graph**: A beautiful, force-directed node graph visualizes the connections between your repositories and your contributors. You can hover over nodes to see how heavily involved a contributor is in a specific repository.

### 2. Repositories Page
Click on "Repositories" in the top navigation bar.
- Here you can see a list of all your active projects.
- Each repository card gives a summary of its purpose and recent activity.

### 3. Contributors Page
Click on "Contributors" in the top navigation bar to view your engineering team.
- You will see a list of all team members. 
- **View Details**: Click on a contributor's profile to view their detailed contribution history, including specific commits, issues resolved, and the repositories they specialize in.

### 4. Digital Twin Chat (AI Clone)
When you click into a specific Contributor's detail page, you will notice a floating chat bubble in the bottom right corner.
- **Chat with their Twin**: Click the chat bubble to open a conversation with the contributor's AI Digital Twin.
- **Ask Questions**: Ask the twin about their recent commits, why they made certain design decisions, or how a specific repository works. The AI twin has full context of that engineer's actual work history and will respond in character!

### 5. Global Llama Chat
On the main pages (like the Dashboard), you can access the global AI assistant.
- Use this chat to ask broad questions about the entire organization's codebase. The AI will analyze all repositories and point you to the exact contributor who is the best expert on your question.

---

## Part 2: Deploying the Backend (Django)

We recommend using **Render** or **Railway** for the backend, as they natively support Python/Django out of the box.

### 1. Preparation (Local)
Before you deploy, make sure you update a few things in your code to make it production-ready. 

**Update `backend/requirements.txt`:**
Ensure `gunicorn` (the production web server for Django) and `whitenoise` (for serving static files) are added:
```text
gunicorn==21.2.0
whitenoise==6.6.0
```

**Update `backend/config/settings.py`:**
You will need to allow your new frontend URL to communicate with your backend.
1. Change `DEBUG = True` to `DEBUG = False`.
2. Update `ALLOWED_HOSTS = ['*']` (or add your specific Render/Railway domain).
3. Update CORS settings so your frontend can reach the backend:
```python
CORS_ALLOW_ALL_ORIGINS = True # Or specifically add your Vercel URL
```

Commit these changes and push to GitHub.

### 2. Deploying to Render
1. Go to [Render.com](https://render.com/) and create a new **Web Service**.
2. Connect your GitHub repository (`rajneeshverma1/Hack-e-awadh`).
3. Set the **Root Directory** to: `backend`
4. Set the **Build Command** to: 
   ```bash
   pip install -r requirements.txt && python manage.py migrate
   ```
5. Set the **Start Command** to: 
   ```bash
   gunicorn config.wsgi:application
   ```
6. **Environment Variables**: Add your API keys here!
   - `OPENAI_API_KEY`: Your OpenAI API Key
   - `LLAMA_API_KEY`: Your Llama/Groq API Key
   - `GITHUB_TOKEN`: Your GitHub PAT
7. Click **Create Web Service**. Wait a few minutes for it to deploy, and copy the provided `.onrender.com` URL.

### 3. Digital Twin Streaming & Proxy Configuration
To ensure real-time chunked streaming for `/api/twin_stream/` in production:
- **Gunicorn Workers**: Use `--timeout 120` or `--worker-class gevent` if running long-lived streaming completions.
- **Nginx / Reverse Proxy**: Disable HTTP response buffering (`proxy_buffering off;` and `X-Accel-Buffering: no`) so streaming tokens reach the frontend without delay.
- **CORS Configuration**: Ensure `CORS_ALLOW_HEADERS` allows `Content-Type` and `Authorization` headers for POST streaming requests.


---

## Part 3: Deploying the Frontend (React/Vite)

We recommend using **Vercel** for the frontend, as it is incredibly fast and perfectly optimized for Vite.

### 1. Preparation (Local)
You need to point your frontend to your new production backend URL instead of `localhost:8000`.

**Update API URLs:**
Search your frontend code (like `ContributorTwinChat.jsx` and `LlamaChat.jsx`) and replace:
`http://localhost:8000/api/...`
with your new Render URL:
`https://your-backend-url.onrender.com/api/...`

*(Best practice: use a `.env` file in your frontend for this!)*

Commit these changes and push to GitHub.

### 2. Deploying to Vercel
1. Go to [Vercel.com](https://vercel.com/) and click **Add New Project**.
2. Import your GitHub repository (`rajneeshverma1/Hack-e-awadh`).
3. Configure the Project:
   - **Framework Preset**: Vercel should automatically detect **Vite**.
   - **Root Directory**: Click "Edit" and select `frontend`.
4. Click **Deploy**.

Vercel will build your React application and provide you with a live, production-ready URL!


### 5. Theme Switching (Light/Dark Mode)
- **Top Header Toggle**: Click the ☀️ / 🌙 theme toggle button located on the top header navbar.
- **Instant Persistence**: Your preference is saved locally and applies across all pages seamlessly.

### 6. Environment Checklist
- Ensure `OPENAI_API_KEY` and `GITHUB_TOKEN` are populated in production settings.

### 7. Release Notes (v1.1.1)
- Added full Light/Dark mode support across all components.
- Resilient AI stream generation.
