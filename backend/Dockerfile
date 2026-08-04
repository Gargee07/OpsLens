FROM python:3.14-slim

WORKDIR /app

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
# FROM python:3.14-slim

# WORKDIR /app

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# EXPOSE 8000
# CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
