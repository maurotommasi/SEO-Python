# SEO Analyzer

The SEO Analyzer is a Python tool designed to provide a detailed analysis of on-page SEO elements and check for broken links on a webpage. It uses various libraries like `requests`, `BeautifulSoup`, `nltk`, and `pandas` to fetch webpage content, process HTML, perform text analysis, and generate insightful reports.

## Components

### 1. **Initialization**

The `SEO` class is initialized with a language (default: English) and downloads necessary resources using `nltk.download('punkt')` and `nltk.download('stopwords')`.

### 2. **Fetching Page Content**

The `fetch_page_content` method fetches the HTML content of the given URL and returns a BeautifulSoup object. It handles HTTP errors and exceptions.

### 3. **Analyzing On-Page SEO**

The `analyze_onpage_seo` method extracts meta tags, headings, links, text content, images, keywords, keyword density, canonical URL, language, and charset from the webpage's HTML. It tokenizes words, calculates keyword density, and organizes the data into pandas DataFrames.

### 4. **Checking Broken Links**

The `check_broken_links` method extracts all links from the webpage and checks their HTTP status codes. It appends broken links to a list and returns it.

### 5. **Generating SEO Report**

The `generate_seo_report` method generates and prints an SEO audit report for the given URL. Optionally, it saves the report to a file and returns the on-page SEO analysis and broken links data.

### 6. **Saving Reports**

The `generate_seo_report` method allows saving reports to a file by setting the `save` parameter to `True`. The report will be saved in the current directory with the filename `seo_report.txt`.

## Usage

```python
url = "https://example.com"
analyzer = SEO()
onpage_seo, broken_links = analyzer.generate_seo_report(url, save=True)
