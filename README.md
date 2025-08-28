# Amduat Scraper - Theban Mapping Project

Web scraper for extracting Amduat (Book of the Hidden Chamber) images from the Theban Mapping Project website.

## Description

This project scrapes the Theban Mapping Project website to collect images of the Amduat, an ancient Egyptian funerary text that describes the journey of the sun god Ra through the twelve hours of the night. The scraper organizes images by each of the twelve hours, downloading them in the highest available resolution.

## Features

- Automatically discovers all tombs in the Valley of the Kings
- Identifies and extracts Amduat/Imydwat images from tomb documentation
- Organizes images by the twelve hours of the night
- Downloads images in original high resolution
- Creates structured folder hierarchy for easy navigation

## Installation

This project uses `uv` for dependency management.

```bash
# Clone the repository
git clone https://github.com/arcangelo7/amduat_scraper.git
cd amduat_scraper

# Install dependencies with uv
uv sync
```

## Usage

Run the scraper using:

```bash
uv run python amduat_scraper.py
```

Or use the installed script:

```bash
uv run amduat-scraper
```

## Notes

- The scraper includes delays between requests to be respectful to the server
- Images are downloaded only once (no duplicates across different tombs)
- The scraper identifies Amduat content through text analysis of the tomb descriptions

## License

This software is licensed under the ISC License. See the [LICENSE](LICENSE) file for details.

Note: All images downloaded by this scraper are property of the Theban Mapping Project and subject to their terms of use.