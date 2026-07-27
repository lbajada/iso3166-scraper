# ISO 3166 Scraper

A headless web scraper that extracts the complete [ISO 3166](https://www.iso.org/iso-3166-country-codes.html) dataset directly from the official ISO Online Browsing Platform (OBP). It produces structured JSON files containing country codes, subdivision data, administrative language information, and change history for every entry in the standard.

The scraper uses [SeleniumBase](https://github.com/seleniumbase/SeleniumBase) in UC (Undetected-Chromedriver) mode with a virtual display to automatically bypass Cloudflare Turnstile protection, making it work reliably from Docker containers and headless servers.

## What It Scrapes

For each ISO 3166 entry the scraper collects:

| Field | Description |
|---|---|
| `alpha2_code` | ISO 3166-1 alpha-2 code (e.g. `DE`) |
| `alpha3_code` | ISO 3166-1 alpha-3 code (e.g. `DEU`) |
| `numeric_code` | ISO 3166-1 numeric code (e.g. `276`) |
| `short_name` | Official short name in upper case |
| `short_name_lower_case` | Official short name in title case |
| `full_name` | Full official name (e.g. *the Federal Republic of Germany*) |
| `independent` | Whether the entity is an independent country |
| `status` | Assignment status (e.g. *Officially assigned*, *Exceptionally reserved*) |
| `remarks` | Any remarks from the standard |
| `territory_name` | Territory name, if applicable |
| `subdivision_categories` | Category counts and locale labels for ISO 3166-2 subdivisions |
| `subdivisions` | Complete ISO 3166-2 subdivision list with codes, names, and parent relationships |
| `additional_information` | Administrative languages with alpha-2/alpha-3 codes and local short names |
| `change_history` | Chronological list of changes with dates and bilingual (EN/FR) descriptions |

## Output

The scraper writes to a `countries/` directory:

- **`{alpha2_code}.json`** — One file per country/entry (e.g. `DE.json`, `MT.json`).
- **`countries.json`** — A single combined file with all entries under a top-level `"countries"` array.

All fields that have no value are represented as `null` in the JSON output. See the [OpenAPI specification](openapi.yaml) for the full schema definition.

## Requirements

- **Docker** (recommended), **or**
- Python 3.10+ with Google Chrome and a display server (or Xvfb)

## Quick Start

### Docker Compose (recommended)

The simplest way to run the scraper — no local Python, Chrome, or display server needed:

```bash
docker compose up
```

This builds the image (if needed), runs the scraper, and writes the JSON output to a `countries/` directory in your current working directory.

You can also pass arguments by overriding the default command:
```bash
docker compose run --rm iso3166-scraper python3 -m iso3166_scraper --countries US,CA
```

> **Note:** The first run downloads and installs the matching ChromeDriver automatically. Subsequent runs use the cached driver.

### Docker (manual)

If you prefer to build and run manually:

```bash
# Build the image
docker build -t iso3166-scraper .

# Run the scraper (default behavior)
docker run --shm-size=2g -v ./countries:/app/countries:rw iso3166-scraper

# Run with custom options
docker run --shm-size=2g -v ./countries:/app/countries:rw iso3166-scraper python3 -m iso3166_scraper --all-only
```

> **Important:** The `--shm-size=2g` flag is required. Chrome uses `/dev/shm` for shared memory during rendering — the default 64MB in Docker will cause crashes. This is already configured in `docker-compose.yaml`.

### Run the smoke test

Before running the full scrape (~314 countries), you can verify that Cloudflare Turnstile bypass is working:

```bash
docker compose run --rm iso3166-scraper python3 tests/test_turnstile.py
```

Expected output:

```
2026-07-27 07:08:16  INFO      Starting Turnstile bypass smoke test …
2026-07-27 07:08:31  INFO      SUCCESS — Cloudflare bypassed, country list loaded!
2026-07-27 07:08:31  INFO      Page title: Country Codes Collection
```

### Run locally (without Docker)

If you prefer to run directly on your machine:

1. **Install Google Chrome** (the official version, not Chromium):

    ```bash
    # Debian/Ubuntu
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
    sudo apt-get update && sudo apt-get install -y google-chrome-stable
    ```

2. **Install Xvfb** (required on headless servers — skip this if you have a desktop environment):

    ```bash
    sudo apt-get install -y xvfb
    ```

3. **Install Python dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Run the scraper:**

    ```bash
    PYTHONPATH=src python -m iso3166_scraper
    ```

    You can optionally pass the following arguments:
    - `--all-only`: Only output the `countries.json` file (skips creating individual country files).
    - `--countries`: Provide a comma-separated list of 2-letter country codes to scrape only those specific countries (e.g., `--countries US,CA,GB`).

> **Why Google Chrome and not Chromium?** SeleniumBase UC mode patches the ChromeDriver binary to evade bot detection. These patches are built and tested against official Google Chrome releases. Chromium builds may use different versioning or be missing features that UC mode depends on, leading to detection or crashes.

## How It Bypasses Cloudflare

The ISO OBP website is protected by Cloudflare Turnstile, which blocks headless browsers and automated scraping tools. This scraper uses a multi-layered approach:

1. **Virtual display (Xvfb)** — Instead of Chrome's `--headless` flag (which Cloudflare fingerprints), Chrome runs in normal "headed" mode inside a virtual X11 framebuffer. To Cloudflare, it looks like a regular desktop browser.

2. **UC mode (Undetected-Chromedriver)** — SeleniumBase patches the ChromeDriver binary, renames Chrome DevTools Protocol variables, and blocks common automation detection scripts.

3. **Strategic WebDriver disconnect** — During page loads, the WebDriver is temporarily disconnected from Chrome. Cloudflare's JavaScript challenge runs while no automation hooks are present, so it passes. The WebDriver reconnects after the challenge completes.

4. **Turnstile click fallback** — If a Turnstile checkbox challenge appears, `uc_gui_click_captcha()` uses PyAutoGUI to click it on the virtual display, simulating a real mouse click.

## Troubleshooting

### Blocked by Cloudflare despite bypass

If the scraper is consistently blocked:

- **Datacenter IPs** — If running on a cloud server (AWS, GCP, Azure, etc.), your IP range may be flagged by Cloudflare regardless of browser fingerprinting. Residential IPs work best.
- **Rate limiting** — If you're re-running the scraper frequently, Cloudflare may start blocking your IP temporarily. Wait a few minutes and try again.
- **Chrome version mismatch** — SeleniumBase auto-downloads the matching ChromeDriver, but if Chrome was updated mid-scrape, restart the container to pick up the new driver.

### Chrome crashes in Docker

- Ensure `shm_size: '2g'` is set in `docker-compose.yaml` (or `--shm-size=2g` with `docker run`). Chrome uses `/dev/shm` for rendering and the default 64MB is not enough.
- If running on a resource-constrained system, ensure at least 2GB of RAM is available to the container.

### "Display not found" errors

- On a headless server without Docker, ensure `xvfb` is installed (`sudo apt-get install xvfb`). SeleniumBase manages the virtual display automatically when `xvfb=True` is set.
- Inside Docker, the Dockerfile already installs Xvfb and all required X11 libraries.

## Project Structure

```
src/                            # Source code directory
└── iso3166_scraper/            # Python package
    ├── __init__.py             # Public API exports
    ├── __main__.py             # Entry point (python -m iso3166_scraper)
    ├── models.py               # Dataclass models (Country, Subdivision, etc.)
    ├── serialization.py        # JSON normalization and serialization
    ├── scraper.py              # ISO3166Scraper class (browser + parsing)
    └── output.py               # File I/O (save_all_countries)
tests/                          # Test suite
├── __init__.py
├── test_models.py              # Unit tests for data models
├── test_output.py              # Integration tests for file output
├── test_serialization.py       # Unit tests for JSON serialization
└── test_turnstile.py           # Smoke test for Cloudflare Turnstile bypass
requirements.txt                # Python dependencies (seleniumbase)
requirements-dev.txt            # Development dependencies (pytest, pylint)
Makefile                        # Make targets (run, dev, test, lint, etc.)
Dockerfile                      # Container image (Ubuntu 22.04 + Chrome + Xvfb)
docker-compose.yaml             # One-command Docker setup
countries/                      # Output directory (created at runtime)
├── AC.json
├── AD.json
├── ...
└── countries.json
.pylintrc                       # Pylint configuration
.github/workflows/
└── ci.yml                      # CI pipeline (lint → test → build → push)
LICENSE                         # MIT License
```

## CI / CD

The GitHub Actions [CI pipeline](.github/workflows/ci.yml) runs on every push and pull request to `main`:

1. **Lint** — Runs Pylint against the `src/iso3166_scraper/` package.
2. **Validate OpenAPI** — Validates `openapi.yaml` against the OpenAPI specification.
3. **Build & Push** — Builds the Docker image and pushes it to both GitHub Container Registry and Docker Hub (only on push to `main`, after lint and validation pass).

## License

[MIT](LICENSE) © Luke Bajada