# Theban Scraper - Theban Mapping Project

Web scraper for extracting funerary text images from the Theban Mapping Project website.

## Description

This project scrapes the Theban Mapping Project website to collect images of ancient Egyptian funerary texts. Currently supports:

- **Amduat** (Book of the Hidden Chamber): Describes the sun god Ra's journey through the twelve hours of the night
- **Book of Caverns**: Another ancient Egyptian funerary text describing the underworld journey

The scraper organizes images by their respective sections (hours for Amduat, sections for Book of Caverns), downloading them in the highest available resolution.

## Features

- Automatically discovers all tombs in the Valley of the Kings
- Identifies and extracts funerary text images from tomb documentation
- Organizes images by their respective sections (hours, divisions, etc.)
- Downloads images in original high resolution
- Creates structured folder hierarchy for easy navigation

## Installation

This project uses `uv` for dependency management.

```bash
# Clone the repository
git clone https://github.com/arcangelo7/theban_scraper.git
cd theban_scraper

# Install dependencies with uv
uv sync
```

## Usage

Run the scraper specifying the funerary text type:

```bash
# Scrape Amduat images
uv run python theban_scraper.py amduat

# Scrape Book of Caverns images
uv run python theban_scraper.py caverns
```

## License

This software is licensed under the ISC License. See the [LICENSE](LICENSE) file for details.

Note: All images downloaded by this scraper are property of the Theban Mapping Project and subject to their terms of use.