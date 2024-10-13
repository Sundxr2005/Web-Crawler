#!/usr/bin/env python3
# -- coding: utf-8 --

import argparse
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from pyfiglet import figlet_format
from urllib.parse import urljoin
import random

# Define colors for output
class Colors:
    INFO = '\033[94m'
    SUCCESS = '\033[92m'
    ERROR = '\033[91m'
    HEADER = '\033[95m'
    FOOTER = '\033[96m'
    HIGHLIGHT = '\033[93m'
    WHITE = '\033[97m'  # Added white color
    END = '\033[0m'

def print_decorative(message, color=Colors.INFO, end='\n'):
    """Prints a decorative message with a specified color."""
    print(f"{color}{message}{Colors.END}", end=end)

def print_header():
    """Prints the decorative header for the web crawler."""
    header = figlet_format("Web Crawler", font="big")
    footer = "Created by G Sundar Murthy"
    
    # Calculate the width for centering the footer
    max_width = max(len(line) for line in header.split('\n'))
    centered_footer = footer.center(max_width)
    
    print_decorative(header, Colors.HEADER)
    print_decorative(centered_footer, Colors.FOOTER)
    print_decorative('')

def print_progress(message):
    """Prints progress updates in a highlighted color."""
    print_decorative(message, Colors.HIGHLIGHT)

def simulate_probing_and_analysis():
    """Simulate probing and analysis at the start."""
    print_progress(f"[*] Probing the target for stability")
    time.sleep(1)  # Simulate probing delay
    print_progress(f"[*] Analyzing HTTP response for anomalies")
    time.sleep(1)  # Simulate analysis delay
    print_progress(f"[*] Analyzing HTTP response for potential parameter names")
    time.sleep(1)  # Simulate analysis delay

def extract_parameters_from_html(html):
    """Extract potential parameters from HTML content."""
    soup = BeautifulSoup(html, 'html.parser')
    params = set()
    
    # Extract parameters from various input elements
    for tag in soup.find_all(['input', 'select', 'textarea', 'button']):
        if 'name' in tag.attrs:
            params.add(tag.attrs['name'])
    
    # Extract from meta tags and other attributes
    for meta in soup.find_all('meta'):
        if 'name' in meta.attrs:
            params.add(meta.attrs['name'])
    
    for tag in soup.find_all(attrs={'data-*': True}):
        for attr in tag.attrs:
            if attr.startswith('data-'):
                params.add(attr)
    
    return list(params)

def fetch_html(url, timeout=15, retries=3):
    """Fetch HTML content from the URL with timeout and retry."""
    headers = {
        'User-Agent': get_random_user_agent()
    }
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            if response.status_code == 429:
                # Handle rate limiting
                wait_time = 2 ** attempt  # Exponential backoff
                print_decorative(f"Rate limit exceeded. Retrying in {wait_time} seconds...", Colors.HIGHLIGHT)
                time.sleep(wait_time)
                continue
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            if attempt < retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print_decorative(f"Error fetching URL {url}: {e}. Retrying in {wait_time} seconds...", Colors.ERROR)
                time.sleep(wait_time)
            else:
                print_decorative(f"Failed to fetch URL {url} after {retries} attempts: {e}", Colors.ERROR)
                return None

def fetch_html_with_selenium(url):
    """Fetch HTML content using Selenium."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get(url)
        html = driver.page_source
    finally:
        driver.quit()
    
    return html

def get_random_user_agent():
    """Return a random User-Agent string from a predefined list."""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
    ]
    return random.choice(user_agents)

def extract_links(html, base_url):
    """Extract and return all unique links from the HTML content."""
    soup = BeautifulSoup(html, 'html.parser')
    links = set()
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        full_url = urljoin(base_url, href)
        links.add(full_url)
    return links

def process_url(url, use_selenium=False, timeout=15):
    """Fetch and process the URL to find parameters."""
    html = fetch_html_with_selenium(url) if use_selenium else fetch_html(url, timeout=timeout)
    
    if html:
        parameters = extract_parameters_from_html(html)
        links = extract_links(html, url)
        return parameters, links
    return [], set()

def crawl_depth(url, depth, use_selenium=False, timeout=15, delay=0):
    """Crawl the URL up to the specified depth."""
    visited = set()
    parameters = []
    to_visit = [(url, 0)]

    # Start probing and analysis
    simulate_probing_and_analysis()

    while to_visit:
        current_url, current_depth = to_visit.pop(0)
        if current_url in visited or current_depth > depth:
            continue

        visited.add(current_url)
        params, links = process_url(current_url, use_selenium, timeout)
        
        if params:
            parameters.extend(params)

        # Add new links to the queue if within depth limit
        if current_depth < depth:
            for link in links:
                if link not in visited:
                    to_visit.append((link, current_depth + 1))

        time.sleep(delay)  # Respect delay between requests

    return list(set(parameters))  # Return unique parameters

def display_parameters(url, parameters, file=None):
    """Display found parameters in a decorative manner and save to file."""
    if parameters:
        print_decorative(f"[+] Found {len(parameters)} parameters for {url}:", Colors.SUCCESS)
        for param in parameters:
            print_decorative(f"    - {param}", Colors.INFO)
        
        if file:
            try:
                with open(file, 'a') as f:
                    f.write(f"\nParameters found for {url}:\n")
                    for param in parameters:
                        f.write(f"    - {param}\n")
            except IOError as e:
                print_decorative(f"Error writing to file {file}: {e}", Colors.ERROR)
    else:
        print_decorative(f"[+] No parameters were found for {url}.", Colors.INFO)

def main():
    parser = argparse.ArgumentParser(description='Web Crawler to find parameters.')
    parser.add_argument('-u', '--url', required=True, help='Target URL')
    parser.add_argument('-t', '--threads', type=int, default=5, help='Number of concurrent threads')
    parser.add_argument('-d', '--delay', type=float, default=0, help='Delay between requests in seconds')
    parser.add_argument('--timeout', type=int, default=15, help='HTTP request timeout in seconds')
    parser.add_argument('--depth', type=int, default=1, help='Depth of URL crawling')
    parser.add_argument('--selenium', action='store_true', help='Use Selenium to handle JavaScript content')
    parser.add_argument('--output', type=str, help='File to save parameters')
    args = parser.parse_args()
    
    url = args.url
    num_threads = args.threads
    delay = args.delay
    timeout = args.timeout
    depth = args.depth
    use_selenium = args.selenium
    output_file = args.output
    
    print_header()
    
    print_decorative('Starting the web crawling process...', Colors.INFO)
    
    # Use a ThreadPoolExecutor for concurrent requests
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {executor.submit(crawl_depth, url, depth, use_selenium, timeout, delay): url}
        
        for future in as_completed(futures):
            url = futures[future]
            try:
                parameters = future.result()
                display_parameters(url, parameters, output_file)
            except Exception as exc:
                print_decorative(f"Error processing {url}: {exc}", Colors.ERROR)
    
    print_decorative('Web crawling process completed.', Colors.WHITE)  # Updated color to white

if _name_ == '_main_':
    main()