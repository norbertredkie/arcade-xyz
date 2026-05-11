#!/bin/bash
set -e
pip install fastapi uvicorn pydantic stripe anthropic supabase python-jose 2>/dev/null || true
uvicorn src.api.main:app --host 0.0.0.0 --port 8002 &
echo "✅ Arcade.XYZ API running at http://localhost:8002"
