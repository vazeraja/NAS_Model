import os
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import discord

from utilities import Utilities

class PDFDownloader:

    @staticmethod
    async def get_pdf_url(url: str):
        # Fetch the webpage content
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all links in the page
            links = soup.find_all('a', href=True)

            # Search for the link that points to the PDF
            for link in links:
                href = link['href']
                if href.endswith('.pdf'):
                    # Return the full PDF URL
                    if href.startswith('http'):
                        return href  # Direct URL
                    else:
                        return url + href  # Relative URL (adjust as needed)
        else:
            print(f"Error: Unable to fetch the webpage. Status code: {response.status_code}")
            return None