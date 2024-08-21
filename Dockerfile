FROM python:3.9-slim

# Set the working directory as app
WORKDIR /app

# Copy the requirements file to the container /app
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the working directory to the container at /app
COPY . .

# Export port 80 to host
EXPOSE 80

# Define the command to run the app using gunicorn, specifying Flask server
CMD ["gunicorn", "-b", "0.0.0.0:80", "app:app"]

