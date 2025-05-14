# 1. Use an official Python base image (slim for smaller size)
FROM python:3.11-slim

# What is this? 
# This sets the base image to Python 3.11 on a minimal Debian system, reducing image size and attack surface.

# # 2. Set environment variables for Python
# ENV PYTHONDONTWRITEBYTECODE=1 \
#     PYTHONUNBUFFERED=1

# What is this?
# Prevents Python from writing .pyc files (not needed in containers) and ensures logs are output directly.

# 3. Set the working directory in the container
WORKDIR /src

# What is this?
# All subsequent commands will run in /app. Keeps the container organized.

# 4. Install system dependencies required for your Python packages
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends \
#         build-essential \
#         tesseract-ocr \
#         libgl1 \
#         libglib2.0-0 \
#         git \
#         && rm -rf /var/lib/apt/lists/*

# What is this?
# Installs system packages needed for:
# - Building Python packages (build-essential)
# - OCR (tesseract-ocr, required by pytesseract)
# - Image processing (libgl1, libglib2.0-0, required by Pillow/torch)
# - git (sometimes needed for pip installs)
# Cleans up apt cache to reduce image size.

# 5. Copy requirements.txt and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# What is this?
# Installs all Python dependencies listed in requirements.txt. --no-cache-dir reduces image size.

# 6. Copy the rest of the application code
# COPY ./src ./src
# COPY ./README.md .

# What is this?
# Copies your source code and readme into the container.

# 7. Expose the port FastAPI will run on
EXPOSE 7860

# What is this?
# Documents that the container will listen on port 8080 (matches your uvicorn command).
# Copy toàn bộ mã nguồn
COPY . .

# 8. Set the default command to run the FastAPI app
CMD ["fastapi", "run", "src/main.py", "--port", "7860"]

# What is this?
# This starts your FastAPI app using Uvicorn, making it accessible from outside the container.
# --reload is useful for development (auto-reloads on code changes). Remove it for production.