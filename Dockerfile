# 1. Use an official Python base image (slim for smaller size)
FROM python:3.11-slim

# 2. Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. Set the working directory in the container
WORKDIR /src

# 4. Install system dependencies required for Python packages and llama-cpp-python
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    # gcc \
    # g++ \
    cmake \
    # tesseract-ocr \
    # libgl1 \
    libglib2.0-0 \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /tmp/cache /tmp/vector_store /.cache && \
    chown -R 1000:1000 /tmp /.cache

# 5. Copy requirements.txt and install Python dependencies
COPY requirements.txt .
# RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Install llama-cpp-python first (faster rebuilds)
RUN pip install --no-cache-dir "llama-cpp-python==0.3.8"

# Remove llama line from requirements and install the rest
RUN grep -v "llama-cpp-python" requirements.txt > requirements-no-llama.txt && \
    pip install --no-cache-dir -r requirements-no-llama.txt

# 6. Copy the rest of the application code
COPY . .

# 7. Expose the port FastAPI will run on
EXPOSE 7860

# 8. Set the default command to run the FastAPI app
CMD ["fastapi", "run", "src/main.py", "--port", "7860"]