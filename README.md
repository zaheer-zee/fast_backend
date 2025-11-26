# Crux-AI Backend

This is the FastAPI backend for Crux-AI, featuring a multi-agent system for misinformation detection.

## Setup

1.  **Install Dependencies**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2.  **Environment Variables**:
    - Copy `.env.example` to `.env`.
    - Add your `GROQ_API_KEY` and `NEWSDATA_API_KEY`.

## Running the Server

You can use the helper script:
```bash
./run.sh
```

Or run manually:
```bash
source venv/bin/activate
uvicorn main:app --reload
```

## API Documentation

Once running, visit:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Key Endpoints

- `POST /api/verify`: Verify a claim text.
- `POST /api/scan`: Trigger a news scan.
- `GET /api/crisis`: Check for crisis alerts.
