FROM python:3.10-slim

WORKDIR /app

# Install system dependencies and Google Chrome
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    gnupg && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install ChromeDriver (ensure compatibility with Google Chrome)
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d '.' -f 1) && \
    CHROMEDRIVER_VERSION=$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION) && \
    wget https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip -d /usr/local/bin/ && \
    rm chromedriver_linux64.zip && \
    chmod +x /usr/local/bin/chromedriver

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Expose Flask default port
EXPOSE 5000

# Default command to run the application
CMD ["python", "main.py"]
