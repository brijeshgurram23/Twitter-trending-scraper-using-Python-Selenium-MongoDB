# Use the official Python 3.10 image as the base
FROM python:3.10

# Set the working directory
WORKDIR /app

# Install system dependencies, Chrome, and ChromeDriver
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg && \
    # Add Google's signing key and stable repository for Chrome
    curl -sSL https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    # Download and install ChromeDriver
    CHROME_VERSION=$(google-chrome --version | grep -oP '[0-9.]+' | head -1) && \
    CHROMEDRIVER_VERSION=$(curl -sSL https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION) && \
    curl -q "https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip" -O chromedriver.zip && \
    unzip chromedriver.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm chromedriver.zip && \
    # Clean up
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the .env file into the Docker image
COPY .env /app/.env

# Upgrade pip and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# Expose the application port
EXPOSE 5000

# Copy the application code to the container
COPY . /app

# Set the command to run the application
CMD ["python", "main.py"]
