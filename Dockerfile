FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /src

# 1. Cài các package cần thiết
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libglib2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy requirements và thư viện local
COPY requirements_for_server.txt ./
COPY local_packages_for_server/ /tmp/local_packages_for_server/

# 3. Cài đặt gói từ local
RUN pip install --no-cache-dir --find-links=/tmp/local_packages_for_server -r requirements_for_server.txt

# 4. Copy mã nguồn
COPY src/ .

# 5. Expose và chạy app
EXPOSE 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
