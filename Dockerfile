# Use official Python image as base
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (for better Docker caching)
COPY requirements.txt .

# Install dependencies with increased timeout and retries
RUN pip install --default-timeout=100 --retries=5 -r requirements.txt

# Copy all application files
COPY . .

# Expose Streamlit default port
EXPOSE 8501

# Command to run Streamlit app
CMD ["streamlit", "run", "mediconsult_app.py", "--server.port=8501", "--server.address=0.0.0.0"]