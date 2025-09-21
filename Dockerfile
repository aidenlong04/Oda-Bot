# Use official Python runtime as a parent image
FROM python:3.12-slim

# Set workdir
WORKDIR /app

# Copy requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application
COPY . /app

# Expose nothing (Discord bot uses outbound connections)

# Run the bot
CMD ["python", "oda_bot.py"]
