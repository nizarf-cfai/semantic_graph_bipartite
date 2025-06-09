FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create a directory for the graph file
RUN mkdir -p /app/data

# Set environment variables
ENV PORT=8050

# Expose the port
EXPOSE 8050

# Run the application
CMD ["python", "app.py"] 