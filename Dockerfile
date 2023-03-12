# Start from a base image of Python 3.8
FROM python:3.8

# Set environment variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files to disk (reduces clutter)
# PYTHONUNBUFFERED: Ensures Python output is sent straight to terminal (useful for logging)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt -v

# Copy the current directory contents into the container at /app
COPY . /app

# Expose port 3306, 5000 for the MySQL server and financial django server
EXPOSE 5000
EXPOSE 3306
