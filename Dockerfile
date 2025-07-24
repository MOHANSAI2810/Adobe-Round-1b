# Base image
FROM python:3.12.3-slim

# Set working directory inside the container
WORKDIR /app

# Copy your script and dependencies
COPY main.py .
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create output directory (optional, if your script expects it)
RUN mkdir -p /app/output

# Default command without CLI argument, since main.py reads input.json automatically
CMD ["python", "main.py"]
