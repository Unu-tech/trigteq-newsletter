# Use a lightweight Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy only the requirements first to leverage Docker's layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code into the container
COPY ./src ./src

# Ensure Python knows where to find your 'newsletter' package
ENV PYTHONPATH=/app/src

# Expose the port Uvicorn will run on
EXPOSE 8000

# Run the Uvicorn server with 2 workers and bind to all interfaces
CMD ["uvicorn", "src.newsletter.service.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
