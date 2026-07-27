FROM ubuntu:22.04

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install Xvfb, X11 dependencies, fonts, and tools needed for Google Chrome
RUN apt-get update && apt-get install -y --no-install-recommends \
        wget \
        gnupg \
        ca-certificates \
        xvfb \
        libasound2 \
        libatk-bridge2.0-0 \
        libatk1.0-0 \
        libcairo2 \
        libcups2 \
        libdbus-1-3 \
        libgbm1 \
        libgtk-3-0 \
        libnspr4 \
        libnss3 \
        libx11-xcb1 \
        libxcomposite1 \
        libxdamage1 \
        libxfixes3 \
        libxrandr2 \
        xdg-utils \
        fonts-liberation \
        fonts-noto \
        fonts-noto-color-emoji \
        fonts-freefont-ttf \
        python3 \
        python3-pip \
        python3-tk \
        python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome (official — UC mode works best with real Chrome, not Chromium)
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub \
        | gpg --dearmor > /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] \
        http://dl.google.com/linux/chrome/deb/ stable main" \
        > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -m scraper && chown -R scraper:scraper /app
USER scraper

# Ensure local bin is on PATH for pip-installed binaries
ENV PATH="/home/scraper/.local/bin:${PATH}"

COPY --chown=scraper:scraper requirements.txt ./
RUN pip3 install --user --no-cache-dir -r requirements.txt

COPY --chown=scraper:scraper src/ ./src/
COPY --chown=scraper:scraper tests/ ./tests/

ENV PYTHONPATH=/app/src
CMD ["python3", "-m", "scraper"]