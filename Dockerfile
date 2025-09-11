# Use official Python slim image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code
COPY . .

# Expose port if needed (e.g., for DeepSeek API, but here just ETL script)
# EXPOSE 8000

# Default command to run your ETL script
CMD ["python", "etl_pipeline.py"]
