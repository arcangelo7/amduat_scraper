#!/usr/bin/env python3

import argparse
import os
import re
import time
from typing import Dict, List, Tuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

FUNERARY_TEXT_CONFIGS = {
    'amduat': {
        'name': 'Amduat',
        'keywords': ['amduat', 'imydwat'],
        'patterns': [
            r'imydwat[,\s]*(\w+)\s+hour',
            r'amduat[,\s]*(\w+)\s+hour',
            r'(\w+)\s+hour\s+of\s+(?:the\s+)?(?:imydwat|amduat)',
            r'hour\s+(\d+)[,\s]*(?:imydwat|amduat)'
        ],
        'sections': {
            1: "prima_ora", 2: "seconda_ora", 3: "terza_ora", 4: "quarta_ora",
            5: "quinta_ora", 6: "sesta_ora", 7: "settima_ora", 8: "ottava_ora",
            9: "nona_ora", 10: "decima_ora", 11: "undicesima_ora", 12: "dodicesima_ora"
        },
        'section_mapping': {
            'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5, 'sixth': 6,
            'seventh': 7, 'eighth': 8, 'ninth': 9, 'tenth': 10, 'eleventh': 11, 'twelfth': 12,
            '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
            '7': 7, '8': 8, '9': 9, '10': 10, '11': 11, '12': 12
        }
    },
    'caverns': {
        'name': 'Book of Caverns',
        'keywords': ['caverns', 'book of caverns'],
        'patterns': [
            r'(?:book\s+of\s+)?caverns[,\s]*(\w+)\s+(?:section|part|division)',
            r'(\w+)\s+(?:section|part|division)\s+of\s+(?:the\s+)?(?:book\s+of\s+)?caverns',
            r'(?:section|part|division)\s+(\d+)[,\s]*(?:book\s+of\s+)?caverns'
        ],
        'sections': {
            1: "prima_sezione", 2: "seconda_sezione", 3: "terza_sezione", 
            4: "quarta_sezione", 5: "quinta_sezione", 6: "sesta_sezione"
        },
        'section_mapping': {
            'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5, 'sixth': 6,
            '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6
        }
    }
}


