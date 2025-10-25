"""Manus deployment entry for MAQUA membership service.
Enables CORS, health check, and PORT env var support.
"""
from __future__ import annotations

import os

from flask_cors import CORS

# Import the main Flask app and routes from existing application
from app import app  # type: ignore

# Enable CORS for API endpoints. Configure allowed origins via ALLOWED_ORIGINS env.
CORS(app, resources={r"/api/*": {"origins": os.getenv("ALLOWED_ORIGINS", "*")}})

# Health check endpoint for platform probes
@app.route("/healthz")
def healthz():
    return "OK"

if __name__ == "__main__":  # pragma: no cover
    port = int(os.getenv("PORT", os.getenv("FLASK_PORT", "5000")))
    debug_env = os.getenv("FLASK_DEBUG", "").lower()
    debug = debug_env in {"1", "true", "yes", "on"}
    app.run(host="0.0.0.0", port=port, debug=debug)