# Web Crawler Tool for Extracting URL Parameters

This tool is designed to crawl websites and extract all URL parameters, storing the results in a `.txt` file. It's suitable for web developers, cybersecurity enthusiasts, and researchers who need to analyze URL structures and parameter details efficiently.

## Features
- **Parameter Extraction**: Crawls the provided URL(s) and identifies all parameters used within the site.
- **File Storage**: Automatically saves the extracted parameters into a `.txt` file for easy access and review.
- **Command-Line and GUI Options**: The tool offers both a command-line interface (CLI) for quick use and a graphical user interface (GUI) for ease of interaction.
- **Platform**: Optimized for use in Kali Linux but can be adapted for other Linux distributions.

## Requirements
- **Operating System**: Kali Linux (or any compatible Linux distro)
- **Dependencies**: Ensure that Python and required libraries (such as `requests`, `beautifulsoup4`) are installed.

## Usage
- **CLI Mode**: Run the tool using the terminal by providing the URL as an argument.
- **GUI Mode**: A simple interface allows you to enter the URL and view results without using the terminal.

## Installation
Clone the repository and run the installation script to set up the dependencies:
```bash
git clone https://github.com/Sundxr2005/Web-Crawler.git
cd Web-Crawler
pip install -r requirements.txt

## Usage

### Command-Line Interface (CLI) Mode

To run the tool in CLI mode, use the following command:
```bash
python "web crawler.py" --url "http://example.com"

