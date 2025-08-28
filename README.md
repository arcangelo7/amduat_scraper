# Theban Mapping Project Scraper - Amduat Images

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
git clone <repository-url>
cd theban_mapping_progect_scraper

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

For educational and research purposes only. All images are property of the Theban Mapping Project.