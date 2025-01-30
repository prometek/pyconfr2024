# Dockerfile for ASGI (FastAPI) Application

# Use official Python base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

RUN apt-get update && apt-get install -y gcc python3-dev

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 8000 for the ASGI server
EXPOSE 8000

# Run the application with Uvicorn
CMD ["sleep", "infinity"]
