# Use Python
FROM python:3.10

# Create working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port Fly will use
EXPOSE 8080

# Run the app using gunicorn instead of flask run
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
