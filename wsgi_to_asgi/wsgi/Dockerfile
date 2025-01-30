# Dockerfile for WSGI (Flask) Application

# Use official Python base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 5000 for the WSGI server
EXPOSE 8000

# Run the application with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8000", "wsgi:app", "--workers", "4"]

