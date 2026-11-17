import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Importing uvicorn...", flush=True)
    import uvicorn
    print("Importing app...", flush=True)
    from app.main import app
    print("Ready to start uvicorn.run...", flush=True)
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
except Exception as e:
    print("CRASHED:", e, flush=True)
    traceback.print_exc()
