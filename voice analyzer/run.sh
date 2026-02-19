#!/usr/bin/env bash
cd "voice analyzer"
python3 -m venv .venv
# Use POSIX-compatible activation and explicit python -m pip for reliability
. .venv/bin/activate
python3 -m pip install -r requirements.txt

# Terminal 1: Start the API (run in its own terminal)
# source .venv/bin/activate
# uvicorn app.main:app --reload

# Terminal 2: Start the dashboard (run in its own terminal)
# source .venv/bin/activate
# streamlit run dashboard/streamlit_app.py