# Step 1: Base image
FROM python:3.9-slim

# Step 2: Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tcpdump \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create uploads directory
RUN mkdir -p uploads && chmod 777 uploads

# Step 5: Expose the Flask port
EXPOSE 5001

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# Step 6: Run the app
CMD ["python", "app.py"]