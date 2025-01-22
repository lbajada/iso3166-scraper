# iso3166-scraper
Scrapes the official ISO website for all countries and their subdivision under the ISO 3166 standard.

Run `docker compose up` to start scraping. A folder called `countries` will be created in the same location the `docker-compose.yaml` file is executed and gradually starts being filled with a JSON file for each country. A file called `all_countries.json` will have all the countries in one place.