# Career Agents Web UI

A beautiful web interface for the Career Agents toolkit with secure API key management.

## Features

- 🎨 Modern, dark-themed UI
- 🔒 Secure API key handling via backend (never exposed to client)
- 💬 Interactive chat interface for all 4 agents
- 🔄 Conversation persistence per agent
- 📱 Responsive design

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Key

**Local Development:**
```bash
export XAI_API_KEY="your-xai-api-key-here"
```

Or create a `.env` file:
```bash
XAI_API_KEY=your-xai-api-key-here
```

**Production (GitHub Secrets):**
- Go to repository Settings → Secrets and variables → Actions
- Add secret: `XAI_API_KEY`

### 3. Run the Server

```bash
python app.py
```

The server will start on http://localhost:5000

### 4. Open in Browser

Navigate to http://localhost:5000 and start chatting with the agents!

## Architecture

```
┌─────────────────┐
│   Browser       │
│  (HTML/JS UI)   │
└────────┬────────┘
         │ /api/chat
         │ (no API key)
         ▼
┌─────────────────┐
│  Flask Backend  │
│    (app.py)     │
│  XAI_API_KEY    │
└────────┬────────┘
         │ chat.completions
         │ (with API key)
         ▼
┌─────────────────┐
│   xAI Grok API  │
│  api.x.ai       │
└─────────────────┘
```

**Security Benefits:**
- ✅ API key stays on server, never sent to client
- ✅ All API calls proxied through backend
- ✅ Works with GitHub Secrets in deployment
- ✅ No risk of key exposure in browser console/network

## Deployment Options

### Option 1: Local/VPS Deployment

```bash
# Set environment variable
export XAI_API_KEY="your-key"

# Run with production server
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Install gunicorn:
```bash
pip install gunicorn
```

### Option 2: Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=5000
EXPOSE 5000

CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t career-agents-ui .
docker run -p 5000:5000 -e XAI_API_KEY="your-key" career-agents-ui
```

### Option 3: GitHub Actions + Cloud Run

See `.github/workflows/deploy-ui.yml` for automated deployment to Google Cloud Run.

## API Endpoints

### `GET /`
Serves the main UI

### `POST /api/chat`
Proxies chat requests to xAI

**Request:**
```json
{
  "model": "grok-beta",
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
  ],
  "max_tokens": 2000,
  "temperature": 0.7
}
```

**Response:**
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "..."
      }
    }
  ]
}
```

### `GET /api/health`
Health check endpoint

**Response:**
```json
{
  "status": "ok",
  "api_key_configured": true
}
```

## The 4 Agents

### 🔍 Gap Analyst
Analyzes skill gaps between your resume and job descriptions

### ✍️ Resume Tailor
ATS-optimizes your resume for specific job descriptions

### 🤝 Outreach Drafter
Generates personalized LinkedIn connection messages

### 🎙️ Interview Prep
Provides mock interviews, code review, and behavioral prep

## Troubleshooting

### API Key Not Configured
```
✗ API key not configured on server
```
**Solution:** Set the `XAI_API_KEY` environment variable before starting the server.

### Cannot Connect to Backend
```
✗ Cannot connect to backend server
```
**Solution:** Make sure the Flask server is running on port 5000.

### CORS Errors (in browser console)
**Solution:** The Flask backend has CORS enabled. If you're running on a different port, update the CORS configuration in `app.py`.

## Development

Run in debug mode:
```bash
export FLASK_ENV=development
python app.py
```

The server will auto-reload on file changes.

## Security Notes

- Never commit API keys to git
- Use `.env` files for local development (add to `.gitignore`)
- Use GitHub Secrets for CI/CD
- The backend validates all requests before proxying
- Consider adding rate limiting for production use

## License

Same as parent project
