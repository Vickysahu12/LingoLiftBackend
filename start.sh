export PATH=/opt/venv/bin:$PATH
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT