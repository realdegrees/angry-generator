# Use a lightweight base image
FROM python:3.13-alpine

RUN apk add --no-cache bash ffmpeg

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Make the start script executable
RUN chmod +x start.sh

# Expose the port the app runs on
EXPOSE 5000

CMD ["bash", "./start.sh"]