class ThebanScraper:
    def __init__(self, text_type: str):
        if text_type not in FUNERARY_TEXT_CONFIGS:
            raise ValueError(f"Unknown funerary text type: {text_type}. Available: {list(FUNERARY_TEXT_CONFIGS.keys())}")
        
        self.text_type = text_type
        self.config = FUNERARY_TEXT_CONFIGS[text_type]
        self.base_url = "https://thebanmappingproject.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def get_tombs_list(self) -> List[str]:
        """Get list of all tomb URLs from the Valley of Kings"""
        tomb_urls = []
        
        url = f"{self.base_url}/valley-kings"
        response = self.session.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=re.compile(r'/tombs/kv-\d+')):
                tomb_url = urljoin(self.base_url, link['href'])
                if tomb_url not in tomb_urls:
                    tomb_urls.append(tomb_url)
        
        return tomb_urls
    
    def sanitize_filename(self, text: str, max_length: int = 100) -> str:
        """Sanitize text to be used in filenames"""
        text = re.sub(r'[<>:"/\\|?*]', '_', text)
        text = re.sub(r'\s+', '_', text)
        text = re.sub(r'_+', '_', text)
        text = text.strip('_')
        if len(text) > max_length:
            text = text[:max_length]
        return text if text else "unnamed"
    
    def extract_tomb_name(self, soup: BeautifulSoup, tomb_url: str) -> str:
        """Extract tomb name from page title or URL"""
        # Try to get from page title first
        title_elem = soup.find('title')
        if title_elem:
            title = title_elem.get_text(strip=True)
            # Remove common site suffixes
            title = re.sub(r'\s*-\s*Theban Mapping Project.*', '', title, flags=re.IGNORECASE)
            if title and title.lower() not in ['home', 'theban mapping project']:
                return title
        
        # Try to get from h1 heading
        h1_elem = soup.find('h1')
        if h1_elem:
            h1_text = h1_elem.get_text(strip=True)
            if h1_text:
                return h1_text
        
        # Fallback to URL parsing
        match = re.search(r'/tombs/([^/]+)', tomb_url)
        if match:
            return match.group(1).replace('-', ' ').title()
        
        return "Unknown_Tomb"
    
    def extract_funerary_text_images(self, tomb_url: str) -> Dict[int, List[Tuple[str, str, str]]]:
        """Extract funerary text images from a specific tomb page with captions and tomb name"""
        sections = self.config['sections']
        images_by_section = {i: [] for i in sections.keys()}
        
        print(f"Analyzing tomb: {tomb_url}")
        response = self.session.get(tomb_url)
        
        if response.status_code != 200:
            print(f"Failed to access {tomb_url}")
            return images_by_section
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract tomb name
        tomb_name = self.extract_tomb_name(soup, tomb_url)
        
        # Get patterns and mappings from configuration
        patterns = self.config['patterns']
        section_mapping = self.config['section_mapping']
        keywords = self.config['keywords']
        
        images = soup.find_all('img')
        
        for element in soup.find_all(attrs={'data-src': True}):
            src = element.get('data-src')
            if src:
                images.append({'src': src})
        
        for img in images:
            img_src = img.get('src') or img.get('data-src')
            if not img_src:
                continue
                
            if any(skip in img_src.lower() for skip in ['logo', 'icon', 'compass', 'hieroglyph']):
                continue
            
            if '/styles/' in img_src:
                match = re.search(r'/styles/[^/]+/public/(.+)', img_src)
                if match:
                    img_src = f"/sites/default/files/{match.group(1)}"
            
            img_url = urljoin(self.base_url, img_src)
            
            img_context = ""
            if img.get('alt'):
                img_context = img.get('alt').lower()
            
            # Get text context from parent elements
            parent = img.parent
            context_text = ""
            for _ in range(3):  # Check up to 3 levels up
                if parent:
                    parent_text = parent.get_text().lower()
                    img_context += " " + parent_text
                    if not context_text:  # Keep the first (closest) parent text for caption
                        context_text = parent.get_text(strip=True)
                    parent = parent.parent
            
            # Try to identify which section this image belongs to
            section_found = None
            matching_text = ""
            for pattern in patterns:
                matches = re.findall(pattern, img_context)
                for match in matches:
                    if match.lower() in section_mapping:
                        section_found = section_mapping[match.lower()]
                        # Extract the sentence/phrase containing the keyword
                        sentences = re.split(r'[.;!?\n]', context_text)
                        for sentence in sentences:
                            if any(keyword in sentence.lower() for keyword in keywords):
                                matching_text = sentence.strip()
                                break
                        if not matching_text:
                            # If no sentence found, use a portion of context containing keywords
                            words = context_text.split()
                            for i, word in enumerate(words):
                                if any(keyword in word.lower() for keyword in keywords):
                                    start = max(0, i-5)
                                    end = min(len(words), i+10)
                                    matching_text = ' '.join(words[start:end])
                                    break
                        break
                if section_found:
                    break
            
            # If we found a section association, add the image with the matching text as caption
            if section_found and section_found in sections:
                img_exists = any(url == img_url for url, _, _ in images_by_section[section_found])
                if not img_exists:
                    # Use the text that matched our pattern as caption, fallback to alt/title
                    caption = matching_text or img.get('alt') or img.get('title') or ""
                    images_by_section[section_found].append((img_url, caption, tomb_name))
                    print(f"  Found image for section {section_found}: {os.path.basename(img_url)}")
                    if caption:
                        print(f"    Caption: {caption[:100]}...")
        
        return images_by_section
    
    def download_image(self, url: str, filepath: str) -> bool:
        """Download an image from URL to filepath"""
        try:
            response = self.session.get(url, stream=True)
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                return True
        except Exception as e:
            print(f"Error downloading {url}: {e}")
        return False
    
    def create_folder_structure(self):
        """Create the folder structure for organizing images"""
        base_dir = self.text_type
        
        os.makedirs(base_dir, exist_ok=True)
        
        for _, section_name in self.config['sections'].items():
            section_dir = os.path.join(base_dir, section_name)
            os.makedirs(section_dir, exist_ok=True)
        
        print(f"Created folder structure in '{base_dir}' directory")
        return base_dir
    
    def scrape_all_tombs(self):
        """Main function to scrape all tombs and organize images"""
        print(f"Starting {self.config['name']} scraper...")
        
        base_dir = self.create_folder_structure()
        
        print("\nFetching tomb list...")
        tomb_urls = self.get_tombs_list()
        print(f"Found {len(tomb_urls)} tombs")
        
        sections = self.config['sections']
        all_images = {i: {} for i in sections.keys()}
        
        for tomb_url in tomb_urls:
            images_by_section = self.extract_funerary_text_images(tomb_url)
            
            for section, img_data in images_by_section.items():
                for img_url, caption, tomb_name in img_data:
                    if img_url not in all_images[section]:
                        all_images[section][img_url] = (caption, tomb_name)
            
            # Be polite to the server
            time.sleep(1)
        
        print("\nDownloading images...")
        total_downloaded = 0
        
        for section_num, img_dict in all_images.items():
            if not img_dict:
                continue
                
            section_dir = os.path.join(base_dir, sections[section_num])
            print(f"\nSection {section_num} ({sections[section_num]}): {len(img_dict)} images")
            
            for idx, (img_url, (caption, tomb_name)) in enumerate(img_dict.items(), 1):
                tomb_id = re.search(r'/kv-(\d+)', img_url)
                tomb_id_prefix = f"kv{tomb_id.group(1)}_" if tomb_id else ""
                
                base_filename = os.path.basename(img_url).split('?')[0]
                extension = os.path.splitext(base_filename)[1] or '.jpg'
                
                # Sanitize tomb name
                sanitized_tomb_name = self.sanitize_filename(tomb_name)
                
                if caption:
                    sanitized_caption = self.sanitize_filename(caption)
                    filename = f"{tomb_id_prefix}{sanitized_tomb_name}_{sanitized_caption}{extension}"
                else:
                    # Caption should always exist if we found the image through keywords
                    if base_filename:
                        filename = f"{tomb_id_prefix}{sanitized_tomb_name}_{base_filename}"
                    else:
                        filename = f"{tomb_id_prefix}{sanitized_tomb_name}_image_{idx}{extension}"
                
                filepath = os.path.join(section_dir, filename)
                
                if self.download_image(img_url, filepath):
                    print(f"  Downloaded: {os.path.basename(filepath)}")
                    total_downloaded += 1
                
                time.sleep(0.5)
        
        print(f"\nScraping complete! Downloaded {total_downloaded} images")
        print(f"Images organized in '{base_dir}' directory")


def main():    
    parser = argparse.ArgumentParser(description='Scrape funerary text images from the Theban Mapping Project')
    parser.add_argument('text_type', 
                       choices=list(FUNERARY_TEXT_CONFIGS.keys()),
                       help='Type of funerary text to scrape')
    
    args = parser.parse_args()
    
    scraper = ThebanScraper(text_type=args.text_type)
    scraper.scrape_all_tombs()


if __name__ == "__main__":
    main()