# Use the official Playwright image with Python support.
# Using a specific version is recommended for stability.
FROM mcr.microsoft.com/playwright/python:v1.54.0-noble

# Set the working directory inside the container
WORKDIR /code

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install the browser binaries and their dependencies
RUN playwright install --with-deps

# Copy the main Python script into the container
COPY . /code

# Set the command to run when the container starts
CMD ["rq", "worker"]
