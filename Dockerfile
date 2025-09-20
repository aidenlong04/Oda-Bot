FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot code
COPY bot.py .

# Create a non-root user for security
RUN useradd -m -u 1001 botuser
USER botuser

# Run the bot
CMD ["python", "bot.py"]