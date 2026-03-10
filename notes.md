Steps we follow in this Project:
1. Python -m venv venv
2. venv/scripts/activate
3. pip install "fastapi[standard]" "sqlalchemy[asyncio]" asyncpg alembic python-decouple "python-jose[cryptography]" "passlib[bcrypt]"    cryptography google-auth httpx
4. pip freeze > requirements.txt