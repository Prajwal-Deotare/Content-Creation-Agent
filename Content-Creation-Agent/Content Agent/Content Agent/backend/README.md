# Content Agent Web Interface

This UI is designed to sit on top of the existing custom Python Content Agent.

## Files

- `app.py` - FastAPI API and session management
- `static/index.html` - polished web interface

## Expected existing backend files

The `backend` folder should also contain:

- `content_agent.py`
- `foundry_llm.py`
- `models.py`
- `prompts.py`

## Run

From the `backend` directory:

```powershell
python -m uvicorn app:app --reload --port 8000
```

Then open:

http://localhost:8000

## Workflow

1. Fill the six-question content brief.
2. Generate exactly three options.
3. Select A, B, or C.
4. Revise the selected version.
5. Approve it.
6. The state becomes READY_TO_SAVE.

The current implementation stores sessions in memory for local development.
A database should be added before production deployment.
