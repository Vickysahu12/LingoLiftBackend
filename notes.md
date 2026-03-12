Steps we follow in this Project:
# 1. Python -m venv venv
# 2. venv/scripts/activate
# 3. pip install "fastapi[standard]" "sqlalchemy[asyncio]" asyncpg alembic python-decouple "python-jose[cryptography]" "passlib[bcrypt]"    cryptography google-auth httpx
# 4. pip freeze > requirements.txt

Alembic Info:
# Jab bhi model banayenge ya change karenge —

# 1. Migration file auto-generate karo
alembic revision --autogenerate -m "what changed"

# 2. Database pe apply karo
alembic upgrade head

# 3. Agar galti ho — rollback
alembic downgrade -1