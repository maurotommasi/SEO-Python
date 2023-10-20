import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
from urllib.parse import urlparse
import re
import pandas as pd

class SEO:

    def __init__(self, language = 'english'):
        nltk.download('punkt')
        nltk.download('stopwords')
        self.stop_words = set(stopwords.words(language))

    def fetch_page_content(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return BeautifulSoup(response.text, 'html.parser')
            else:
                return None
        except Exception as e:
            print(f"Error fetching URL: {e}")
            return None

    def analyze_onpage_seo(self, soup):
        # Extract Meta Tags
        meta_tags = soup.find_all('meta')
        meta_data = {}
        for tag in meta_tags:
            name = tag.get('name', '').lower()
            content = tag.get('content', '')
            if name and content:
                meta_data[name] = content
        
        # Extract Headings (h1 to h6)
        headings = {}
        for heading_level in range(1, 7):
            heading_tags = soup.find_all(f'h{heading_level}')
            headings[f'h{heading_level}'] = [tag.text.strip() for tag in heading_tags]
        
        # Extract Links (a tags)
        links = [link.get('href') for link in soup.find_all('a', href=True) if link.get('href')]
        
        # Extract Text Content
        text_content = soup.get_text(strip=True)
        
        # Extract Images (img tags)
        images = [img.get('src') for img in soup.find_all('img', src=True) if img.get('src')]
        
        # Extract Keywords (from meta tags and headings)
        keywords = re.findall(r'\b\w+\b', ' '.join(meta_data.values()) + ' '.join(sum(headings.values(), [])))
        
        # Extract Keyword Density
        # Calculate word frequency in text content
        words = word_tokenize(text_content.lower())
        filtered_words = [word for word in words if word.isalnum() and word not in self.stop_words]
        word_counts = Counter(filtered_words)
        total_words = len(filtered_words)
        
        # Calculate keyword density
        keyword_density = {}
        for keyword in keywords:
            keyword_count = word_counts[keyword.lower()]
            density = (keyword_count / total_words) * 100
            keyword_density[keyword] = density
        
        # Extract Canonical URL
        canonical_url_tag = soup.find('link', {'rel': 'canonical'})
        canonical_url = canonical_url_tag.get('href') if canonical_url_tag else None
        
        # Extract Language
        language = soup.find('html').get('lang') if soup.find('html').get('lang') else None
        
        # Extract Charset
        charset_tag = soup.find('meta', {'charset': True})
        charset = charset_tag.get('charset') if charset_tag else None
        
        # Create separate dictionaries for each SEO element
        meta_data_dict = {'Meta Tags': [meta_data]}
        headings_dict = {'Headings': [headings]}
        links_dict = {'Links': [links]}
        text_content_dict = {'Text Content': [text_content]}
        images_dict = {'Images': [images]}
        keywords_dict = {'Keywords': [keywords]}
        keyword_density_dict = {'Keyword Density': [keyword_density]}
        canonical_url_dict = {'Canonical URL': [canonical_url]}
        language_dict = {'Language': [language]}
        charset_dict = {'Charset': [charset]}
        
        # Create DataFrames from the dictionaries
        meta_df = pd.DataFrame(meta_data_dict)
        headings_df = pd.DataFrame(headings_dict)
        links_df = pd.DataFrame(links_dict)
        text_content_df = pd.DataFrame(text_content_dict)
        images_df = pd.DataFrame(images_dict)
        keywords_df = pd.DataFrame(keywords_dict)
        keyword_density_df = pd.DataFrame(keyword_density_dict)
        canonical_url_df = pd.DataFrame(canonical_url_dict)
        language_df = pd.DataFrame(language_dict)
        charset_df = pd.DataFrame(charset_dict)
        
        # Concatenate the DataFrames along columns to create the final DataFrame
        seo_data_df = pd.concat([meta_df, headings_df, links_df, text_content_df, images_df,
                                 keywords_df, keyword_density_df, canonical_url_df,
                                 language_df, charset_df], axis=1)
        
        return seo_data_df
    
    def check_broken_links(self, soup, base_url):
        broken_links = []
        
        # Extract all links from the page
        links = soup.find_all('a', href=True)
        
        for link in links:
            url = link['href']
            if not url.startswith(('http://', 'https://')):
                # Handle relative URLs by appending them to the base URL
                url = base_url + url
            
            try:
                # Send a request to the URL and check the status code
                response = requests.head(url)
                if response.status_code >= 400:
                    broken_links.append((url, response.status_code))
            except requests.RequestException:
                # Handle connection errors or timeouts
                broken_links.append((url, "Connection Error"))

        return broken_links
    
    def generate_seo_report(self, url, save = False):
        soup = self.fetch_page_content(url)
        if soup is not None:
            onpage_seo_results = self.analyze_onpage_seo(soup)
            broken_links = self.check_broken_links(soup, urlparse(url).scheme + '://' + urlparse(url).hostname)
            
            # Generate and print SEO audit report
            print(f"SEO Audit Report for {url}:")
            print(f"On-Page SEO Analysis: {onpage_seo_results}")
            print(f"Broken Links: {broken_links}")
            if save:
                self.__save_and_display_report(onpage_seo_results, broken_links, url)
            return onpage_seo_results, [broken_links]
        else:
            print("Failed to fetch page content.")

    def __save_and_display_report(self, seo_data_df, brokenLinks, file_path = "seo_report"):
        # Generate a textual report based on the seo_data_df DataFrame
        report = ""
        for column in seo_data_df.columns:
            values = seo_data_df[column].iloc[0]  # Assuming there's only one row in the DataFrame
            report += f"\n{column}:\n"
            if isinstance(values, dict):
                for key, value in values.items():
                    report += f"  {key}: {value}\n"
            elif isinstance(values, list):
                for item in values:
                    report += f"  - {item}\n"
            else:
                report += f"  {values}\n"

        report += "\nBroken Links:\n"
        for brokenLink in brokenLinks:
            report += f"Broken Link: {brokenLink}\n"

        # Save the report to the specified file
        with open(re.sub(r'[^a-zA-Z]', '', file_path) + ".txt", 'w', encoding='utf-8') as file:
            file.write(report)

        return report