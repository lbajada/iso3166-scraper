FROM python:3-alpine

# Install chromium and its matching chromedriver
RUN apk update && \
    apk add --no-cache \
        chromium \
        chromium-chromedriver

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY iso3166_scraper.py ./

CMD [ "python", "./iso3166_scraper.py" ]