# Base image
FROM python:3.12.3-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements first (for cache efficiency)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy main script
COPY main.py .

# Copy input folder (and its PDFs/input.json)
COPY input ./input

# Create output directory
RUN mkdir -p /app/output

# Run the script (input.json is loaded automatically from /app/input)
CMD ["python", "main.py"]
