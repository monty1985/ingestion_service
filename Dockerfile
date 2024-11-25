# Use an official Python image from DockerHub
FROM python:3.12-slim

# Install ping and netcat utilities (choose netcat-openbsd)
RUN apt-get update && apt-get install -y iputils-ping netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory once and copy files there
WORKDIR /app

# Copy the requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire `src` directory into `/app/src`
COPY src /app/src

# Expose the FastAPI port
EXPOSE 8000

# Run the FastAPI server from the correct location
CMD ["uvicorn", "src.main.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
