# 1. Use an official Python base image (slim for smaller size)
FROM python:3.11-slim

# 2. Set environment variables for Python and Hugging Face
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/src/cache/huggingface \
    HUGGINGFACE_HUB_CACHE=/src/cache/huggingface

# 3. Create cache directory with appropriate permissions
RUN mkdir -p /src/cache/huggingface && \
    chown -R 1000:1000 /src/cache

# 4. Set the working directory in the container
WORKDIR /src

# 5. Install system dependencies required for Python packages and llama-cpp-python
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        g++ \
        cmake \
        tesseract-ocr \
        libgl1 \
        libglib2.0-0 \
        git \
        && rm -rf /var/lib/apt/lists/*

# 6. Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# 7. Copy the rest of the application code
COPY . .

# 8. Expose the port FastAPI will run on
EXPOSE 7860

# 9. Set the default command to run the FastAPI app
CMD ["fastapi", "run", "src/main.py", "--port", "7860"]