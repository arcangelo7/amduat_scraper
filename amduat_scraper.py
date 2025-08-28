#!/usr/bin/env python3

import os
import re
import time
from typing import Dict, List
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


class AmduatScraper:
    def __init__(self):
        self.base_url = "https://thebanmappingproject.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.amduat_hours = {
            1: "prima_ora",
            2: "seconda_ora", 
            3: "terza_ora",
            4: "quarta_ora",
            5: "quinta_ora",
            6: "sesta_ora",
            7: "settima_ora",
            8: "ottava_ora",
            9: "nona_ora",
            10: "decima_ora",
            11: "undicesima_ora",
            12: "dodicesima_ora"
        }
        
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
    
    def extract_amduat_images(self, tomb_url: str) -> Dict[int, List[str]]:
        """Extract Amduat/Imydwat images from a specific tomb page"""
        images_by_hour = {i: [] for i in range(1, 13)}
        
        print(f"Analyzing tomb: {tomb_url}")
        response = self.session.get(tomb_url)
        
        if response.status_code != 200:
            print(f"Failed to access {tomb_url}")
            return images_by_hour
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all mentions of Imydwat/Amduat with hour references
        patterns = [
            r'imydwat[,\s]*(\w+)\s+hour',
            r'amduat[,\s]*(\w+)\s+hour',
            r'(\w+)\s+hour\s+of\s+(?:the\s+)?(?:imydwat|amduat)',
            r'hour\s+(\d+)[,\s]*(?:imydwat|amduat)'
        ]
        
        hour_mapping = {
            'first': 1, 'second': 2, 'third': 3, 'fourth': 4,
            'fifth': 5, 'sixth': 6, 'seventh': 7, 'eighth': 8,
            'ninth': 9, 'tenth': 10, 'eleventh': 11, 'twelfth': 12,
            '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
            '7': 7, '8': 8, '9': 9, '10': 10, '11': 11, '12': 12
        }
        
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
            
            parent = img.parent
            for _ in range(3):  # Check up to 3 levels up
                if parent:
                    img_context += " " + parent.get_text().lower()
                    parent = parent.parent
            
            # Try to identify which hour this image belongs to
            hour_found = None
            for pattern in patterns:
                matches = re.findall(pattern, img_context)
                for match in matches:
                    if match.lower() in hour_mapping:
                        hour_found = hour_mapping[match.lower()]
                        break
                if hour_found:
                    break
            
            # If we found an hour association, add the image
            if hour_found and 1 <= hour_found <= 12:
                if img_url not in images_by_hour[hour_found]:
                    images_by_hour[hour_found].append(img_url)
                    print(f"  Found image for hour {hour_found}: {os.path.basename(img_url)}")
        
        return images_by_hour
    
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
        base_dir = "amduat"
        
        os.makedirs(base_dir, exist_ok=True)
        
        for _, hour_name in self.amduat_hours.items():
            hour_dir = os.path.join(base_dir, hour_name)
            os.makedirs(hour_dir, exist_ok=True)
        
        print(f"Created folder structure in '{base_dir}' directory")
        return base_dir
    
    def scrape_all_tombs(self):
        """Main function to scrape all tombs and organize images"""
        print("Starting Amduat scraper...")
        
        base_dir = self.create_folder_structure()
        
        print("\nFetching tomb list...")
        tomb_urls = self.get_tombs_list()
        print(f"Found {len(tomb_urls)} tombs")
        
        all_images = {i: set() for i in range(1, 13)}
        
        for tomb_url in tomb_urls:
            images_by_hour = self.extract_amduat_images(tomb_url)
            
            for hour, img_urls in images_by_hour.items():
                all_images[hour].update(img_urls)
            
            # Be polite to the server
            time.sleep(1)
        
        print("\nDownloading images...")
        total_downloaded = 0
        
        for hour_num, img_urls in all_images.items():
            if not img_urls:
                continue
                
            hour_dir = os.path.join(base_dir, self.amduat_hours[hour_num])
            print(f"\nHour {hour_num} ({self.amduat_hours[hour_num]}): {len(img_urls)} images")
            
            for idx, img_url in enumerate(img_urls, 1):
                tomb_id = re.search(r'/kv-(\d+)', img_url)
                tomb_prefix = f"kv{tomb_id.group(1)}_" if tomb_id else ""
                
                filename = os.path.basename(img_url).split('?')[0]
                if not filename:
                    filename = f"image_{idx}.jpg"
                
                filepath = os.path.join(hour_dir, f"{tomb_prefix}{filename}")
                
                if self.download_image(img_url, filepath):
                    print(f"  Downloaded: {os.path.basename(filepath)}")
                    total_downloaded += 1
                
                time.sleep(0.5)
        
        print(f"\nScraping complete! Downloaded {total_downloaded} images")
        print(f"Images organized in '{base_dir}' directory")

def main():
    scraper = AmduatScraper()
    scraper.scrape_all_tombs()

if __name__ == "__main__":
    main()